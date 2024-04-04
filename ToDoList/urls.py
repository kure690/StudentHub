from django.urls import path
from .views import ToDo, ToDoDetail, TaskCreate, TaskUpdate, DeleteTask, TeacherToDo

urlpatterns = [
    path('todolist/', ToDo.as_view(), name='tasks'),
    path('todolistdetail/<int:pk>/', ToDoDetail.as_view(), name='task'),
    path('create_task/', TaskCreate.as_view(), name='task-create'),
    path('task-update/<int:pk>/', TaskUpdate.as_view(), name='task-update'),
    path('task-delete/<int:pk>/', DeleteTask.as_view(), name='task-delete'),
    path('teacher-todolist/', TeacherToDo.as_view(), name='teacher_tasks'),

]