from django.urls import path
from .views import ToDo, ToDoDetail, TaskCreate, TaskUpdate, DeleteTask, TeacherToDo, ClassCreate, ClassView, ClassUpdate, ClassDetails, AddStudent

urlpatterns = [
    path('todolist/', ToDo.as_view(), name='tasks'),
    path('todolistdetail/<int:pk>/', ToDoDetail.as_view(), name='task'),
    path('create_task/<int:pk>/', TaskCreate.as_view(), name='task-create'),
    path('task-update/<int:pk>/', TaskUpdate.as_view(), name='task-update'),
    path('task-delete/<int:pk>/', DeleteTask.as_view(), name='task-delete'),
    path('teacher-todolist/', TeacherToDo.as_view(), name='teacher_tasks'),
    path('create_class/', ClassCreate.as_view(), name='Class_create'),
    path('classview/', ClassView.as_view(), name='Class_view'),
    path('classupdate/<int:pk>/', ClassUpdate.as_view(), name='class_update'),
    path('classdetails/<int:pk>/', ClassDetails.as_view(), name='class_details'),
    path('addstudent/<int:pk>/', AddStudent.as_view(), name='add_student'),

]