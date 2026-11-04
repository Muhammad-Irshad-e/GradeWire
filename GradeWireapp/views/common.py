from functools import wraps
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import redirect
from django.contrib import messages
from ..models import Teacher, Student, Course


def verify_and_upgrade_password(raw_password, stored_password, instance):
    """
    Validates a raw password against the stored password.
    Supports both hashed passwords and legacy plaintext passwords.
    If the password matches the legacy plaintext format, it is automatically
    upgraded to a secure hashed password.
    """
    if not raw_password or not stored_password:
        return False
    if check_password(raw_password, stored_password):
        return True
    if raw_password == stored_password:
        instance.password = make_password(raw_password)
        instance.save(update_fields=['password'])
        return True
    return False


def admin_required(view_func):
    """Decorator to require authenticated admin user (staff or superuser)."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)):
            messages.error(request, "Admin access required. Please log in.")
            return redirect('adminlogin')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def teacher_required(view_func):
    """Decorator to require authenticated teacher session."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        teacher_id = request.session.get('teacher_id')
        if not teacher_id or not Teacher.objects.filter(id=teacher_id).exists():
            messages.error(request, "Teacher access required. Please log in.")
            return redirect('teacherLogin')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def student_required(view_func):
    """Decorator to require approved and authenticated student session."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        student_id = request.session.get('register_id')
        if not student_id or not Student.objects.filter(id=student_id, is_approved=True).exists():
            messages.error(request, "Student access required. Please log in.")
            return redirect('studentLogin')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def get_course_instance(dept_identifier):
    """
    Safely resolves a Course instance by primary key ID, course_name, or course_id.
    Standardizes lookups across endpoints that receive different identifier types.
    """
    if not dept_identifier:
        return None
    dept_str = str(dept_identifier).strip()
    if dept_str.isdigit():
        course = Course.objects.filter(id=int(dept_str)).first()
        if course:
            return course
    return (
        Course.objects.filter(course_name__iexact=dept_str).first()
        or Course.objects.filter(course_id__iexact=dept_str).first()
    )
