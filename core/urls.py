from django.urls import path
from core import views 
from student import views as student_views
app_name='core'

urlpatterns = [
    path('', views.landingpage, name='landingpage'),
    path('student_dashboard/', student_views.student_dashboard, name='student_dashboard'),
    path('teacher_dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
]


