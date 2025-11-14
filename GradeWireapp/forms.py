from django import forms
from django.contrib.auth.models import User
from . import models

from django import forms
from .models import Teacher, Course

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['name', 'email', 'teacher_id', 'mobile', 'password', 'department']

    # Customize the department field
    department = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        empty_label="Select Department",
        label="Department",
        to_field_name=None  # Use the default pk (id); we'll customize display in the widget
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize how department choices are displayed
        self.fields['department'].label_from_instance = lambda obj: obj.course_name


from django import forms
from .models import Student,Course

class StudentForm(forms.ModelForm):
    department = forms.ModelChoiceField(queryset=Course.objects.all(), empty_label="Select Department")
    class Meta:
        model = Student
        fields = ['name', 'Class', 'department', 'register_id', 'mobile', 'email', 'parent', 'parent_no', 'password']  


from django import forms
from .models import Marks, Student, Course, Subject

class MarksForm(forms.ModelForm):
    class Meta:
        model = Marks
        fields = ['semester', 'registerId', 'exam_name', 'course', 'subject', 'internalMarks', 'externalMarks']

    SEMESTER_CHOICES = [
        ('semester-1', 'Semester 1'),
        ('semester-2', 'Semester 2'),
        ('semester-3', 'Semester 3'),
        ('semester-4', 'Semester 4'),
        ('semester-5', 'Semester 5'),
        ('semester-6', 'Semester 6'),
    ]
    EXAM_CHOICES = [
        ('internal-1', 'Internal Exam 1'),
        ('internal-2', 'Internal Exam 2'),
        ('model', 'Model Exam'),
        ('sem-exam', 'Semester Exam'),
    ]

    semester = forms.ChoiceField(choices=SEMESTER_CHOICES)
    exam_name = forms.ChoiceField(choices=EXAM_CHOICES)
    registerId = forms.ModelChoiceField(queryset=Student.objects.none(), required=False)
    course = forms.ModelChoiceField(queryset=Course.objects.all())
    subject = forms.ModelChoiceField(queryset=Subject.objects.none())
    internalMarks = forms.IntegerField(required=False)
    externalMarks = forms.IntegerField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)