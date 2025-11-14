from django.contrib.auth import authenticate, login
from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect
from . import forms,models
from .models import Teacher,Student,Course
from django.contrib.auth.decorators import login_required
from .forms import TeacherForm
from django.contrib import messages
from django.contrib.auth.models import Group
# Create your views here.
def index(request):
    return render(request,'index.html')
def student_dashboard_view(request):
    return render(request,'stdnt_dashboard.html')


# Hardcoded username and password
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponse

ADMIN_USERNAME = "group1"
ADMIN_PASSWORD = "4321"

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = User.objects.filter(username=username).first()
        
        if user:
            authenticated_user = authenticate(request, username=username, password=password)
            if authenticated_user is not None:
                login(request, authenticated_user)
                return redirect('adminDashboard')
            else:
                return HttpResponse("Invalid credentials, please try again.", status=401)
        else:
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                user = User.objects.create_user(username=username, password=password)
                login(request, user)
                return redirect('adminDashboard')
            else:
                return HttpResponse("Invalid credentials, please try again.", status=401)
    
    return render(request, 'admin_login.html')


from django.shortcuts import render, redirect
from .models import Student
from django.contrib.auth.decorators import login_required

def approve_students(request):

    # Get all students who are not approved
    students = Student.objects.filter(is_approved=False)

    # Handle approval
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        try:
            student = Student.objects.get(id=student_id)
            student.is_approved = True
            student.save()
            return redirect('approve_students')  # Refresh the page
        except Student.DoesNotExist:
            return redirect('approve_students')  # Redirect if student does not exist

    context = {
        'students': students,
    }
    return render(request, 'approve_students.html', context)

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import Group
from . import forms

def Teacher_signup_view(request):
    teacherForm = forms.TeacherForm()
    if request.method == 'POST':
        teacherForm = forms.TeacherForm(request.POST)
        if teacherForm.is_valid():
            teacher = teacherForm.save()
            my_teacher_group, _ = Group.objects.get_or_create(name='TEACHER')
            teacher.groups.add(my_teacher_group)
            messages.success(request, "Registration successful! Please log in.")
            return redirect('teacherLogin')
        else:
            messages.error(request, "Please correct the errors below.")
    return render(request, 'teach_register.html', {'teacherForm': teacherForm})
def is_teacher(user):
    return user.group.filter(name='TEACHER').exists()

from django.contrib import messages

from .models import Student
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Teacher  
from django.contrib.auth.hashers import check_password

def teacherLogin(request):
    if request.method == 'POST':
        username = request.POST['teacher_id']
        password = request.POST['password']

        try:
            teacher = Teacher.objects.get(teacher_id=username)
            
            if teacher.password ==password:  # Verify password securely
                request.session['teacher_id'] = teacher.id  # Store teacher ID in session
                return redirect('teacherDashboard')
            else:
                messages.error(request, 'Invalid credentials.')
        except Teacher.DoesNotExist:
            messages.error(request, 'No teacher account found for this ID.')

    return render(request, 'teach_login.html')


# @login_required
def teacher_dashboard_view(request):
    return render(request,'teach_dashboard.html')
    



from .forms import StudentForm
def Student_signup_view(request):
    if request.method == 'POST':
        # Create the form instance with POST data and file data (if any)
        studentForm = forms.StudentForm(request.POST, request.FILES)
        
        if studentForm.is_valid():
            studentForm.save()
            return redirect('studentLogin')  # Make sure 'studentlogin' is a valid URL name in your urls.py
        else:
            return render(request, 'stdnt_register.html', {'studentForm': studentForm})

    else:
        studentForm = StudentForm()

    return render(request, 'stdnt_register.html', {'studentForm': studentForm})


def is_student(user):
    return user.group.filter(name='STUDENT').exists()


from django.shortcuts import render, redirect
from django.contrib import messages

from .models import Student  # Import the Student model
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Student

