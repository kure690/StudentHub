from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import ToDoList, Subjects
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from authentication.models import CustomUser
from django import forms

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

class TaskCreate(CreateView):
    model = ToDoList
    fields = ['Subject_Code', 'task', 'description', 'deadline', 'perfect']
    template_name = 'todolist/task_form.html'
    success_url = reverse_lazy('teacher_tasks')

    def form_valid(self, form):
        # Save the form instance
        response = super().form_valid(form)
        # Get the subject code from the form
        subject_code = form.cleaned_data['Subject_Code']
        # Retrieve users under the selected subject
        users = CustomUser.objects.filter(subjects__Subject_Code=subject_code)
        # Assign the task to the retrieved users
        for user in users:
            self.object.users.add(user)
        return response



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



class ClassCreate(CreateView):
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['class'] = context['class'].filter(user=self.request.user)

