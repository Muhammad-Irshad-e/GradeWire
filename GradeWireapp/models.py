from django.db import models
from django.db.models import Count


class Course(models.Model):
    course_id = models.CharField(max_length=30, unique=True)
    course_name = models.CharField(max_length=30, unique=True, default=' ')
    duration = models.CharField(max_length=25, default='3 Year', blank=True, null=True)

    def __str__(self):
        return self.course_name


class Teacher(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    teacher_id = models.CharField(max_length=20, unique=True)
    mobile = models.CharField(max_length=10, default=' ')
    password = models.CharField(max_length=128)
    department = models.ForeignKey(Course, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name} ({self.teacher_id})"


class Student(models.Model):
    name = models.CharField(max_length=30)
    Class = models.CharField(max_length=20)
    department = models.ForeignKey(Course, on_delete=models.PROTECT)
    register_id = models.CharField(max_length=30, unique=True)
    mobile = models.CharField(max_length=10)
    email = models.EmailField(unique=True)
    parent = models.CharField(max_length=30)
    parent_no = models.CharField(max_length=10)
    password = models.CharField(max_length=128)
    full_day_attendance = models.PositiveIntegerField(default=0)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def update_full_day_attendance(self, date=None):
        """
        Idempotently calculates and updates the total full-day attendance count
        for the student. A day qualifies as full-day attendance if the student
        was present for at least 5 distinct hours on that date.
        """
        full_days = (
            Attendance.objects.filter(
                student=self,
                is_present=True
            )
            .values('date')
            .annotate(present_hours=Count('hour', distinct=True))
            .filter(present_hours__gte=5)
            .count()
        )
        self.full_day_attendance = full_days
        self.save(update_fields=['full_day_attendance'])
        return full_days


class Subject(models.Model):
    SEMESTER_CHOICES = [
        ('semester-1', 'Semester 1'),
        ('semester-2', 'Semester 2'),
        ('semester-3', 'Semester 3'),
        ('semester-4', 'Semester 4'),
        ('semester-5', 'Semester 5'),
        ('semester-6', 'Semester 6'),
    ]

    semester = models.CharField(max_length=20, choices=SEMESTER_CHOICES, default='semester-1')
    subject_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.name} ({self.subject_code}) - {self.course.course_name}"


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    hour = models.PositiveSmallIntegerField()
    is_present = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'date', 'hour', 'subject')

    def __str__(self):
        return f"Attendance: {self.student} on {self.date} - Hour {self.hour}: {'Present' if self.is_present else 'Absent'}"


class Marks(models.Model):
    semester = models.CharField(max_length=20)
    registerId = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    exam_name = models.CharField(max_length=50)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)
    internalMarks = models.PositiveIntegerField(default=0)
    externalMarks = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('registerId', 'semester', 'exam_name', 'subject')

    def __str__(self):
        return f"{self.registerId} - {self.semester} - {self.subject}"