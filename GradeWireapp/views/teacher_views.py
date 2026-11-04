import json
import logging
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from ..models import Teacher, Student, Course, Subject, Attendance, Marks
from ..forms import MarksForm
from .common import teacher_required, get_course_instance

logger = logging.getLogger(__name__)


@teacher_required
def teacher_dashboard_view(request):
    return render(request, 'teach_dashboard.html')


@teacher_required
def detail_student_view(request):
    students = Student.objects.all()
    return render(request, 'teach_st_details.html', {'student': students})


@teacher_required
def teacher_details_view(request):
    return detail_student_view(request)


@teacher_required
def teacher_home_view(request):
    total_first_year = Student.objects.filter(Class="1st Year").count()
    total_second_year = Student.objects.filter(Class="2nd Year").count()
    total_third_year = Student.objects.filter(Class="3rd Year").count()

    context = {
        'total_first_year': total_first_year,
        'total_second_year': total_second_year,
        'total_third_year': total_third_year,
    }
    return render(request, 'teach_home.html', context)


@teacher_required
def teacher_profile_view(request):
    t_id = request.session.get('teacher_id')
    if not t_id:
        return redirect('teacherLogin')
    
    try:
        teacher = Teacher.objects.get(id=t_id)
    except Teacher.DoesNotExist:
        return redirect('teacherLogin')
    
    courses = Course.objects.all()

    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            email = request.POST.get('email')
            mobile = request.POST.get('mobile')
            department_id = request.POST.get('department')

            if not mobile.isdigit() or len(mobile) != 10:
                messages.error(request, "Mobile number must be 10 digits")
                return render(request, 'teacher_profile.html', {'teacher': teacher, 'courses': courses})

            if Teacher.objects.exclude(id=t_id).filter(email=email).exists():
                messages.error(request, "Email is already in use by another teacher")
                return render(request, 'teacher_profile.html', {'teacher': teacher, 'courses': courses})
            try:
                department = Course.objects.get(id=department_id)
            except Course.DoesNotExist:
                messages.error(request, "Invalid department selected")
                return render(request, 'teacher_profile.html', {'teacher': teacher, 'courses': courses})

            teacher.name = name
            teacher.email = email
            teacher.mobile = mobile
            teacher.department = department
            teacher.save()
            
            messages.success(request, "Profile updated successfully")
            return redirect('teacherProfile')
            
        except Exception as e:
            messages.error(request, f"Error updating profile: {str(e)}")
            return render(request, 'teacher_profile.html', {'teacher': teacher, 'courses': courses})

    return render(request, 'teacher_profile.html', {'teacher': teacher, 'courses': courses})


@teacher_required
def teacher_attendance_view(request):
    years = Student.objects.values_list('Class', flat=True).distinct().order_by('Class')
    departments = Course.objects.values_list('course_name', flat=True).distinct().order_by('course_name')
    hours = range(1, 6)
    logger.debug(f"Loaded years: {list(years)}, departments: {list(departments)}")
    return render(request, 'teach_st_attendance.html', {
        'years': years,
        'departments': departments,
        'hours': hours,
    })


@teacher_required
def load_students_by_dept_year(request):
    department = request.GET.get('department')
    Class = request.GET.get('Class')
    logger.debug(f"load_students_by_dept_year: department={department}, Class={Class}")

    if department and Class:
        try:
            course = get_course_instance(department)
            if course:
                students = Student.objects.filter(
                    department=course,
                    Class=Class
                ).order_by('name')
            else:
                students = Student.objects.none()

            if not students.exists():
                logger.warning(f"No students found for department={department}, Class={Class}")
            
            student_list = [{'id': student.id, 'name': student.name, 'register_id': student.register_id} for student in students]
            logger.debug(f"Students found: {len(student_list)}")
            return JsonResponse({'students': student_list})
        except Exception as e:
            logger.error(f"Error in load_students_by_dept_year: {str(e)}")
            return JsonResponse({'error': f"Server error: {str(e)}"}, status=500)
    return JsonResponse({'students': []})


