from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import ToDoList, Subjects
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from authentication.models import CustomUser
from django import forms
from collections import OrderedDict
from django.views.generic import DetailView
from .models import Subjects
from .models import ToDoList

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
        
        print("Users found:", users)
        
        # Check if there are any users related to the subject code
        if users.exists():
            # Get the number of students assigned to the subject code
            
            # Create and save a task instance for each user
            for user in users:
                print("Creating task for user:", user)
                task = ToDoList.objects.create(
                    Subject_Code=form.instance.Subject_Code,
                    user=user,
                    task=form.cleaned_data['task'],
                    description=form.cleaned_data['description'],
                    status=False,  # Default status to False
                    deadline=form.cleaned_data['deadline'],
                    perfect=form.cleaned_data['perfect'],
                    assigned_user=user  # Assign the user to the task
                )
                print("Task created:", task)
                
            return super().form_valid(form)
        else:
            # No users related to the subject code, return an error or handle it accordingly
            print("No users found related to the subject code. Cannot create task.")
            return HttpResponse("No users related to the subject code. Cannot create task.")
    
    def get_success_url(self):
        # Get the primary key (pk) of the subject object
        subject_pk = self.kwargs['pk']
        # Generate the success URL with the subject's pk
        success_url = reverse_lazy('class_details', kwargs={'pk': subject_pk})
        return success_url






class TaskUpdate(UpdateView):
    model = ToDoList
    fields = ['Subject_Code', 'task', 'description', 'status', 'deadline', 'score', 'perfect']
    template_name = 'todolist/taskupdate.html'
    success_url = reverse_lazy('teacher_tasks')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs['pk']  # Pass the 'pk' from URL kwargs to the template
        return context
    
