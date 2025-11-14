from django.db import models

# Create your models here.
class Course(models.Model):
    course_id = models.CharField(max_length=30,unique=True)
    course_name = models.CharField(max_length=30,unique=True,default= ' ')
    duration = models.CharField(max_length=25, default='3 Year', blank=True, null=True)
    def __str__(self):
        return self.course_name
    
    
class Teacher(models.Model):
    name=models.CharField(max_length=30)
    email=models.EmailField(unique=True)
    teacher_id=models.CharField(max_length=20,unique=True)
    mobile = models.CharField(max_length=10,default=' ')  # Changed from IntegerField to CharField
    password=models.CharField(max_length=15)
    department = models.ForeignKey(Course, on_delete=models.CASCADE) 



from django.db import models
from django.db.models import Count, Q


class Student(models.Model):
    name = models.CharField(max_length=30)
    Class = models.CharField(max_length=20)
    department = models.ForeignKey(Course, on_delete=models.CASCADE)  # Changed to ForeignKey    register_id = models.CharField(max_length=30,unique=True)
    register_id = models.CharField(max_length=30, unique=True)
    mobile = models.CharField(max_length=10)  
    email = models.EmailField(unique=True)
    parent = models.CharField(max_length=30)
    parent_no = models.CharField(max_length=10)  # Changed from IntegerField to CharField
    password = models.CharField(max_length=15)
    full_day_attendance = models.PositiveIntegerField(default=0)  # To store full-day attendance count
    is_approved = models.BooleanField(default=False) 
    def __str__(self):
        return self.name
    
    def update_full_day_attendance(self, date):
        """Updates the full-day attendance count for the student if they are present for 5 hours on the given date."""
        hours_present_today = (
            Attendance.objects.filter(
                student=self,
                date=date,
                is_present=True
            )
            .values('hour')
            .distinct()
            .count()
        )

        if hours_present_today == 5:
            self.full_day_attendance += 1
            self.save()


    

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
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.subject_code}) - {self.course.course_name}"


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    hour = models.PositiveSmallIntegerField()  # No choices here; teacher selects freely
    is_present = models.BooleanField(default=False)
    # Add a ForeignKey to Subject if you need to associate attendance with a subject


    class Meta:
        unique_together = ('student', 'date', 'hour')

    def __str__(self):
        return f"Attendance: {self.student} on {self.date} - Hour {self.hour}: {'Present' if self.is_present else 'Absent'}"
    

class Marks(models.Model):
    semester = models.CharField(max_length=20)
    registerId = models.ForeignKey(Student, on_delete=models.CASCADE,null=True,blank=True)
    exam_name = models.CharField(max_length=50)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    subject =models.ForeignKey(Subject, on_delete=models.CASCADE,null=True,blank=True)
    internalMarks = models.PositiveIntegerField(default=0)
    externalMarks = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.registerId} - {self.semester} - {self.subject}"