@teacher_required
def load_subjects_by_dept_class(request):
    department = request.GET.get('department')
    Class = request.GET.get('Class')
    
    logger.debug(f"Received: department={department}, Class={Class}")
    
    if not department or not Class:
        logger.debug("Missing department or Class, returning empty list")
        return JsonResponse({'subjects': []})

    Class = Class.strip()
    logger.debug(f"Normalized Class: {Class}")

    semester_mapping = {
        '1st Year': ['semester-1', 'semester-2'],
        '2nd Year': ['semester-3', 'semester-4'],
        '3rd Year': ['semester-5', 'semester-6'],
    }
    semesters = semester_mapping.get(Class, [])
    logger.debug(f"Semesters mapped for {Class}: {semesters}")

    if not semesters:
        available_classes = Student.objects.values_list('Class', flat=True).distinct()
        logger.warning(f"No semesters defined for Class: {Class}. Available classes: {list(available_classes)}")
        return JsonResponse({'subjects': [], 'message': f"No semesters mapped for {Class}"}, status=200)

    try:
        course = get_course_instance(department)
        if not course:
            logger.warning(f"No course found for identifier: {department}")
            return JsonResponse({'subjects': [], 'message': f"No course found for {department}"}, status=200)

        subjects = Subject.objects.filter(
            course=course,
            semester__in=semesters
        ).order_by('name')
        logger.debug(f"Subjects found: {list(subjects.values('name', 'semester'))}")

        if not subjects.exists():
            logger.warning(f"No subjects found for department={department}, semesters={semesters}")
            return JsonResponse({'subjects': [], 'message': "No subjects available for this selection"}, status=200)

        subject_list = [{'id': subject.id, 'name': subject.name} for subject in subjects]
        return JsonResponse({'subjects': subject_list})

    except Exception as e:
        logger.error(f"Unexpected error in load_subjects_by_dept_class: {str(e)}")
        return JsonResponse({'error': f"Server error: {str(e)}"}, status=500)


