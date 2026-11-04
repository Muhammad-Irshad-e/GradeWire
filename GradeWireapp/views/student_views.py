from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from ..models import Student, Attendance, Marks
from .common import student_required, get_course_instance


@student_required
def student_dashboard_view(request):
    return render(request, 'stdnt_dashboard.html')


@student_required
def student_home_view(request):
    return render(request, 'stdnt_home.html')


@student_required
def student_profile_view(request):
    student_id = request.session.get('register_id')
    if not student_id:
        return redirect('studentLogin')
    
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return redirect('studentLogin')

    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            class_name = request.POST.get('class')
            mobile = request.POST.get('mobile')
            email = request.POST.get('email')
            parent = request.POST.get('parent')
            parent_no = request.POST.get('parent_no')

            if not mobile.isdigit() or len(mobile) != 10:
                messages.error(request, "Mobile number must be 10 digits")
                return render(request, 'student_profile.html', {'student': student})

            if not parent_no.isdigit() or len(parent_no) != 10:
                messages.error(request, "Parent mobile number must be 10 digits")
                return render(request, 'student_profile.html', {'student': student})

            if Student.objects.exclude(id=student_id).filter(email=email).exists():
                messages.error(request, "Email is already in use by another student")
                return render(request, 'student_profile.html', {'student': student})

            student.name = name
            student.Class = class_name
            student.mobile = mobile
            student.email = email
            student.parent = parent
            student.parent_no = parent_no
            student.save()
            
            messages.success(request, "Profile updated successfully")
            return redirect('studentProfile')
            
        except Exception as e:
            messages.error(request, f"Error updating profile: {str(e)}")
            return render(request, 'student_profile.html', {'student': student})

    return render(request, 'student_profile.html', {'student': student})


@student_required
def student_attendance_view(request):
    student_id = request.session.get('register_id')
    if not student_id:
        messages.error(request, "You must be logged in to view attendance.")
        return redirect('studentLogin')

    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        messages.error(request, "Student record not found. Please contact support.")
        return redirect('studentLogin')

    student_attendance = Attendance.objects.filter(student=student)
    full_day_count = student.full_day_attendance

    all_dates = student_attendance.values('date').distinct()
    absent_dates = []
    for date_record in all_dates:
        date = date_record['date']
        hours_present = student_attendance.filter(date=date, is_present=True).values('hour').distinct().count()
        if hours_present < 5:
            absent_dates.append(date)

    absent_count = len(absent_dates)

    return render(request, 'stdnt_attendance.html', {
        'present_count': full_day_count,
        'absent_count': absent_count,
        'absent_dates': absent_dates,
    })


@student_required
def student_grades_view(request):
    student_id = request.session.get('register_id')
    all_grades = Marks.objects.filter(registerId__id=student_id)
    
    semesters = all_grades.values_list('semester', flat=True).distinct()
    exam_names = all_grades.values_list('exam_name', flat=True).distinct()

    filtered_grades = []
    selected_semester = None
    selected_exam_name = None

    if request.method == 'POST':
        selected_semester = request.POST.get('semester')
        selected_exam_name = request.POST.get('exam_name')
        
        filtered_grades = all_grades
        if selected_semester:
            filtered_grades = filtered_grades.filter(semester=selected_semester)
        if selected_exam_name:
            filtered_grades = filtered_grades.filter(exam_name=selected_exam_name)

        filtered_grades = list(filtered_grades)
        for grade in filtered_grades:
            grade.total_marks = grade.externalMarks + grade.internalMarks

    return render(request, 'stdnt_grades.html', {
        'grades': filtered_grades,
        'semesters': semesters,
        'exam_names': exam_names,
        'selected_semester': selected_semester,
        'selected_exam_name': selected_exam_name,
        'show_results': request.method == 'POST',
    })


def student_status(request):
    student_id = request.GET.get('student_id')
    subject_id = request.GET.get('subject_id')
    department_id = request.GET.get('department_id')
    semester = request.GET.get('semester')

    if not all([student_id, subject_id, department_id, semester]):
        return JsonResponse({'error': 'Missing parameters'}, status=400)

    course = get_course_instance(department_id)
    if not course:
        return JsonResponse({'error': 'Course not found'}, status=404)

    marks = Marks.objects.filter(
        registerId_id=student_id,
        subject_id=subject_id,
        course=course,
        semester=semester
    )

    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)

    data = {
        'student_name': student.name,
        'marks': [
            {
                'exam_name': mark.exam_name,
                'internalMarks': mark.internalMarks,
                'externalMarks': mark.externalMarks,
                'totalMarks': mark.internalMarks + mark.externalMarks
            } for mark in marks
        ]
    }
    return JsonResponse(data, safe=False)
