from django.forms import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import ToDoList
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

# Create your views here.



class ToDo(LoginRequiredMixin, ListView):
    model = ToDoList
    context_object_name = 'tasks'
    template_name = 'todolist/todolist_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)

        search_input = self.request.GET.get('search area') or ''
        if search_input:
            context['tasks']=context['tasks'].filter(subject__icontains=search_input)

        context['search_input']=search_input
        
        return context
    


class ToDoDetail(DetailView):
    model = ToDoList
    context_object_name = 'data'
    template_name = 'todolist/todolist.html'

class TaskCreate(CreateView):
    model = ToDoList
    fields = ['subject', 'task', 'description', 'status', 'deadline']
    template_name = 'todolist/task_form.html'
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)


class TaskUpdate(UpdateView):
    model = ToDoList
    fields = ['subject', 'task', 'description', 'status', 'deadline']
    template_name = 'todolist/task_form.html'
    success_url = reverse_lazy('tasks')


class DeleteTask(DeleteView):
    model = ToDoList
    context_object_name = 'data'
    template_name = 'todolist/task_delete.html'
    success_url = reverse_lazy('tasks')