@teacher_required
def record_attendance(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            date_str = data.get('date')
            hour = data.get('hour')
            subject_id = data.get('subject')
            attendance_data = data.get('attendance_data')

            if not date_str or not hour or not subject_id:
                return JsonResponse({'error': 'Date, hour, and subject are required.'}, status=400)

            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            hour = int(hour)
            subject = Subject.objects.get(id=subject_id)

            for student_id, status in attendance_data.items():
                student = Student.objects.get(pk=student_id)
                is_present = (status == 'present')

                Attendance.objects.update_or_create(
                    student=student,
                    date=selected_date,
                    hour=hour,
                    subject=subject,
                    defaults={'is_present': is_present}
                )

                student.update_full_day_attendance(selected_date)

            return JsonResponse({'success': 'Attendance recorded successfully!'})

        except (json.JSONDecodeError, Student.DoesNotExist, Subject.DoesNotExist, ValueError) as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@teacher_required
def teacher_marks_view(request):
    semesters = [
        'semester-1', 'semester-2', 'semester-3',
        'semester-4', 'semester-5', 'semester-6'
    ]
    courses = Course.objects.values_list('course_name', flat=True).distinct().order_by('course_name')
    logger.debug(f"Loaded semesters: {semesters}, courses: {list(courses)}")
    return render(request, 'teach_st_marks.html', {
        'form': MarksForm(),
        'semesters': semesters,
        'courses': courses,
    })


@teacher_required
def load_subjects_by_course_semester(request):
    course_name = request.GET.get('course')
    semester = request.GET.get('semester')
    
    logger.debug(f"load_subjects_by_course_semester: course={course_name}, semester={semester}")
    
    if not course_name or not semester:
        return JsonResponse({'subjects': []})

    try:
        course = get_course_instance(course_name)
        if not course:
            logger.warning(f"No courses found for course: {course_name}")
            return JsonResponse({'subjects': [], 'message': f"No courses found for {course_name}"}, status=200)

        subjects = Subject.objects.filter(
            course=course,
            semester=semester
        ).order_by('name')

        if not subjects.exists():
            logger.warning(f"No subjects found for course={course_name}, semester={semester}")
            return JsonResponse({'subjects': [], 'message': "No subjects available for this selection"}, status=200)

        subject_list = [{'id': subject.id, 'name': subject.name} for subject in subjects]
        logger.debug(f"Returning subjects: {subject_list}")
        return JsonResponse({'subjects': subject_list})

    except Exception as e:
        logger.error(f"Unexpected error in load_subjects_by_course_semester: {str(e)}")
        return JsonResponse({'error': f"Server error: {str(e)}"}, status=500)


@teacher_required
def load_students_by_course_semester(request):
    course_name = request.GET.get('course')
    semester = request.GET.get('semester')
    logger.debug(f"load_students_by_course_semester: course={course_name}, semester={semester}")

    if course_name and semester:
        try:
            class_map = {
                'semester-1': '1st Year',
                'semester-2': '1st Year',
                'semester-3': '2nd Year',
                'semester-4': '2nd Year',
                'semester-5': '3rd Year',
                'semester-6': '3rd Year',
            }
            class_year = class_map.get(semester, None)
            if not class_year:
                logger.warning(f"No class year mapped for semester: {semester}")
                return JsonResponse({'students': [], 'message': f"No class year mapped for {semester}"}, status=200)

            course = get_course_instance(course_name)
            if not course:
                return JsonResponse({'students': [], 'message': f"No course found for {course_name}"}, status=200)

            students = Student.objects.filter(
                department=course,
                Class=class_year
            ).order_by('name')

            if not students.exists():
                logger.warning(f"No students found for course={course_name}, Class={class_year}")
            
            student_list = [{'id': student.id, 'name': student.name, 'register_id': student.register_id} for student in students]
            logger.debug(f"Returning students: {student_list}")
            return JsonResponse({'students': student_list})
        except Exception as e:
            logger.error(f"Error in load_students_by_course_semester: {str(e)}")
            return JsonResponse({'error': f"Server error: {str(e)}"}, status=500)
    return JsonResponse({'students': []})


@teacher_required
def record_marks(request):
    if request.method == 'POST':
        logger.debug(f"Received POST request: {request.body}")
        try:
            data = json.loads(request.body)
            course_name = data.get('course')
            semester = data.get('semester')
            exam_name = data.get('exam_name')
            subject_id = data.get('subject')
            marks_data = data.get('marks_data')

            logger.debug(f"Parsed data: course={course_name}, semester={semester}, exam_name={exam_name}, subject={subject_id}, marks_data={marks_data}")

            if not all([course_name, semester, exam_name, subject_id, marks_data]):
                logger.error("Missing required fields")
                return JsonResponse({'error': 'Course, semester, exam name, subject, and marks data are required.'}, status=400)

            course = get_course_instance(course_name)
            if not course:
                return JsonResponse({'error': f'Course "{course_name}" not found.'}, status=404)

            subject = Subject.objects.get(id=subject_id)
            logger.debug(f"Resolved course: {course}, subject: {subject}")

            for student_id, marks in marks_data.items():
                student = Student.objects.get(pk=student_id)
                internal_marks = int(marks.get('internal', 0))
                external_marks = int(marks.get('external', 0))
                logger.debug(f"Saving for student {student_id}: internal={internal_marks}, external={external_marks}")

                Marks.objects.update_or_create(
                    registerId=student,
                    semester=semester,
                    exam_name=exam_name,
                    subject=subject,
                    defaults={
                        'course': course,
                        'internalMarks': internal_marks,
                        'externalMarks': external_marks
                    }
                )

            logger.info("Marks recorded/updated successfully")
            return JsonResponse({'success': 'Marks saved successfully!'})

        except (json.JSONDecodeError, Course.DoesNotExist, Subject.DoesNotExist, Student.DoesNotExist, ValueError) as e:
            logger.error(f"Error in record_marks: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)
    logger.warning("Invalid request method")
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@teacher_required
def view_student_marks(request):
    courses = Course.objects.all()
    semester_choices = Subject.SEMESTER_CHOICES
    exam_choices = MarksForm().fields['exam_name'].choices
    
    selected_department = request.GET.get('department')
    selected_semester = request.GET.get('semester')
    selected_subject = request.GET.get('subject')
    selected_exam = request.GET.get('exam_name')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.GET.get('ajax'):
        department = request.GET.get('department')
        semester = request.GET.get('semester')
        subjects = Subject.objects.filter(course_id=department, semester=semester)
        subject_list = [{'id': s.id, 'name': s.name} for s in subjects]
        return JsonResponse(subject_list, safe=False)

    marks = None
    subjects = Subject.objects.none()
    
    if selected_department and selected_semester and selected_subject and selected_exam:
        marks = Marks.objects.filter(
            course_id=selected_department,
            semester=selected_semester,
            subject_id=selected_subject,
            exam_name=selected_exam
        )
        subjects = Subject.objects.filter(course_id=selected_department, semester=selected_semester)

    context = {
        'courses': courses,
        'semester_choices': semester_choices,
        'exam_choices': exam_choices,
        'subjects': subjects,
        'marks': marks,
        'selected_department': selected_department,
        'selected_semester': selected_semester,
        'selected_subject': selected_subject,
        'selected_exam': selected_exam,
    }
    
    return render(request, 'teach_view_st_marks.html', context)


@teacher_required
def teacher_stats_view(request):
    courses = Course.objects.all()
    semesters = Subject.SEMESTER_CHOICES
    return render(request, 'teach_st_stats.html', {'courses': courses, 'semesters': semesters})


@teacher_required
def filter_students(request):
    department_id = request.GET.get('department_id')
    if department_id:
        course = get_course_instance(department_id)
        if course:
            students = Student.objects.filter(department=course).values('id', 'name', 'Class')
            return JsonResponse({'students': list(students)}, safe=False)
    return JsonResponse({'students': []}, safe=False)


@teacher_required
def filter_subjects(request):
    department_id = request.GET.get('department_id')
    semester = request.GET.get('semester')
    if department_id and semester:
        course = get_course_instance(department_id)
        if course:
            subjects = Subject.objects.filter(course=course, semester=semester).values('id', 'name')
            return JsonResponse({'subjects': list(subjects)}, safe=False)
    return JsonResponse({'subjects': []}, safe=False)


@teacher_required
def view_student_attendance(request):
    departments = Course.objects.values_list('course_name', flat=True).distinct().order_by('course_name')
    semesters = Subject.SEMESTER_CHOICES
    return render(request, 'teach_view_st_attendance.html', {
        'departments': departments,
        'semesters': semesters,
    })


@teacher_required
def get_filtered_subjects(request):
    department = request.GET.get('department')
    semester = request.GET.get('semester')

    if not department or not semester:
        return JsonResponse({'subjects': []})

    course = get_course_instance(department)
    if not course:
        return JsonResponse({'subjects': []})

    subjects = Subject.objects.filter(course=course, semester=semester)
    subjects_data = [
        {'id': subject.id, 'name': subject.name, 'subject_code': subject.subject_code}
        for subject in subjects
    ]
    return JsonResponse({'subjects': subjects_data})


@teacher_required
def fetch_attendance_data(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method.'}, status=405)

    department = request.GET.get('department')
    semester = request.GET.get('semester')
    subject_id = request.GET.get('subject')

    if not all([department, semester, subject_id]):
        return JsonResponse({'error': 'All filters are required.'}, status=400)

    course = get_course_instance(department)
    if not course:
        return JsonResponse({'error': f'Department "{department}" not found.'}, status=404)

    try:
        semester_map = {
            'semester-1': '1st Year',
            'semester-2': '1st Year',
            'semester-3': '2nd Year',
            'semester-4': '2nd Year',
            'semester-5': '3rd Year',
            'semester-6': '3rd Year',
        }
        class_value = semester_map.get(semester, semester)

        students = Student.objects.filter(department=course, Class=class_value)

        total_attendance_marked = Attendance.objects.filter(
            subject_id=subject_id
        ).values('date', 'hour').distinct().count()

        attendance_data = []
        for student in students:
            total_hours_present = Attendance.objects.filter(
                student=student,
                subject_id=subject_id,
                is_present=True
            ).values('date', 'hour').distinct().count()

            total_hours_marked_all = Attendance.objects.filter(
                student=student,
                subject_id=subject_id
            ).values('date', 'hour').distinct().count()

            attendance_percentage = (total_hours_present / total_hours_marked_all * 100) if total_hours_marked_all > 0 else 0

            if total_hours_marked_all > 0:
                student_attendance = {
                    'student_name': student.name,
                    'class': student.Class,
                    'total_hours_present': total_hours_present,
                    'attendance_percentage': round(attendance_percentage, 2),
                }
                attendance_data.append(student_attendance)

        return JsonResponse({
            'attendance_data': attendance_data,
            'total_attendance_marked': total_attendance_marked
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
