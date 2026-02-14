from django import forms
from .models import Exam, Question, StudentGroup, ExamSchedule
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model


User = get_user_model()


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        exclude = ['created_by']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = '__all__'


class StudentGroupForm(forms.ModelForm):
    class Meta:
        model = StudentGroup
        fields = ['name', 'students']
        widgets = {
            'students': forms.CheckboxSelectMultiple()
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 👇 Filter only students
        self.fields['students'].queryset = User.objects.filter(user_type='student')


class ExamScheduleForm(forms.ModelForm):
    class Meta:
        model = ExamSchedule
        fields = ['exam', 'group', 'date', 'start_time', 'end_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }
