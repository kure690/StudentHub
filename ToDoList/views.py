from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import ToDoList, Subjects
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from authentication.models import CustomUser
from django import forms
from collections import OrderedDict

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
            context['tasks'] = context['tasks'].filter(Subject_Code__Subject_Code__icontains=search_input)

        context['search_input']=search_input
        
        return context
    
    
class TeacherToDo(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = ToDoList
    context_object_name = 'tasks'
    template_name = 'todolist/todolistteacher_list.html'  # Assuming you have a separate template for teachers

    def test_func(self):
        return self.request.user.is_teacher  # Ensures only teachers can access this view

    def get_queryset(self):
        return ToDoList.objects.filter(user__is_student=True)  # Filter tasks of students only

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        search_input = self.request.GET.get('search area') or ''
        if search_input:
            context['tasks'] = context['tasks'].filter(subject__icontains=search_input)

        context['search_input'] = search_input
        
        return context
    



class ToDoDetail(DetailView):
    model = ToDoList
    context_object_name = 'data'
    template_name = 'todolist/todolist.html'

class TaskCreate(LoginRequiredMixin, CreateView):
    model = ToDoList
    fields = ['task', 'description', 'deadline', 'perfect']
    template_name = 'todolist/task_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs.get('pk')
        return context

    def form_valid(self, form):
        # Set the Subject_Code_id for the task
        form.instance.Subject_Code_id = self.kwargs.get('pk')
        
        # Get the users related to the subject code
        subject = form.instance.Subject_Code
        users = subject.users.all()
        
        # Create and save a task instance for each user
        for user in users:
            task = ToDoList.objects.create(
                Subject_Code=form.instance.Subject_Code,
                user=user,
                task=form.cleaned_data['task'],
                description=form.cleaned_data['description'],
                status=False,  # Default status to False
                deadline=form.cleaned_data['deadline'],
                perfect=form.cleaned_data['perfect']
            )

        return super().form_valid(form)
    
    def get_success_url(self):
        # Get the primary key (pk) of the subject object
        subject_pk = self.kwargs['pk']
        # Generate the success URL with the subject's pk
        success_url = reverse_lazy('class_details', kwargs={'pk': subject_pk})
        return success_url



class TaskUpdate(UpdateView):
    model = ToDoList
    fields = ['Subject_Code', 'task', 'description', 'status', 'deadline', 'score', 'perfect']
    template_name = 'todolist/task_form.html'
    success_url = reverse_lazy('teacher_tasks')

    


class DeleteTask(DeleteView):
    model = ToDoList
    context_object_name = 'data'
    template_name = 'todolist/task_delete.html'
    success_url = reverse_lazy('teacher_tasks')



class ClassCreate(LoginRequiredMixin, CreateView):
    model = Subjects
    context_object_name = 'class'
    fields = '__all__'
    template_name = 'todolist/CreateClass.html'
    success_url = reverse_lazy('dashboard')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        users_queryset = CustomUser.objects.filter(is_student=True)
        form.fields['users'] = forms.ModelMultipleChoiceField(
            queryset=users_queryset,
            widget=forms.CheckboxSelectMultiple,
            required=False
        )
        return form

    def form_valid(self, form):
        # Save the form instance
        response = super().form_valid(form)
        # Add selected users to the task
        self.object.users.set(form.cleaned_data['users'])
        return response
    
class ClassView(ListView):
    model = Subjects
    context_object_name = 'class'
    template_name = 'todolist/ClassView.html'

    def get_queryset(self):
        return Subjects.objects.all()

class ClassUpdate(UpdateView):
    model = Subjects
    fields = '__all__'
    template_name = 'todolist/ClassAdd.html'
    success_url = reverse_lazy('teacher_tasks')
    

class ClassDetails(LoginRequiredMixin, DetailView):
    model = Subjects
    context_object_name = 'subject'  # Change context_object_name to match what you're using in the template
    template_name = 'todolist/ClassDetails.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subject = self.get_object()
        
        # Fetching all tasks related to the subject
        tasks = ToDoList.objects.filter(Subject_Code=subject)
        
        # Using OrderedDict to maintain the order of tasks and remove duplicates
        unique_tasks = OrderedDict()

        for task in tasks:
            unique_tasks[task.task] = task

        context['tasks'] = unique_tasks.values()

        return context
    
class AddStudent(LoginRequiredMixin, UpdateView):
    model = Subjects
    fields = ['users']
    template_name = 'todolist/ClassAdd.html'

    def get_success_url(self):
        # Get the primary key (pk) of the subject object
        subject_pk = self.kwargs['pk']
        # Generate the success URL with the subject's pk
        success_url = reverse_lazy('class_details', kwargs={'pk': subject_pk})
        return success_url
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs.get('pk')
        return context
    

class DeleteClass(LoginRequiredMixin, DeleteView):
    model = Subjects
    context_object_name = 'subject'
    template_name = 'todolist/class_delete.html'
    success_url = reverse_lazy('dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs.get('pk')
        return context