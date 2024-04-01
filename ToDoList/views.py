from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import ToDoList
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

# Create your views here.

class ToDo(ListView):
    model = ToDoList
    context_object_name = 'tasks'

class ToDoDetail(DetailView):
    model = ToDoList
    context_object_name = 'data'
    template_name = 'todolist/todolist.html'

class TaskCreate(CreateView):
    model = ToDoList
    fields = '__all__'
    template_name = 'todolist/task_form.html'
    success_url = reverse_lazy('tasks')

class TaskUpdate(UpdateView):
    model = ToDoList
    fields = '__all__'
    template_name = 'todolist/task_form.html'
    success_url = reverse_lazy('tasks')


class DeleteTask(DeleteView):
    model = ToDoList
    context_object_name = 'data'
    template_name = 'todolist/task_delete.html'
    success_url = reverse_lazy('tasks')



