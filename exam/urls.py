from django.urls import path
from . import views

app_name = 'exam'

urlpatterns = [
    path('', views.exam_list, name='exam_list'),
    path('create/', views.exam_create, name='exam_create'),
    path('<int:pk>/edit/', views.exam_update, name='exam_update'),
    path('<int:pk>/delete/', views.exam_delete, name='exam_delete'),
    path('<int:exam_id>/question/add/', views.question_add, name='question_add'),

    path('<int:exam_id>/questions/', views.question_list, name='question_list'),
    path('question/<int:pk>/edit/', views.question_update, name='question_update'),
    path('question/<int:pk>/delete/', views.question_delete, name='question_delete'),
    
    path("groups/", views.group_list, name="group_list"),
    path("groups/create/", views.group_create, name="group_create"),

    path("schedule/", views.schedule_list, name="schedule_list"),
    path("schedule/create/", views.schedule_create, name="schedule_create"),
    path("schedule/<int:pk>/cancel/", views.schedule_cancel, name="schedule_cancel"),
    path("schedule/<int:pk>/reschedule/", views.schedule_reschedule, name="schedule_reschedule"),

]
