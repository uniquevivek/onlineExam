from django.urls import path
from . import views

app_name = 'exam'

urlpatterns = [
    path('', views.exam_list, name='exam_list'),
    path('create/', views.exam_create, name='exam_create'),
    path('<int:pk>/edit/', views.exam_update, name='exam_update'),
    path('<int:pk>/delete/', views.exam_delete, name='exam_delete'),
    path('<int:exam_id>/question/add/', views.question_add, name='question_add'),
]
urlpatterns += [
    path('<int:exam_id>/questions/', views.question_list, name='question_list'),
    path('question/<int:pk>/edit/', views.question_update, name='question_update'),
    path('question/<int:pk>/delete/', views.question_delete, name='question_delete'),
]
