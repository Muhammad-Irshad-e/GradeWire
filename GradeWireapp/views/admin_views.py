from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseNotAllowed
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.db import models
from ..models import Teacher, Student, Course, Subject
from .common import admin_required, get_course_instance


@admin_required
def admin_dashboard_view(request):
    return render(request, 'admin_dashboard.html')


@admin_required
def admin_home_view(request):
    total_students = Student.objects.count()
    total_teachers = Teacher.objects.count()
    total_courses = Course.objects.count()

    courses = Course.objects.all()

    course_student_counts = []
    for course in courses:
        student_count = Student.objects.filter(department=course).count()
        course_student_counts.append({
            'course_name': course.course_name,
            'student_count': student_count
        })

    chart_data = {
        'labels': ['Students', 'Teachers'],
        'datasets': [{
            'data': [total_students, total_teachers],
            'backgroundColor': ['#1e90ff', '#ff6347'],
        }]
    }

    course_chart_data = {
        'labels': [item['course_name'] for item in course_student_counts],
        'datasets': [{
            'label': 'Students in each course',
            'data': [item['student_count'] for item in course_student_counts],
            'backgroundColor': 'rgba(54, 162, 235, 0.5)',
            'borderColor': 'rgba(54, 162, 235, 1)',
            'borderWidth': 1,
        }]
    }

    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_courses': total_courses,
        'chart_data': chart_data,
        'course_chart_data': course_chart_data
    }

    return render(request, 'admin_home.html', context)


@admin_required
def approve_students(request):
    students = Student.objects.filter(is_approved=False)

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        try:
            student = Student.objects.get(id=student_id)
            student.is_approved = True
            student.save()
            messages.success(request, f"Student {student.name} approved.")
            return redirect('approve_students')
        except Student.DoesNotExist:
            return redirect('approve_students')

    context = {
        'students': students,
    }
    return render(request, 'approve_students.html', context)


@admin_required
def manage_course_view(request):
    courses = Course.objects.all()
    return render(request, 'admin_mg_course.html', {'courses': courses})


@admin_required
def admin_mg_course_view(request):
    courses = Course.objects.all()
    return render(request, 'admin_mg_course.html', {'courses': courses})


@admin_required
def add_course(request):
    if request.method == 'POST':
        course_name = request.POST.get('course_name')
        course_id = request.POST.get('course_id')
        duration = request.POST.get('duration')
        if course_name and course_id:
            new_course = Course(course_name=course_name, course_id=course_id, duration=duration)
            new_course.save()
            messages.success(request, f"Course {course_name} added successfully.")
            return redirect('adminMgCourse')
        else:
            messages.error(request, "Error: Course name or ID is missing.")
            return redirect('adminMgCourse')

    return redirect('adminMgCourse')


@admin_required
def edit_course(request, course_no):
    course = get_object_or_404(Course, id=course_no)
    
    if request.method == "POST":
        course.course_id = request.POST.get('courseId')
        course.course_name = request.POST.get('courseName')
        course.duration = request.POST.get('courseDuration')
        course.save()
        messages.success(request, "Course updated successfully!")
        return redirect('ManageCourse')
    
    return render(request, 'edit_course.html', {'course': course})


@admin_required
def delete_course(request, course_no):
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
    course = get_object_or_404(Course, id=course_no)
    try:
        course.delete()
        messages.success(request, f"Course '{course.course_name}' deleted successfully.")
    except models.ProtectedError:
        messages.error(request, f"Cannot delete course '{course.course_name}' because students, teachers, or subjects are assigned to it.")
    return redirect('ManageCourse')


@admin_required
def manage_subject_view(request):
    subjects = Subject.objects.all()
    courses = Course.objects.all()
    semester_choices = Subject.SEMESTER_CHOICES
    return render(request, 'admin_mg_subject.html', {'subjects': subjects, 'courses': courses, 'semester_choices': semester_choices})


@admin_required
def admin_mg_subject_view(request):
    return manage_subject_view(request)


