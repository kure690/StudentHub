from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import SubjectSchedule, ToDoList, Subjects
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

class TaskCreate(LoginRequiredMixin,  UserPassesTestMixin, CreateView):
    model = ToDoList
    fields = ['task', 'description', 'perfect', 'deadline']
    template_name = 'todolist/task_form.html'

    def test_func(self):
        return self.request.user.is_teacher

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
        
        # Filter out users who are None
        users = [user for user in users if user is not None]

        # Check if there are any users related to the subject code
        if users:
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






class TaskUpdate( UserPassesTestMixin, UpdateView):
    model = ToDoList
    fields = ['Subject_Code', 'description', 'perfect', 'deadline']
    template_name = 'todolist/taskupdate.html'
    success_url = reverse_lazy('teacher_tasks')

    def test_func(self):
        return self.request.user.is_teacher

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs['pk']  # Pass the 'pk' from URL kwargs to the template
        return context
    
    def form_valid(self, form):
        # Get the task being updated
        task = form.instance
        # Get all tasks with the same name
        tasks_to_update = ToDoList.objects.filter(task=task.task)
        # Update all tasks with the same name
        for task_to_update in tasks_to_update:
            task_to_update.Subject_Code = task.Subject_Code
            task_to_update.description = task.description
            task_to_update.deadline = task.deadline
            task_to_update.perfect = task.perfect
            task_to_update.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        # Retrieve subject PK from the session
        subject_pk = self.request.session.get('subject_pk')
        return reverse_lazy('viewtasks', kwargs={'pk': subject_pk})
    

class DeleteTask(UserPassesTestMixin, DeleteView):
    model = ToDoList
    context_object_name = 'data'
    template_name = 'todolist/task_delete.html'
    success_url = reverse_lazy('viewgrades')

    def test_func(self):
        return self.request.user.is_teacher

    def post(self, request, *args, **kwargs):
        # Get the task object
        task = get_object_or_404(ToDoList, pk=self.kwargs['pk'])
        # Retrieve the subject code and task name
        subject = task.Subject_Code
        task_name = task.task
        # Delete all tasks with the same name as the selected task within the subject
        tasks_to_delete = ToDoList.objects.filter(Subject_Code=subject, task=task_name)
        tasks_to_delete.delete()
        return JsonResponse({'message': 'Tasks deleted successfully'})

    def get_success_url(self):
        # Retrieve subject PK from the session
        subject_pk = self.request.session.get('subject_pk')
        return reverse_lazy('viewtasks', kwargs={'pk': subject_pk})
    
# class DeleteTask (UserPassesTestMixin,  DeleteView):
#     model = ToDoList
#     context_object_name = 'data'
#     success_url = reverse_lazy('viewgrades')

#     def test_func(self):
#         return self.request.user.is_teacher

#     def get_object(self, queryset=None):
#         # Return the task object based on the provided task ID
#         return self.model.objects.get(pk=self.kwargs['pk'])

#     def post(self, request, *args, **kwargs):
#         # Check if the "Confirm Delete" button is clicked
#         if "confirm_delete" in request.POST:
#             # Proceed with the deletion
#             return self.confirm_delete(request, *args, **kwargs)
#         # If cancellation is requested, redirect back to the detail view
#         return HttpResponseRedirect(self.request.path)

#     def confirm_delete(self, request, *args, **kwargs):
#         # Retrieve the task object
#         task = self.get_object()
#         subject = task.Subject_Code
#         task_name = task.task
#         # Delete all tasks with the same name as the selected task within the subject
#         tasks_to_delete = ToDoList.objects.filter(Subject_Code=subject, task=task_name)
#         tasks_to_delete.delete()
#         # Redirect to the success URL
#         return HttpResponseRedirect(self.get_success_url())

#     def get_success_url(self):
#         # Retrieve subject PK from the session
#         subject_pk = self.request.session.get('subject_pk')
#         return reverse_lazy('viewtasks', kwargs={'pk': subject_pk})

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['pk'] = self.kwargs['pk']  # Pass subject_pk to the context
#         return context
    
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