def studentLogin(request):
    if request.method == 'POST':
        username = request.POST.get('register_id')
        password = request.POST.get('password')

        try:
            student = Student.objects.get(register_id=username)

            # Check if the student is approved
            if student.is_approved:
                # Authenticate the student using the stored password
                if student.password == password:  
                    request.session['register_id'] = student.id  
                    return redirect('studentDashboard')  # Redirect to student dashboard once approved
                else:
                    messages.error(request, 'Invalid credentials.')
            else:
                # Redirect to waiting for approval page if the account is not approved
                return redirect('waiting_for_approval')

        except Student.DoesNotExist:
            messages.error(request, 'No student account found for this ID.')

    return render(request, 'stdnt_login.html')


# @login_required
def student_dashboard_view(request):
    return render(request,'stdnt_dashboard.html')



def detail_student_view(request):
    students = models.Student.objects.all()
    return render(request, 'teach_st_details.html',{'student':students})



def manage_course_view(request):
    courses = models.Course.objects.all()  # Get all courses from the database
    return render(request,'admin_mg_course.html', {'courses': courses})

def manage_subject_view(request):
    subjects = models.Subject.objects.all()
    courses = models.Course.objects.all()  # Get all courses from the database
    semester_choices = Subject.SEMESTER_CHOICES
      # Get all courses from the database
    return render(request,'admin_mg_subject.html', {'subjects': subjects ,'courses': courses ,'semester_choices': semester_choices})


def afterlogin_view(request):
    if is_teacher(request.user):
        accountapproval=models.Teacher.objects.all().filter(user_id=request.user.id,status=True)
        if accountapproval:
            return redirect('admin-dashboard')
    elif is_student(request.user):
        return redirect('student-home')
    else:
        return redirect('teacher-home')

@login_required
def admin_dashboard_view(request):
    return render(request,'admin_dashboard.html')

from django.shortcuts import render, redirect
from .models import Teacher,Course
from django.contrib import messages

def teacher_profile_view(request):
    t_id = request.session.get('teacher_id')
    if not t_id:
        return redirect('login')  # Redirect to login if no session
    
    try:
        teacher = Teacher.objects.get(id=t_id)
    except Teacher.DoesNotExist:
        return redirect('login')  # Redirect if teacher not found
    
    courses = Course.objects.all()

    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')
            email = request.POST.get('email')
            mobile = request.POST.get('mobile')
            department_id = request.POST.get('department')

            # Validate mobile number
            if not mobile.isdigit() or len(mobile) != 10:
                messages.error(request, "Mobile number must be 10 digits")
                return render(request, 'teacher_profile.html', {'teacher': teacher, 'courses': courses})

            # Check if email is already taken by another teacher
            if Teacher.objects.exclude(id=t_id).filter(email=email).exists():
                messages.error(request, "Email is already in use by another teacher")
                return render(request, 'teacher_profile.html', {'teacher': teacher, 'courses': courses})
            try:
                department = Course.objects.get(id=department_id)
            except Course.DoesNotExist:
                messages.error(request, "Invalid department selected")
                return render(request, 'teacher_profile.html', {'teacher': teacher, 'courses': courses})
            # Update teacher object
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

# app/views.py
# attendance/views.py
# attendance/views.py
# attendance/views.py
# attendance/views.py
import json
import logging
from django.shortcuts import render
from django.http import JsonResponse
from .models import Student, Attendance, Course, Subject
from datetime import datetime

logger = logging.getLogger(__name__)

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