class DeleteTask(DeleteView):
    model = ToDoList
    context_object_name = 'data'
    template_name = 'todolist/task_delete.html'
    success_url = reverse_lazy('viewgrades')

    def get_object(self, queryset=None):
        # Return the task object based on the provided task ID
        return self.model.objects.get(pk=self.kwargs['pk'])

    def post(self, request, *args, **kwargs):
        # Check if the "Confirm Delete" button is clicked
        if "confirm_delete" in request.POST:
            # Proceed with the deletion
            return self.confirm_delete(request, *args, **kwargs)
        # If cancellation is requested, redirect back to the detail view
        return HttpResponseRedirect(self.request.path)

    def confirm_delete(self, request, *args, **kwargs):
        # Retrieve the task object
        task = self.get_object()
        subject = task.Subject_Code
        task_name = task.task
        # Delete all tasks with the same name as the selected task within the subject
        tasks_to_delete = ToDoList.objects.filter(Subject_Code=subject, task=task_name)
        tasks_to_delete.delete()
        # Redirect to the success URL
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        # Retrieve subject PK from the session
        subject_pk = self.request.session.get('subject_pk')
        return reverse_lazy('viewtasks', kwargs={'pk': subject_pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs['pk']  # Pass subject_pk to the context
        return context
    
# class DeleteTask(DeleteView):
#     model = ToDoList
#     context_object_name = 'data'
#     template_name = 'todolist/task_delete.html'

#     def get_success_url(self):
#         task_id = self.kwargs['task_id']
#         task = ToDoList.objects.get(pk=task_id)
#         # Get the primary key (pk) of the subject object
#         subject_pk = task.Subject_Code.pk
#         # Generate the success URL with the subject's pk
#         success_url = reverse_lazy('viewtasks', kwargs={'pk': subject_pk})
#         return success_url

# class DeleteTask(View):
#     def get_success_url(self):
#         try:
#             # Retrieve the subject_pk from the URL parameters
#             subject_pk = self.kwargs['subject_pk']
#             # Generate the success URL with the subject's pk
#             success_url = reverse_lazy('viewtasks', kwargs={'pk': subject_pk})
#             return success_url
#         except KeyError:
#             # Handle the case where the subject_pk is not found in the URL parameters
#             return reverse_lazy('error-view')
    
#     def post(self, request, task_id):
#         try:
#             # Retrieve the task object
#             task = ToDoList.objects.get(pk=task_id)
#             # Retrieve the subject_pk from the task object
#             subject_pk = task.Subject_Code.pk
#             # Delete the task
#             task.delete()
#         except ToDoList.DoesNotExist:
#             # Handle the case where the task does not exist
#             return HttpResponse("The task with the provided ID does not exist.")
        
#         # Redirect to the success URL
#         return redirect(self.get_success_url())

    


# class DeleteTask(View):
#     def post(self, request, pk, *args, **kwargs):
#         task = ToDoList.objects.filter(pk=pk)
#         if task.exists():
#             task_name = task.first().task
#             # Delete all tasks with the same name
#             ToDoList.objects.filter(task=task_name).delete()
#             return redirect('viewtasks', pk=task.first().Subject_Code.pk)
#         # Handle if task does not exist
#         return redirect('viewtasks', pk=None)
    

# class ConfirmDeleteView(View):

#     def get_success_url(self):
#         # Get the primary key (pk) of the subject object
#         subject_pk = self.kwargs['pk']
#         # Generate the success URL with the subject's pk
#         success_url = reverse_lazy('class_details', kwargs={'pk': subject_pk})
#         return success_url



    # def get(self, request, subject_pk, *args, **kwargs):
    #     try:
    #         # Retrieve the subject object based on subject_pk
    #         subject = Subjects.objects.get(pk=subject_pk)
    #         # Retrieve the task object based on the provided task id
    #         task_id = self.kwargs['task_id']
    #         task = ToDoList.objects.get(pk=task_id)
    #         # Get the task name
    #         task_name = task.task
    #         # Delete all tasks with the same name as the selected task
    #         tasks_to_delete = ToDoList.objects.filter(Subject_Code=subject, task=task_name)
    #         tasks_to_delete.delete()
    #     except (Subjects.DoesNotExist, ToDoList.DoesNotExist):
    #         # Handle the case where the subject or task does not exist
    #         return HttpResponse("The subject or task with the provided ID does not exist.")






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

    

    def get_success_url(self):
        # Retrieve subject PK from session
        subject_pk = self.request.session.get('subject_pk')
        print("Retrieved subject PK from session:", subject_pk)
        return reverse_lazy('viewtasks', kwargs={'pk': subject_pk})
    


class ViewGrades(DetailView):
    model = Subjects
    context_object_name = 'subject'
    template_name = 'Grades/viewgradestrial.html'

    def test_func(self):
        return self.request.user.is_teacher  # Ensures only teachers can access this view

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subject = self.get_object()
        students = subject.users.all()  # Get all students associated with the subject

        # Fetch all tasks related to the subject code
        all_tasks = ToDoList.objects.filter(Subject_Code=subject)

        # Extract unique tasks
        unique_tasks = []
        seen_tasks = set()
        for task in all_tasks:
            if task.task not in seen_tasks:
                unique_tasks.append(task)
                seen_tasks.add(task.task)

        student_scores = []
        for student in students:
            student_data = {'student': student, 'scores': []}
            for task in unique_tasks:
                # Retrieve task assigned to the student
                assigned_task = all_tasks.filter(task=task.task, user=student).first()
                # If task is assigned to the student, retrieve score
                score = assigned_task.score if assigned_task else None
                student_data['scores'].append({'task': task, 'score': score})
            student_scores.append(student_data)

        context['students'] = students
        context['tasks'] = unique_tasks
        context['student_scores'] = student_scores

        return context
    
class ViewTasks(DetailView):
    model = Subjects
    context_object_name = 'subject'
    template_name = 'todolist/StudentClass.html'

    def test_func(self):
        return self.request.user.is_teacher
    
    def get(self, request, *args, **kwargs):
        # Store subject PK in session
        subject_pk = self.kwargs['pk']
        request.session['subject_pk'] = subject_pk
        print("Stored subject PK in session:", subject_pk)
        return super().get(request, *args, **kwargs)
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subject = self.get_object() 
        all_tasks = ToDoList.objects.filter(Subject_Code=subject)

        unique_tasks = []
        seen_tasks = set()
        for task in all_tasks:
            if task.task not in seen_tasks:
                unique_tasks.append(task)
                seen_tasks.add(task.task)
        context['tasks'] = unique_tasks
        return context
    

    

    

    # class ViewTasks(DetailView):
    #     model = Subjects
    #     context_object_name = 'subject'
    #     template_name = 'todolist/StudentClass.html'

        








    
    
# Organize data for each task
        # for task in tasks:
        #     task_students = task.user  # Get the user assigned to the task
        #     if task_students:  # Ensure there's a user assigned to the task
        #         student_info = {
        #             'name': task_students.first_name,
        #             'score': task.score,  # Assuming task.score represents the score for the student
        #         }
        #         task_info = {
        #             'task': task.task,
        #             'student_info': student_info,
        #             'deadline': task.deadline,
        #             'status': task.status,
        #             'perfect': task.perfect,
        #         }
        #         task_data.append(task_info)

        # context['task_data'] = task_data