class ClassCreate(LoginRequiredMixin,  UserPassesTestMixin, CreateView):
    model = Subjects
    context_object_name = 'class'
    fields = '__all__'
    template_name = 'todolist/CreateClass.html'
    success_url = reverse_lazy('dashboard')

    def test_func(self):
        return self.request.user.is_teacher

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
    
class CreateSchedule(LoginRequiredMixin,  UserPassesTestMixin, CreateView):
    model = SubjectSchedule
    fields = ['day_of_week', 'start_time', 'end_time']
    template_name = 'todolist/CreateSchedule.html'
    success_url = reverse_lazy('dashboard')

    def test_func(self):
        return self.request.user.is_teacher
    
    def get(self, request, *args, **kwargs):
        # Store subject PK in session
        subject_pk = self.kwargs['pk']
        request.session['subject_pk'] = subject_pk
        print("Stored subject PK in session:", subject_pk)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        # Retrieve the subject from the session
        subject_pk = self.request.session.get('subject_pk')
        subject = Subjects.objects.get(pk=subject_pk)

        # Associate the subject with the schedule
        form.instance.subject = subject

        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subject_pk'] = self.kwargs['pk']
        return context
    
class ClassView( UserPassesTestMixin, ListView):
    model = Subjects
    context_object_name = 'class'
    template_name = 'todolist/ClassView.html'

    def test_func(self):
        return self.request.user.is_teacher
    

    def get_queryset(self):
        return Subjects.objects.all()


class ClassDetails(LoginRequiredMixin,  UserPassesTestMixin, DetailView):
    model = Subjects
    context_object_name = 'subject'  # Change context_object_name to match what you're using in the template
    template_name = 'todolist/ClassDetails.html'

    def test_func(self):
        return self.request.user.is_teacher

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

    def test_func(self):
        return self.request.user.is_teacher
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        users_queryset = CustomUser.objects.filter(is_student=True)
        form.fields['users'] = forms.ModelMultipleChoiceField(
            queryset=users_queryset,
            widget=forms.CheckboxSelectMultiple,
            required=False
        )
        return form

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
    

class DeleteClass(LoginRequiredMixin,  UserPassesTestMixin, DeleteView):

    model = Subjects
    context_object_name = 'subject'
    template_name = 'todolist/class_delete.html'
    success_url = reverse_lazy('dashboard')

    def test_func(self):
        return self.request.user.is_teacher

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs.get('pk')
        return context

    

    def get_success_url(self):
        # Retrieve subject PK from session
        subject_pk = self.request.session.get('subject_pk')
        print("Retrieved subject PK from session:", subject_pk)
        return reverse_lazy('dashboard')
    



    
class ViewTasks( UserPassesTestMixin, DetailView):
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
    
class ViewGrades( UserPassesTestMixin, DetailView):
    model = Subjects
    context_object_name = 'subject'
    template_name = 'Grades/viewgradestrial.html'

    def test_func(self):
        return self.request.user.is_teacher  # Ensures only teachers can access this view
    

    def get(self, request, *args, **kwargs):
        # Store subject PK in session
        subject_pk = self.kwargs['pk']
        request.session['subject_pk'] = subject_pk
        print("Stored subject PK in session:", subject_pk)
        return super().get(request, *args, **kwargs)
    

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
    

class UpdateScore(UserPassesTestMixin, ListView):
    model = ToDoList
    context_object_name = 'tasks'
    template_name = 'Grades/UpdateScore.html'

    def test_func(self):
        return self.request.user.is_teacher
    

    def get_queryset(self):
        # Retrieve the task name from URL parameters
        task_name = self.kwargs.get('task_name')
        if task_name:
            # Filter tasks based on the task name
            return ToDoList.objects.filter(task=task_name)
        else:
            # If task name is not available, return an empty queryset
            return ToDoList.objects.none()
        

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass the task name to the template
        context['task_name'] = self.kwargs.get('task_name')
        
        # Filter students associated with the task and remove None values
        task_name = self.kwargs.get('task_name')
        if task_name:
            # Assuming ToDoList has a ForeignKey field 'user' to the user model
            students = ToDoList.objects.filter(task=task_name).values_list('user', flat=True).distinct().exclude(user=None)
            print(students)
            context['students'] = students
        
        return context
        