def load_students_by_dept_year(request):
    department = request.GET.get('department')  # This is the course_name from Course model
    Class = request.GET.get('Class')  # This is the year (e.g., "1st Year", "2nd Year")
    logger.debug(f"load_students_by_dept_year: department={department}, Class={Class}")

    if department and Class:
        try:
            # Filter students by department (course_name) and Class
            students = Student.objects.filter(
                department__course_name=department,  # Access course_name via ForeignKey
                Class=Class
            ).order_by('name')

            if not students.exists():
                logger.warning(f"No students found for department={department}, Class={Class}")
                available_depts = Student.objects.values_list('department__course_name', flat=True).distinct()
                logger.debug(f"Available student departments: {list(available_depts)}")
            
            student_list = [{'id': student.id, 'name': student.name, 'register_id': student.register_id} for student in students]
            logger.debug(f"Students found: {len(student_list)}")
            return JsonResponse({'students': student_list})
        except Exception as e:
            logger.error(f"Error in load_students_by_dept_year: {str(e)}")
            return JsonResponse({'error': f"Server error: {str(e)}"}, status=500)
    return JsonResponse({'students': []})

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
        courses = Course.objects.filter(course_name__iexact=department)
        if not courses.exists():
            logger.warning(f"No courses found for course_name/department: {department}")
            return JsonResponse({'subjects': [], 'message': f"No courses found for {department}"}, status=200)
        logger.debug(f"Courses found: {list(courses.values('course_name'))}")

        subjects = Subject.objects.filter(
            course__in=courses,
            semester__in=semesters
        ).order_by('name')
        logger.debug(f"Subjects found: {list(subjects.values('name', 'semester', 'course__course_name'))}")

        if not subjects.exists():
            logger.warning(f"No subjects found for department={department}, semesters={semesters}")
            return JsonResponse({'subjects': [], 'message': "No subjects available for this selection"}, status=200)

        subject_list = [{'id': subject.id, 'name': subject.name} for subject in subjects]
        return JsonResponse({'subjects': subject_list})

    except Exception as e:
        logger.error(f"Unexpected error in load_subjects_by_dept_class: {str(e)}")
        return JsonResponse({'error': f"Server error: {str(e)}"}, status=500)

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
                is_present = status == 'present'

                existing_attendance = Attendance.objects.filter(
                    student=student,
                    date=selected_date,
                    hour=hour,
                    subject=subject
                ).first()

                if existing_attendance:
                    return JsonResponse({
                        'warning': f'Attendance for Students on {selected_date} at hour {hour} for {subject.name} already recorded.'
                    }, status=200)

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




import json
import logging
from django.shortcuts import render
from django.http import JsonResponse
from .models import Student, Course, Subject, Marks
from .forms import MarksForm

logger = logging.getLogger(__name__)

def teacher_marks_view(request):
    """Render the marks recording page with initial data."""
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