@admin_required
def add_subject(request):
    courses = Course.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        subject_code = request.POST.get('subject_code')
        course_id = request.POST.get('course')
        semester = request.POST.get('semester')
        course = get_course_instance(course_id)
        if not course:
            messages.error(request, "Error: The selected course does not exist.")
            return redirect('adminMgSubject')

        if name and subject_code and course and semester:
            new_subject = Subject(name=name, subject_code=subject_code, course=course, semester=semester)
            new_subject.save()
            messages.success(request, f"Subject {name} added successfully.")
            return redirect('adminMgSubject')
        else:
            messages.error(request, "Error: Subject name, code, or course is missing.")
            return redirect('adminMgSubject')

    return render(request, 'admin_mg_subject.html', {
        'courses': courses,
        'subjects': Subject.objects.all(),
        'semester_choices': Subject.SEMESTER_CHOICES
    })


@admin_required
def edit_subject(request, subject_no):
    subject = get_object_or_404(Subject, id=subject_no)
    courses = Course.objects.all()
    semester_choices = Subject.SEMESTER_CHOICES
    
    if request.method == "POST":
        subject.semester = request.POST.get('Semester')
        subject.subject_code = request.POST.get('subjectCode')
        subject.name = request.POST.get('subjectName')
        course_name = request.POST.get('courseName')
        course_instance = get_course_instance(course_name)
        if not course_instance:
            messages.error(request, "Selected course does not exist.")
            return render(request, 'edit_subject.html', {
                'subject': subject,
                'courses': courses,
                'semester_choices': semester_choices
            })
        subject.course = course_instance

        subject.save()
        messages.success(request, f"Subject '{subject.name}' updated successfully!")
        return redirect('ManageSubject')
    
    return render(request, 'edit_subject.html', {
        'subject': subject,
        'courses': courses,
        'semester_choices': semester_choices
    })


@admin_required
def delete_subject(request, subject_no):
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
    subject = get_object_or_404(Subject, id=subject_no)
    try:
        subject.delete()
        messages.success(request, f"Subject '{subject.name}' deleted successfully.")
    except models.ProtectedError:
        messages.error(request, f"Cannot delete subject '{subject.name}' because attendance or marks records are associated with it.")
    return redirect('ManageSubject')


@admin_required
def manage_student_view(request):
    courses = Course.objects.all()
    students = Student.objects.all()
    return render(request, 'admin_mg_student.html', {'courses': courses, 'student': students})


@admin_required
def admin_mg_student_view(request):
    return manage_student_view(request)


@admin_required
def add_student(request):
    if request.method == "POST":
        name = request.POST.get('name')
        student_class = request.POST.get('Class')
        department_id = request.POST.get('department')
        register_id = request.POST.get('register_id')
        mobile = request.POST.get('mobile')
        email = request.POST.get('email')
        parent = request.POST.get('parent')
        parent_no = request.POST.get('parent_no')
        password = request.POST.get('password')
        
        if Student.objects.filter(register_id=register_id).exists():
            messages.error(request, "Register ID already exists. Please use a unique ID.")
            return redirect('ManageStudent')

        department = get_course_instance(department_id)
        if not department:
            messages.error(request, "Invalid department selected.")
            return redirect('ManageStudent')

        student = Student(
            name=name,
            Class=student_class,
            department=department,
            register_id=register_id,
            mobile=mobile,
            email=email,
            parent=parent,
            parent_no=parent_no,
            password=make_password(password) if password else "",
            is_approved=True,
        )
        student.save()
        messages.success(request, "Student added successfully!")
        return redirect('ManageStudent')

    courses = Course.objects.all()
    students = Student.objects.all()
    return render(request, 'admin_mg_student.html', {'courses': courses, 'student': students})


