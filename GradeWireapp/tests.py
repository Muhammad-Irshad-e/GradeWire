import json
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import ProtectedError
from .models import Course, Subject, Teacher, Student, Attendance, Marks
from .views.common import verify_and_upgrade_password, get_course_instance


class ModelAndDatabaseIntegrityTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            course_name="Computer Science",
            course_id="CS101",
            duration="3 Years"
        )
        self.subject = Subject.objects.create(
            course=self.course,
            name="Data Structures",
            subject_code="CS201",
            semester="semester-1"
        )
        self.student = Student.objects.create(
            name="Alice Smith",
            Class="1st Year",
            department=self.course,
            register_id="REG001",
            mobile="9876543210",
            email="alice@example.com",
            parent="Bob Smith",
            parent_no="9876543211",
            password=make_password("securepass123"),
            is_approved=True
        )
        self.teacher = Teacher.objects.create(
            name="Dr. Alan Turing",
            email="alan@example.com",
            teacher_id="T001",
            mobile="9123456780",
            department=self.course,
            password=make_password("teacherpass123")
        )

    def test_string_representations(self):
        """Verify model __str__ representations return expected values."""
        self.assertEqual(str(self.course), "Computer Science")
        self.assertEqual(str(self.subject), "Data Structures (CS201) - Computer Science")
        self.assertEqual(str(self.student), "Alice Smith")
        self.assertEqual(str(self.teacher), "Dr. Alan Turing (T001)")

    def test_course_protected_against_cascade_deletion(self):
        """Course deletion must raise ProtectedError if dependent objects exist."""
        with self.assertRaises(ProtectedError):
            self.course.delete()

    def test_idempotent_full_day_attendance(self):
        """Full day attendance should count dates with >= 5 distinct present hours idempotently."""
        today = date(2026, 10, 29)
        # Mark 5 distinct hours as present
        for h in range(1, 6):
            Attendance.objects.create(
                student=self.student,
                date=today,
                hour=h,
                subject=self.subject,
                is_present=True
            )

        self.student.update_full_day_attendance(today)
        self.student.refresh_from_db()
        self.assertEqual(self.student.full_day_attendance, 1)

        # Re-running the calculation must remain 1 (idempotent)
        self.student.update_full_day_attendance(today)
        self.student.refresh_from_db()
        self.assertEqual(self.student.full_day_attendance, 1)

    def test_attendance_uniqueness_constraint(self):
        """Student, date, hour, subject combination must be unique."""
        today = date(2026, 10, 29)
        Attendance.objects.create(
            student=self.student,
            date=today,
            hour=1,
            subject=self.subject,
            is_present=True
        )
        # Unique together should allow updating via update_or_create without duplicates
        obj, created = Attendance.objects.update_or_create(
            student=self.student,
            date=today,
            hour=1,
            subject=self.subject,
            defaults={'is_present': False}
        )
        self.assertFalse(created)
        self.assertFalse(obj.is_present)
        self.assertEqual(Attendance.objects.filter(student=self.student, date=today, hour=1).count(), 1)

    def test_marks_uniqueness_constraint(self):
        """Marks model enforces uniqueness on registerId, semester, exam_name, and subject."""
        mark, created = Marks.objects.update_or_create(
            registerId=self.student,
            semester="semester-1",
            exam_name="Mid-Term",
            subject=self.subject,
            defaults={
                'course': self.course,
                'internalMarks': 25,
                'externalMarks': 65
            }
        )
        self.assertTrue(created)
        self.assertEqual(mark.internalMarks, 25)

        # Update existing record
        mark_updated, created_again = Marks.objects.update_or_create(
            registerId=self.student,
            semester="semester-1",
            exam_name="Mid-Term",
            subject=self.subject,
            defaults={
                'course': self.course,
                'internalMarks': 28,
                'externalMarks': 70
            }
        )
        self.assertFalse(created_again)
        self.assertEqual(mark_updated.internalMarks, 28)
        self.assertEqual(Marks.objects.filter(registerId=self.student, exam_name="Mid-Term").count(), 1)


class AuthenticationAndSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.course = Course.objects.create(course_name="Physics", course_id="PHY01", duration="3 Years")
        self.teacher = Teacher.objects.create(
            name="Teacher One",
            email="t1@example.com",
            teacher_id="T100",
            mobile="9876501234",
            department=self.course,
            password="plaintext_legacy_pass"
        )
        self.student = Student.objects.create(
            name="Student One",
            Class="1st Year",
            department=self.course,
            register_id="S100",
            mobile="9876501235",
            email="s1@example.com",
            password=make_password("studentsecret"),
            is_approved=True
        )
        self.admin_user = User.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="adminpassword123"
        )

    def test_verify_and_upgrade_plaintext_password(self):
        """Plaintext password validates and automatically upgrades to a secure hash."""
        # Initial state: plaintext
        self.assertEqual(self.teacher.password, "plaintext_legacy_pass")

        # Validation succeeds
        result = verify_and_upgrade_password("plaintext_legacy_pass", self.teacher.password, self.teacher)
        self.assertTrue(result)

        # Database state: auto-upgraded to hash
        self.teacher.refresh_from_db()
        self.assertTrue(self.teacher.password.startswith("pbkdf2_sha256$"))
        self.assertTrue(check_password("plaintext_legacy_pass", self.teacher.password))

    def test_admin_route_protection(self):
        """Unauthenticated access to admin dashboard redirects to admin login."""
        response = self.client.get(reverse('adminDashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('adminlogin'), response.url)

    def test_teacher_route_protection(self):
        """Unauthenticated access to teacher dashboard redirects to teacher login."""
        response = self.client.get(reverse('teacherDashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('teacherLogin'), response.url)

    def test_student_route_protection(self):
        """Unauthenticated access to student dashboard redirects to student login."""
        response = self.client.get(reverse('studentDashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('studentLogin'), response.url)

    def test_delete_endpoints_reject_get(self):
        """Delete endpoints must reject HTTP GET requests with 405 Method Not Allowed."""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('delete_student', kwargs={'student_id': self.student.id}))
        self.assertEqual(response.status_code, 405)

        response = self.client.get(reverse('delete_teacher', kwargs={'teacher_no': self.teacher.id}))
        self.assertEqual(response.status_code, 405)

        response = self.client.get(reverse('delete_course', kwargs={'course_no': self.course.id}))
        self.assertEqual(response.status_code, 405)


class HelperAndResolutionTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            course_name="Mechanical Engineering",
            course_id="MECH01",
            duration="4 Years"
        )

    def test_get_course_instance_by_id(self):
        """get_course_instance resolves by primary key integer/string."""
        self.assertEqual(get_course_instance(self.course.id), self.course)
        self.assertEqual(get_course_instance(str(self.course.id)), self.course)

    def test_get_course_instance_by_name(self):
        """get_course_instance resolves by course_name case-insensitively."""
        self.assertEqual(get_course_instance("Mechanical Engineering"), self.course)
        self.assertEqual(get_course_instance("mechanical engineering"), self.course)

    def test_get_course_instance_by_code(self):
        """get_course_instance resolves by course_id code."""
        self.assertEqual(get_course_instance("MECH01"), self.course)

    def test_get_course_instance_invalid(self):
        """Non-existent identifier returns None."""
        self.assertIsNone(get_course_instance("NonExistentCourse"))
        self.assertIsNone(get_course_instance(None))