def load_subjects_by_course_semester(request):
    """Load subjects based on course and semester."""
    course_name = request.GET.get('course')
    semester = request.GET.get('semester')
    
    logger.debug(f"load_subjects_by_course_semester: course={course_name}, semester={semester}")
    
    if not course_name or not semester:
        return JsonResponse({'subjects': []})

    try:
        courses = Course.objects.filter(course_name__iexact=course_name)
        if not courses.exists():
            logger.warning(f"No courses found for course_name: {course_name}")
            return JsonResponse({'subjects': [], 'message': f"No courses found for {course_name}"}, status=200)

        subjects = Subject.objects.filter(
            course__in=courses,
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

def load_students_by_course_semester(request):
    """Load students based on course and semester."""
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

            students = Student.objects.filter(
                department__course_name=course_name,
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

def record_marks(request):
    """Record marks for students, preventing duplicates."""
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

            course = Course.objects.get(course_name__iexact=course_name)
            subject = Subject.objects.get(id=subject_id)
            logger.debug(f"Resolved course: {course}, subject: {subject}")

            # Check for existing marks for any student in this batch
            for student_id in marks_data.keys():
                student = Student.objects.get(pk=student_id)
                existing_marks = Marks.objects.filter(
                    registerId=student,
                    semester=semester,
                    exam_name=exam_name,
                    course=course,
                    subject=subject
                ).exists()
                if existing_marks:
                    logger.warning(f"Marks already recorded for {student.name}")
                    return JsonResponse({
                        'warning': f'Marks for {exam_name} in {subject.name} ({semester}, {course_name}) already recorded for some students.'
                    }, status=200)

            # If no duplicates, proceed to save marks
            for student_id, marks in marks_data.items():
                student = Student.objects.get(pk=student_id)
                internal_marks = int(marks.get('internal', 0))
                external_marks = int(marks.get('external', 0))
                logger.debug(f"Saving for student {student_id}: internal={internal_marks}, external={external_marks}")

                Marks.objects.update_or_create(
                    registerId=student,
                    semester=semester,
                    exam_name=exam_name,
                    course=course,
                    subject=subject,
                    defaults={
                        'internalMarks': internal_marks,
                        'externalMarks': external_marks
                    }
                )

            logger.info("Marks recorded successfully")
            return JsonResponse({'success': 'Marks recorded successfully!'})

        except (json.JSONDecodeError, Course.DoesNotExist, Subject.DoesNotExist, Student.DoesNotExist, ValueError) as e:
            logger.error(f"Error in record_marks: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)
    logger.warning("Invalid request method")
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


from django.shortcuts import render
from .models import Course, Subject, Marks
from .forms import MarksForm

def view_student_marks(request):
    courses = Course.objects.all()
    semester_choices = Subject.SEMESTER_CHOICES
    exam_choices = MarksForm().fields['exam_name'].choices
    
    selected_department = request.GET.get('department')
    selected_semester = request.GET.get('semester')
    selected_subject = request.GET.get('subject')
    selected_exam = request.GET.get('exam_name')
    
    # Handle AJAX request for subjects
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.GET.get('ajax'):
        department = request.GET.get('department')
        semester = request.GET.get('semester')
        subjects = Subject.objects.filter(course_id=department, semester=semester)
        subject_list = [{'id': s.id, 'name': s.name} for s in subjects]
        return JsonResponse(subject_list, safe=False)

    marks = None
    subjects = Subject.objects.none()
    
    # If all filters are selected, fetch the marks
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


import json
from django.shortcuts import render
from django.http import JsonResponse
from .models import Course, Subject, Student, Marks

def teacher_stats_view(request):
    courses = Course.objects.all()
    semesters = Subject.SEMESTER_CHOICES
    return render(request, 'teach_st_stats.html', {'courses': courses, 'semesters': semesters})

def filter_students(request):
    department_id = request.GET.get('department_id')
    if department_id:
        students = Student.objects.filter(department_id=department_id).values('id', 'name','Class')
        return JsonResponse({'students': list(students)}, safe=False)
    return JsonResponse({'students': []}, safe=False)

def filter_subjects(request):
    department_id = request.GET.get('department_id')
    semester = request.GET.get('semester')
    if department_id and semester:
        subjects = Subject.objects.filter(course_id=department_id, semester=semester).values('id', 'name')
        return JsonResponse({'subjects': list(subjects)}, safe=False)
    return JsonResponse({'subjects': []}, safe=False)

def student_status(request):
    student_id = request.GET.get('student_id')
    subject_id = request.GET.get('subject_id')
    department_id = request.GET.get('department_id')
    semester = request.GET.get('semester')

    if not all([student_id, subject_id, department_id, semester]):
        return JsonResponse({'error': 'Missing parameters'}, status=400)

    marks = Marks.objects.filter(
        registerId_id=student_id,
        subject_id=subject_id,
        course_id=department_id,
        semester=semester
    )

    student = Student.objects.get(id=student_id)
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

from django.shortcuts import render
from django.http import JsonResponse
from .models import Course, Subject, Student, Attendance

def view_student_attendance(request):
    departments = Course.objects.values_list('course_name', flat=True).distinct().order_by('course_name')
    semesters = Subject.SEMESTER_CHOICES
    return render(request, 'teach_view_st_attendance.html', {
        'departments': departments,
        'semesters': semesters,
    })

def get_filtered_subjects(request):
    department = request.GET.get('department')
    semester = request.GET.get('semester')

    if not department or not semester:
        return JsonResponse({'subjects': []})

    try:
        course = Course.objects.get(course_name=department)
        subjects = Subject.objects.filter(course=course, semester=semester)
        subjects_data = [
            {'id': subject.id, 'name': subject.name, 'subject_code': subject.subject_code}
            for subject in subjects
        ]
        print(f"Subjects for {department}, {semester}: {[(s['id'], s['name']) for s in subjects_data]}")
        return JsonResponse({'subjects': subjects_data})
    except Course.DoesNotExist:
        return JsonResponse({'subjects': []})

def fetch_attendance_data(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method.'}, status=405)

    department = request.GET.get('department')
    semester = request.GET.get('semester')
    subject_id = request.GET.get('subject')

    if not all([department, semester, subject_id]):
        return JsonResponse({'error': 'All filters are required.'}, status=400)

    print(f"Filters - Department: {department}, Semester: {semester}, Subject ID: {subject_id}")

    try:
        course = Course.objects.get(course_name=department)

        # Map frontend semester to Student.Class (year-based)
        semester_map = {
            'semester-1': '1st Year',
            'semester-2': '1st Year',
            'semester-3': '2nd Year',
            'semester-4': '2nd Year',
            'semester-5': '3rd Year',
            'semester-6': '3rd Year',
        }
        class_value = semester_map.get(semester, semester)
        print(f"Semester mapped to Class: {class_value}")

        # Get students matching the filters
        students = Student.objects.filter(department=course, Class=class_value)
        print(f"Students found: {students.count()}")
        for student in students:
            print(f"Student: {student.name}, Class: {student.Class}")

        # Calculate total distinct sessions marked for the subject (date + hour)
        total_attendance_marked = Attendance.objects.filter(
            subject_id=subject_id
        ).values('date', 'hour').distinct().count()  # Count unique date-hour sessions
        print(f"Total Sessions Marked for Subject {subject_id}: {total_attendance_marked}")

        attendance_data = []
        for student in students:
            # Total hours present for this student and subject (distinct date-hour sessions)
            total_hours_present = Attendance.objects.filter(
                student=student,
                subject_id=subject_id,
                is_present=True
            ).values('date', 'hour').distinct().count()

            # Total hours marked for this student (distinct date-hour sessions)
            total_hours_marked_all = Attendance.objects.filter(
                student=student,
                subject_id=subject_id
            ).values('date', 'hour').distinct().count()

            # Calculate percentage
            attendance_percentage = (total_hours_present / total_hours_marked_all * 100) if total_hours_marked_all > 0 else 0

            # Only include students with attendance records
            if total_hours_marked_all > 0:
                student_attendance = {
                    'student_name': student.name,
                    'class': student.Class,
                    'total_hours_present': total_hours_present,
                    'attendance_percentage': round(attendance_percentage, 2),
                }
                attendance_data.append(student_attendance)
                print(f"Added {student.name} - Present: {total_hours_present}, Total: {total_hours_marked_all}, Percentage: {attendance_percentage}")

        print(f"Attendance data length: {len(attendance_data)}")
        return JsonResponse({
            'attendance_data': attendance_data,
            'total_attendance_marked': total_attendance_marked
        })
    except Course.DoesNotExist:
        return JsonResponse({'error': f'Department "{department}" not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



def teacher_details_view(request):
    return render(request,'teach_st_details.html')

def teacher_home_view(request):
    total_first_year = Student.objects.filter (Class="1st Year").count()
    total_second_year = Student.objects.filter(Class="2nd Year").count()
    total_third_year = Student.objects.filter(Class="3rd Year").count()

    # Context to pass to the template
    context = {
        'total_first_year': total_first_year,
        'total_second_year': total_second_year,
        'total_third_year': total_third_year,
    }

    
    return render(request,'teach_home.html',context)
from django.shortcuts import render
from .models import Student, Teacher, Course

from django.db.models import Count

from django.db.models import Count, F

from django.db.models import Count, F
from django.shortcuts import render
from .models import Student, Teacher, Course

from django.db.models import Count, F
from django.shortcuts import render
from .models import Student, Teacher, Course

def admin_home_view(request):
    # Aggregate total counts
    total_students = Student.objects.count()
    total_teachers = Teacher.objects.count()
    total_courses = Course.objects.count()

    # Fetch courses and count the students in each course by matching department (ForeignKey)
    courses = Course.objects.all()

    course_student_counts = []
    for course in courses:
        # Count students whose department matches the Course object
        student_count = Student.objects.filter(department=course).count()  # Use course object
        course_student_counts.append({
            'course_name': course.course_name,
            'student_count': student_count
        })

    # Prepare data for the donut chart (Student-Teacher Ratio)
    chart_data = {
        'labels': ['Students', 'Teachers'],
        'datasets': [{
            'data': [total_students, total_teachers],
            'backgroundColor': ['#1e90ff', '#ff6347'],
        }]
    }

    # Prepare data for the bar chart (Students per course)
    course_chart_data = {
        'labels': [item['course_name'] for item in course_student_counts],  # Course names
        'datasets': [{
            'label': 'Students in each course',
            'data': [item['student_count'] for item in course_student_counts],
            'backgroundColor': 'rgba(54, 162, 235, 0.5)',
            'borderColor': 'rgba(54, 162, 235, 1)',
            'borderWidth': 1,
        }]
    }

    # Pass the data to the template
    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_courses': total_courses,
        'chart_data': chart_data,  # Donut chart data
        'course_chart_data': course_chart_data  # Bar chart data
    }

    return render(request, 'admin_home.html', context)





def admin_mg_teacher_view(request):
    return render(request,'admin_mg_teacher.html')

def admin_mg_student_view(request):
    return render(request,'admin_mg_student.html')

def admin_mg_course_view(request):
    courses = Course.objects.all()  # Get all courses from the database
    return render(request,'admin_mg_course.html', {'courses': courses})

def add_course(request):
    if request.method == 'POST':
        course_name = request.POST.get('course_name')
        course_id = request.POST.get('course_id')
        duration = request.POST.get('duration')
        if course_name and course_id:
            # Create a new Course object and save it to the database
            new_course = Course(course_name=course_name, course_id=course_id, duration=duration)
            new_course.save()

            return redirect('adminMgCourse')  # Redirect to the manage courses page
        else:
            return HttpResponse("Error: Course name or ID is missing.")

    return redirect('adminMgCourse') 

from .models import Subject

def admin_mg_subject_view(request):
    courses=Course.objects.all()
    subjects=Subject.objects.all()
    return render(request,'admin_mg_subject.html',{'courses':courses ,'subjects':subjects})


def add_subject(request):
    # Fetch all courses for the dropdown
    courses = Course.objects.all()

    if request.method == 'POST':
        # Get the data from the form submission
        name = request.POST.get('name')
        subject_code = request.POST.get('subject_code')
        course_id = request.POST.get('course')  # Get the selected course ID
        semester = request.POST.get('semester')
        # Retrieve the selected course object using the course_id
        try:
            course = Course.objects.get(course_id=course_id)  # Use course_id instead of id
        except Course.DoesNotExist:
            return HttpResponse("Error: The selected course does not exist.")

        # Validate that the necessary data exists
        if name and subject_code and course and semester:
            # Create and save the new subject associated with the selected course
            new_subject = Subject(name=name, subject_code=subject_code, course=course,semester = semester)
            new_subject.save()

            return redirect('adminMgSubject')  # Redirect to the manage subject page
        else:
            return HttpResponse("Error: Subject name, code, or course is missing.")

    # If the request is GET, pass the list of courses to the template
    return render(request, 'admin_mg_subject.html', {'courses': courses})

def student_profile_view(request):
    student_id=request.session.get('register_id')
    student=Student.objects.get(id=student_id)
    return render(request,'student_profile.html',{'student':student})
 
from django.shortcuts import render
from .models import Marks

def student_grades_view(request):
    student_id = request.session.get('register_id')
    
    # Fetch all grades for the student
    all_grades = Marks.objects.filter(registerId__id=student_id)
    
    # Get distinct semesters and exam names
    semesters = all_grades.values_list('semester', flat=True).distinct()
    exam_names = all_grades.values_list('exam_name', flat=True).distinct()

    # Initialize variables
    filtered_grades = []
    selected_semester = None
    selected_exam_name = None

    # Handle form submission
    if request.method == 'POST':
        selected_semester = request.POST.get('semester')
        selected_exam_name = request.POST.get('exam_name')
        
        # Filter grades based on selections
        filtered_grades = all_grades
        if selected_semester:
            filtered_grades = filtered_grades.filter(semester=selected_semester)
        if selected_exam_name:
            filtered_grades = filtered_grades.filter(exam_name=selected_exam_name)

        # Convert queryset to list and compute total_marks
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

def student_home_view(request):
    return render(request,'stdnt_home.html')


from django.shortcuts import render
from .models import Attendance

from django.shortcuts import render, redirect
from .models import Attendance, Student
from django.db.models import Count
from django.contrib import messages

def student_attendance_view(request):
    student_id = request.session.get('register_id')
    
    # Check if student_id exists in session
    if not student_id:
        messages.error(request, "You must be logged in to view attendance.")
        return redirect('login')  # Replace 'login' with your login URL name

    try:
        # Get the student object
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        messages.error(request, "Student record not found. Please contact support.")
        return redirect('login')  # Or another appropriate page

    student_attendance = Attendance.objects.filter(student=student)

    # Full-day attendance count from the Student model
    full_day_count = student.full_day_attendance

    # Get all distinct dates the student has attendance records for
    all_dates = student_attendance.values('date').distinct()

    # Calculate absent dates (days with less than 5 hours present)
    absent_dates = []
    for date_record in all_dates:
        date = date_record['date']
        hours_present = student_attendance.filter(date=date, is_present=True).values('hour').distinct().count()
        if hours_present < 5:  # If less than 5 hours, it's an absent day
            absent_dates.append(date)

    # Total absent days
    absent_count = len(absent_dates)

    return render(request, 'stdnt_attendance.html', {
        'present_count': full_day_count,  # Full-day attendance from model
        'absent_count': absent_count,     # Days not fully present
        'absent_dates': absent_dates,     # List of absent dates
    })




from django.shortcuts import render, get_object_or_404, redirect
from .models import Student,Teacher
from django.http import HttpResponse

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Student, Course

def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    courses = Course.objects.all()

    if request.method == "POST":
        print("POST data:", request.POST)

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
        if not selected_course_id:
            messages.error(request, "Please select a department.")
            return redirect('edit_student', student_id=student_id)

        try:
            course = Course.objects.get(id=selected_course_id)
        except Course.DoesNotExist:
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



def delete_student(request, student_id):
    # Get the student by ID
    student = get_object_or_404(Student, id=student_id)
    
    # Delete the student
    student.delete()
    
    return redirect('ManageStudent')  # Redirect back to the student management page
 




from django.shortcuts import render, redirect, get_object_or_404
from .models import Teacher, Course

def edit_teacher(request, teacher_no):
    # Get the teacher by ID
    teacher = get_object_or_404(Teacher, id=teacher_no)
    # Get all courses for the dropdown
    courses = Course.objects.all()

    if request.method == "POST":
        # Update the teacher data from the form
        teacher.name = request.POST.get('teacherName')
        teacher.email = request.POST.get('teacherEmail')
        teacher.teacher_id = request.POST.get('teacherReg')
        teacher.mobile = request.POST.get('teacherMobile')
        teacher.password = request.POST.get('teacherPassword')
        
        # Get the selected Course instance based on the ID from the form
        course_id = request.POST.get('teacherDepartment')
        teacher.department = get_object_or_404(Course, id=course_id)
        
        # Save the updated teacher
        teacher.save()
        
        return redirect('ManageTeacher')  # Redirect back to the teacher management page
    
    # Pass the teacher and courses to the template
    return render(request, 'edit_teacher.html', {'teacher': teacher, 'courses': courses})

def delete_teacher(request, teacher_no):
    # Get the teacher by ID
    teacher = get_object_or_404(Teacher, id=teacher_no)
    
    # Delete the teacher
    teacher.delete()
    
    return redirect('ManageTeacher')  # Redirect back to the teacher management page



def edit_course(request, course_no):
    # Get the course by ID
    course = get_object_or_404(Course, id=course_no)
    
    if request.method == "POST":
        # Update the course data from the form
        course.course_id = request.POST.get('courseId')
        course.course_name = request.POST.get('courseName')
        course.duration = request.POST.get('courseDuration')
        
        # Save the updated coourse
        course.save()
        
        return redirect('ManageCourse')  # Redirect back to the course management page
    
    return render(request, 'edit_course.html', {'course': course})

def delete_course(request, course_no):
    # Get the course by ID
    course = get_object_or_404(Course, id=course_no)
    
    # Delete the course
    course.delete()
    
    return redirect('ManageCourse')  # Redirect back to the course management page

def edit_subject(request ,subject_no):
    subject = get_object_or_404(Subject, id=subject_no)
    
    if request.method == "POST":
        subject.semester = request.POST.get('Semester')
        subject.subject_code = request.POST.get('subjectCode')
        subject.name = request.POST.get('subjectName')
        course_name = request.POST.get('courseName')  # This is a string
        try:
            course_instance = Course.objects.get(course_name=course_name)  # Fetch the Course instance
            subject.course = course_instance  # Assign the instance
        except Course.DoesNotExist:
            # Handle the case where the course doesn't exist
            return HttpResponse("Course not found", status=400)

        
        # Save the updated coourse
        subject.save()
        
        return redirect('ManageSubject')  # Redirect back to the course management page
    
    return render(request, 'edit_subject.html', {'subject': subject})

def delete_subject(request, subject_no):
    subject = get_object_or_404(Subject, id=subject_no)
    
    subject.delete()
    
    return redirect('ManageSubject')  # Redirect back to the course management page

# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Student, Course

def add_student(request):
    if request.method == "POST":
        name = request.POST.get('name')
        student_class = request.POST.get('Class')
        department_id = request.POST.get('department')  # This will be the course ID
        register_id = request.POST.get('register_id')
        mobile = request.POST.get('mobile')
        email = request.POST.get('email')
        parent = request.POST.get('parent')
        parent_no = request.POST.get('parent_no')
        password = request.POST.get('password')
        # Check if register_id already exists
        if Student.objects.filter(register_id=register_id).exists():
            messages.error(request, "Register ID already exists. Please use a unique ID.")
            return redirect('ManageStudent')

        # Get the Course object
        try:
            department = Course.objects.get(id=department_id)
        except Course.DoesNotExist:
            messages.error(request, "Invalid department selected.")
            return redirect('ManageStudent')

        # Save the student if register_id is unique
        student = Student(
            name=name,
            Class=student_class,
            department=department,  # ForeignKey to Course
            register_id=register_id,
            mobile=mobile,
            email=email,
            parent=parent,
            parent_no=parent_no,
            password=password,
        )
        student.save()
        messages.success(request, "Student added successfully!")
        return redirect('ManageStudent')

    # Fetch all courses and students for the template
    courses = Course.objects.all()
    students = Student.objects.all()
    return render(request, 'admin_mg_student.html', {'courses': courses, 'student': students})

def manage_student_view(request):
    # This view might already exist; ensure it passes students and courses
    courses = Course.objects.all()
    students = Student.objects.all()
    return render(request, 'admin_mg_student.html', {'courses': courses, 'student': students})

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Teacher, Course

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

        try:
            course = Course.objects.get(course_name=department_name)
        except Course.DoesNotExist:
            messages.error(request, "Selected department does not exist.")
            return redirect('ManageTeacher')

        teacher = Teacher(
            name=name,
            email=email,
            teacher_id=teacher_id,
            mobile=mobile,
            department=course,
            password=password,
        )
        teacher.save()
        messages.success(request, "Teacher added successfully!")
        return redirect('ManageTeacher')

    courses = Course.objects.all()
    return render(request, 'admin_mg_teacher.html', {'courses': courses})

def manage_teacher_view(request):
    teachers = Teacher.objects.all()
    courses = Course.objects.all()
    return render(request, 'admin_mg_teacher.html', {'teacher': teachers, 'courses': courses})


from django.shortcuts import redirect
from django.contrib.auth import logout

def logout_view(request):
    logout(request)  
    return redirect('index') 


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Student
import re

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Student

def student_profile_view(request):
    student_id = request.session.get('register_id')
    if not student_id:
        return redirect('login')  # Redirect to login if no session
    
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return redirect('login')  # Redirect if student not found

    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')
            class_name = request.POST.get('class')
            mobile = request.POST.get('mobile')
            email = request.POST.get('email')
            parent = request.POST.get('parent')
            parent_no = request.POST.get('parent_no')

            # Validate mobile numbers
            if not mobile.isdigit() or len(mobile) != 10:
                messages.error(request, "Mobile number must be 10 digits")
                return render(request, 'student_profile.html', {'student': student})

            if not parent_no.isdigit() or len(parent_no) != 10:
                messages.error(request, "Parent mobile number must be 10 digits")
                return render(request, 'student_profile.html', {'student': student})

            # Check if email is already taken by another student
            if Student.objects.exclude(id=student_id).filter(email=email).exists():
                messages.error(request, "Email is already in use by another student")
                return render(request, 'student_profile.html', {'student': student})

            # Update student object
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