@admin_required
def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    courses = Course.objects.all()

    if request.method == "POST":
        name = request.POST.get('name')
        student_class = request.POST.get('Class')
        selected_course_id = request.POST.get('department')
        register_id = request.POST.get('register_id')
        mobile = request.POST.get('mobile')
        email = request.POST.get('email')
        parent = request.POST.get('parent')
        parent_no = request.POST.get('parent_no')

        if not name:
            messages.error(request, "Name is required.")
            return redirect('edit_student', student_id=student_id)
        course = get_course_instance(selected_course_id)
        if not course:
            messages.error(request, "Invalid department selected.")
            return redirect('edit_student', student_id=student_id)

        student.name = name
        student.Class = student_class
        student.department = course
        student.register_id = register_id
        student.mobile = mobile
        student.email = email
        student.parent = parent if parent else ""
        student.parent_no = parent_no if parent_no else ""
        student.save()
        messages.success(request, "Student updated successfully!")
        return redirect('ManageStudent')

    context = {
        'student': student,
        'courses': courses,
    }
    return render(request, 'edit_student.html', context)


@admin_required
def delete_student(request, student_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
    student = get_object_or_404(Student, id=student_id)
    try:
        student.delete()
        messages.success(request, f"Student '{student.name}' deleted successfully.")
    except models.ProtectedError:
        messages.error(request, f"Cannot delete student '{student.name}' because associated academic records exist.")
    return redirect('ManageStudent')


@admin_required
def manage_teacher_view(request):
    teachers = Teacher.objects.all()
    courses = Course.objects.all()
    return render(request, 'admin_mg_teacher.html', {'teacher': teachers, 'courses': courses})


@admin_required
def admin_mg_teacher_view(request):
    return manage_teacher_view(request)


@admin_required
def add_teacher(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        teacher_id = request.POST.get('teacher_id')
        mobile = request.POST.get('mobile')
        department_name = request.POST.get('department')
        password = request.POST.get('password')
        
        if Teacher.objects.filter(teacher_id=teacher_id).exists():
            messages.error(request, "Teacher ID already exists. Please use a unique ID.")
            return redirect('ManageTeacher')

        course = get_course_instance(department_name)
        if not course:
            messages.error(request, "Selected department does not exist.")
            return redirect('ManageTeacher')

        teacher = Teacher(
            name=name,
            email=email,
            teacher_id=teacher_id,
            mobile=mobile,
            department=course,
            password=make_password(password) if password else "",
        )
        teacher.save()
        messages.success(request, "Teacher added successfully!")
        return redirect('ManageTeacher')

    courses = Course.objects.all()
    return render(request, 'admin_mg_teacher.html', {'courses': courses})


@admin_required
def edit_teacher(request, teacher_no):
    teacher = get_object_or_404(Teacher, id=teacher_no)
    courses = Course.objects.all()

    if request.method == "POST":
        teacher.name = request.POST.get('teacherName')
        teacher.email = request.POST.get('teacherEmail')
        teacher.teacher_id = request.POST.get('teacherReg')
        teacher.mobile = request.POST.get('teacherMobile')
        new_password = request.POST.get('teacherPassword')
        if new_password and new_password != teacher.password:
            teacher.password = make_password(new_password)
        
        course_id = request.POST.get('teacherDepartment')
        course = get_course_instance(course_id)
        if not course:
            messages.error(request, "Selected department does not exist.")
            return redirect('edit_teacher', teacher_no=teacher_no)
        teacher.department = course
        
        teacher.save()
        messages.success(request, "Teacher updated successfully!")
        return redirect('ManageTeacher')
    
    return render(request, 'edit_teacher.html', {'teacher': teacher, 'courses': courses})


@admin_required
def delete_teacher(request, teacher_no):
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
    teacher = get_object_or_404(Teacher, id=teacher_no)
    try:
        teacher.delete()
        messages.success(request, f"Teacher '{teacher.name}' deleted successfully.")
    except models.ProtectedError:
        messages.error(request, f"Cannot delete teacher '{teacher.name}' because associated records exist.")
    return redirect('ManageTeacher')