class Scoring(LoginRequiredMixin, UpdateView):
    model = ToDoList
    fields = ['score', 'status']
    template_name = 'Grades/Scoring.html'
    
    def get_success_url(self):
    # Assuming you have access to the task name through the ToDoList model
        task_name = self.object.task
        return reverse_lazy('scoreupdate', kwargs={'task_name': task_name})
    
class UserScheduleView(View):
    template_name = 'todolist/ViewSchedule.html'
    context_object_name = 'subject'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user_subjects = Subjects.objects.filter(users=request.user)
            schedule = {}
            times = ['07:00 AM', '07:30 AM', '08:00 AM', '08:30 AM', '09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM',
                    '11:00 AM', '11:30 AM', '12:00 PM', '12:30 PM', '01:00 PM', '01:30 PM', '02:00 PM', '02:30 PM',
                    '03:00 PM', '03:30 PM', '04:00 PM', '04:30 PM', '05:00 PM', '05:30 PM', '06:00 PM', '06:30 PM',
                    '07:00 PM', '07:30 PM', '08:00 PM', '08:30 PM', '09:00 PM', '09:30 PM', '10:00 PM']

            # Convert time strings to datetime objects
            time_objects = [datetime.strptime(time_str, '%I:%M %p') for time_str in times]

            # Convert datetime objects to military time format
            military_times = [time_obj.strftime('%H:%M') for time_obj in time_objects]

            print(military_times)

            print("Data type of times:", type(military_times))
            for day in range(1, 7):
                schedule[day] = []

            for subject in user_subjects:
                subject_schedules = SubjectSchedule.objects.filter(subject=subject)
                for subject_schedule in subject_schedules:
                    formatted_start_time = subject_schedule.start_time.strftime('%I:%M %p')
                    formatted_end_time = subject_schedule.end_time.strftime('%I:%M %p')
                    
                    # Convert start and end times to datetime objects
                    start_time_obj = datetime.combine(datetime.today(), subject_schedule.start_time)
                    end_time_obj = datetime.combine(datetime.today(), subject_schedule.end_time)
                    
                    # Convert start and end times to military time format
                    military_start_time = start_time_obj.strftime('%H:%M')
                    military_end_time = end_time_obj.strftime('%H:%M')
                    
                    duration = end_time_obj - start_time_obj
                    duration_in_minutes = duration.total_seconds() / 60
                    duration_in_intervals = duration_in_minutes // 30
                    schedule[subject_schedule.day_of_week].append({
                        'subject': subject.Subject_Name,
                        'start_time': military_start_time,
                        'end_time': military_end_time,
                        'duration': duration_in_intervals  # Pass duration in intervals to template
                    })

            return render(request, self.template_name, {'schedule': schedule, 'times': military_times, 'user_subjects': user_subjects, 'user': request.user,})
        else:
            return redirect('login')



    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     # Get the specific task object
    #     task = self.get_object()
    #     # Get all students associated with the task
    #     students = task.users.all()
    #     # Prepare data for rendering in the template
    #     context['task'] = task
    #     context['students'] = students
    #     return context
    

    # class UpdateScore(UserPassesTestMixin, ListView):
#     model = ToDoList
#     context_object_name = 'tasks'
#     fields = ['score']  # Fields to be displayed in the form
#     template_name = 'Grades/UpdateScore.html'  # Replace 'your_template_name.html' with your actual template name
#     success_url = reverse_lazy('viewgrades')

#     def test_func(self):
#         return self.request.user.is_teacher

#     def get_queryset(self):
#         # Assuming you have a subject code stored in the session or passed through URL parameters
#         subject_code = self.request.session.get('subject_code')  # Change 'subject_code' to your actual session key
#         if subject_code:
#             # Filter tasks based on the subject code
#             return ToDoList.objects.filter(subject_code=subject_code)
#         else:
#             # If subject code is not available, return an empty queryset
#             return ToDoList.objects.none()
    

    

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