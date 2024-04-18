from django.urls import path
from .views import ToDo, ToDoDetail, TaskCreate, TaskUpdate, TeacherToDo, ClassCreate, ClassView, ClassUpdate, ClassDetails, AddStudent, DeleteClass, ViewGrades, ViewTasks, DeleteTask

urlpatterns = [
    path('todolist/', ToDo.as_view(), name='tasks'),
    path('todolistdetail/<int:pk>/', ToDoDetail.as_view(), name='task'),
    path('create_task/<int:pk>/', TaskCreate.as_view(), name='task-create'),
    path('task-update/<int:pk>/', TaskUpdate.as_view(), name='task-update'),
    path('teacher-todolist/', TeacherToDo.as_view(), name='teacher_tasks'),
    path('create_class/', ClassCreate.as_view(), name='Class_create'),
    path('classview/', ClassView.as_view(), name='Class_view'),
    path('classupdate/<int:pk>/', ClassUpdate.as_view(), name='class_update'),
    path('classdetails/<int:pk>/', ClassDetails.as_view(), name='class_details'),
    path('addstudent/<int:pk>/', AddStudent.as_view(), name='add_student'),
    path('classdelete/<int:pk>/', DeleteClass.as_view(), name='class_delete'),
    path('viewgrades/<int:pk>/', ViewGrades.as_view(), name='viewgrades'),
    path('viewtasks/<int:pk>/', ViewTasks.as_view(), name='viewtasks'), 
    # path('delete-task/<int:task_id>/', DeleteTask.as_view(), name='delete-task'),
    path('task-delete/<int:pk>/', DeleteTask.as_view(), name='task-delete'),
    # path('confirm-delete/<int:subject_pk>/', ConfirmDeleteView.as_view(), name='confirm-delete'),

]
