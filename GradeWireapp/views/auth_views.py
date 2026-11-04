from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.contrib import messages
from ..models import Teacher, Student
from ..forms import TeacherForm, StudentForm
from .common import verify_and_upgrade_password


def index(request):
    return render(request, 'index.html')


def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None and (user.is_staff or user.is_superuser):
            login(request, user)
            return redirect('adminDashboard')
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'admin_login.html', status=401)
    
    return render(request, 'admin_login.html')


def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('index')


def Teacher_signup_view(request):
    teacherForm = TeacherForm()
    if request.method == 'POST':
        teacherForm = TeacherForm(request.POST)
        if teacherForm.is_valid():
            teacher = teacherForm.save(commit=False)
            raw_password = teacherForm.cleaned_data.get('password')
            if raw_password:
                teacher.password = make_password(raw_password)
            teacher.save()
            messages.success(request, "Registration successful! Please log in.")
            return redirect('teacherLogin')
        else:
            messages.error(request, "Please correct the errors below.")
    return render(request, 'teach_register.html', {'teacherForm': teacherForm})


def teacherLogin(request):
    if request.method == 'POST':
        username = request.POST.get('teacher_id')
        password = request.POST.get('password')

        try:
            teacher = Teacher.objects.get(teacher_id=username)
            if verify_and_upgrade_password(password, teacher.password, teacher):
                request.session['teacher_id'] = teacher.id
                return redirect('teacherDashboard')
            else:
                messages.error(request, 'Invalid credentials.')
        except Teacher.DoesNotExist:
            messages.error(request, 'No teacher account found for this ID.')

    return render(request, 'teach_login.html')


def Student_signup_view(request):
    if request.method == 'POST':
        studentForm = StudentForm(request.POST, request.FILES)
        if studentForm.is_valid():
            student = studentForm.save(commit=False)
            raw_password = studentForm.cleaned_data.get('password')
            if raw_password:
                student.password = make_password(raw_password)
            student.save()
            messages.success(request, "Registration successful! Your account is pending admin approval.")
            return redirect('studentLogin')
        else:
            return render(request, 'stdnt_register.html', {'studentForm': studentForm})
    else:
        studentForm = StudentForm()

    return render(request, 'stdnt_register.html', {'studentForm': studentForm})


def studentLogin(request):
    if request.method == 'POST':
        username = request.POST.get('register_id')
        password = request.POST.get('password')

        try:
            student = Student.objects.get(register_id=username)

            if student.is_approved:
                if verify_and_upgrade_password(password, student.password, student):
                    request.session['register_id'] = student.id
                    return redirect('studentDashboard')
                else:
                    messages.error(request, 'Invalid credentials.')
            else:
                return redirect('waiting_for_approval')

        except Student.DoesNotExist:
            messages.error(request, 'No student account found for this ID.')

    return render(request, 'stdnt_login.html')
