from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Exam(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    total_marks = models.IntegerField()
    duration_minutes = models.IntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)

    OPTION_CHOICES = (
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    )
    correct_option = models.CharField(max_length=1, choices=OPTION_CHOICES)
    marks = models.IntegerField(default=1)

    def __str__(self):
        return self.question_text[:50]

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta

User = get_user_model()


class StudentGroup(models.Model):
    name = models.CharField(max_length=100)
    students = models.ManyToManyField(User, related_name="student_groups")

    def __str__(self):
        return self.name

class ExamSchedule(models.Model):
    exam = models.ForeignKey("Exam", on_delete=models.CASCADE)
    group = models.ForeignKey(StudentGroup, on_delete=models.CASCADE)

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    is_cancelled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # 1️⃣ End time must be greater than start time
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be greater than start time.")

        # 2️⃣ Prevent overlapping schedules for students
        students = self.group.students.all()

        for student in students:
            existing_schedules = ExamSchedule.objects.filter(
                group__students=student,
                date=self.date,
                is_cancelled=False
            ).exclude(pk=self.pk)

            for schedule in existing_schedules:
                if (
                    self.start_time < schedule.end_time and
                    self.end_time > schedule.start_time
                ):
                    raise ValidationError(
                        f"Time conflict detected for student {student.username}"
                    )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def cancel(self):
        self.is_cancelled = True
        self.save()


    def __str__(self):
        return f"{self.exam} - {self.group} - {self.date}"
