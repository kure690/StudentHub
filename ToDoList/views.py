from datetime import datetime, timedelta
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import SubjectSchedule, ToDoList, Subjects, Notification
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
from django.db.models import Q, F, Sum, Count
from django.dispatch import receiver
from django.utils import timezone
from django.db.models.signals import post_save

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
            context['tasks'] = context['tasks'].filter(
                Q(Subject_Code__Subject_Name__icontains=search_input) |
                Q(Subject_Code__Subject_Code__icontains=search_input)
            )

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

class TaskCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = ToDoList
    fields = ['task', 'description', 'perfect', 'task_type', 'deadline']
    template_name = 'todolist/task_form.html'

    def test_func(self):
        return self.request.user.is_teacher

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        context['pk'] = self.kwargs.get('pk')
        return context

    def form_valid(self, form):
        # Set the Subject_Code for the task
        form.instance.Subject_Code_id = self.kwargs.get('pk')

        # Get the students related to the subject
        subject = form.instance.Subject_Code
        students = subject.students.all()
        print("Students found:", students)

        # Filter out students who are None
        students = [student for student in students if student is not None]

        # Check if there are any students related to the subject
        if students:
            # Create and save a task instance for each student
            for student in students:
                print("Creating task for student:", student)
                task = ToDoList.objects.create(
                    Subject_Code=form.instance.Subject_Code,
                    user=student,
                    task=form.cleaned_data['task'],
                    description=form.cleaned_data['description'],
                    status=False,  # Default status to False
                    deadline=form.cleaned_data['deadline'],
                    perfect=form.cleaned_data['perfect'],
                    task_type=form.cleaned_data['task_type'],
                    assigned_user=student  # Assign the student to the task
                )
                message = f"A new task has been assigned for {subject.Subject_Name}"
                NotificationManager.send_notification(recipients=[student], message=message)
                print("Task created:", task)
            return super().form_valid(form)
        else:
            # No students related to the subject, return an error or handle it accordingly
            print("No students found related to the subject. Cannot create task.")
            return HttpResponse("No students related to the subject. Cannot create task.")

    def get_success_url(self):
        # Get the primary key (pk) of the subject object
        subject_pk = self.kwargs['pk']
        # Generate the success URL with the subject's pk
        success_url = reverse_lazy('class_details', kwargs={'pk': subject_pk})
        return success_url





class TaskUpdate( UserPassesTestMixin, UpdateView):
    model = ToDoList
    fields = ['Subject_Code', 'description', 'perfect', 'task_type', 'deadline']
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
            task_to_update.task_type = task.task_type
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






class ClassCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Subjects
    context_object_name = 'class'
    fields = ['Subject_Name', 'Subject_Code', 'students']  # Update fields to include 'students'
    template_name = 'todolist/CreateClass.html'
    success_url = reverse_lazy('dashboard')

    def test_func(self):
        return self.request.user.is_teacher

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        students_queryset = CustomUser.objects.filter(is_student=True)
        form.fields['students'] = forms.ModelMultipleChoiceField(
            queryset=students_queryset,
            widget=forms.CheckboxSelectMultiple,
            required=False
        )
        return form

    def form_valid(self, form):
        # Set the teacher for the subject
        form.instance.teacher = self.request.user

        # Save the form instance
        response = super().form_valid(form)

        # Add selected students to the subject
        students = form.cleaned_data['students']
        self.object.students.set(students)

        for student in students:
            message = f"You have been added to the class '{self.object.Subject_Name}' with subject code '{self.object.Subject_Code}'."
            NotificationManager.send_notification(recipients=[student], message=message)
        

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
    
    def get_success_url(self):
        # Get the primary key (pk) of the subject object
        subject_pk = self.kwargs['pk']
        # Generate the success URL with the subject's pk
        success_url = reverse_lazy('class_details', kwargs={'pk': subject_pk})
        return success_url

    
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

        subject_schedules = SubjectSchedule.objects.filter(subject=subject)

        context['tasks'] = unique_tasks.values()
        context['subject_schedules'] = subject_schedules
        return context
    
class AddStudent(LoginRequiredMixin, UpdateView):
    model = Subjects
    fields = []  # Remove 'users' from the fields list
    template_name = 'todolist/ClassAdd.html'

    def test_func(self):
        return self.request.user.is_teacher

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        students_queryset = CustomUser.objects.filter(is_student=True)
        form.fields['students'] = forms.ModelMultipleChoiceField(
            queryset=students_queryset,
            widget=forms.CheckboxSelectMultiple,
            required=False
        )
        form.fields['students'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name}"
        return form

    def get_success_url(self):
        subject_pk = self.kwargs['pk']
        success_url = reverse_lazy('class_details', kwargs={'pk': subject_pk})
        return success_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs.get('pk')
        return context

    def form_valid(self, form):
        subject = self.get_object()
        students = form.cleaned_data.get('students')
        subject.students.set(students)

        # Send notification to each added student
        for student in students:
            message = f"You have been added to the class '{subject.Subject_Name}' with subject code '{subject.Subject_Code}'"
            NotificationManager.send_notification(recipients=[student], message=message)

        return super().form_valid(form)
    

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
    
class ViewGrades(UserPassesTestMixin, DetailView):
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
        students = subject.students.all()  # Get all students enrolled in the subject

        # Fetch all tasks related to the subject code
        all_tasks = ToDoList.objects.filter(Subject_Code=subject)

        # Extract unique tasks
        unique_tasks = []
        seen_tasks = set()
        for task in all_tasks:
            if task.task not in seen_tasks:
                unique_tasks.append(task)
                seen_tasks.add(task.task)

        num_students = len(students)
        student_scores = []

        for student in students:
            student_data = {'student': student, 'scores': []}
            total_score = 0
            total_possible_score = 0

            for task in unique_tasks:
                # Retrieve task assigned to the student
                assigned_task = all_tasks.filter(task=task.task, assigned_user=student).first()

                # If task is assigned to the student and completed, retrieve score
                if assigned_task and assigned_task.status:
                    score = assigned_task.score
                    total_score += score
                    total_possible_score += task.perfect
                else:
                    score = 0

                student_data['scores'].append({'task': task, 'score': score})

            # Calculate the average grade for the student
            average_grade = (total_score / total_possible_score) * 100 if total_possible_score > 0 else 0
            student_data['average_grade'] = round(average_grade, 2)
            student_scores.append(student_data)

        def calculate_class_average():
            total_student_average = 0
            for student_data in student_scores:
                total_student_average += student_data['average_grade']
            class_average = total_student_average / len(student_scores) if len(student_scores) > 0 else 0
            return round(class_average, 2)

        class_average_grade = calculate_class_average()

        context['students'] = students
        context['tasks'] = unique_tasks
        context['student_scores'] = student_scores
        context['num_students'] = num_students
        context['class_average_grade'] = class_average_grade

        return context

class UpdateScoreForm(forms.Form):
    task_id = forms.IntegerField(widget=forms.HiddenInput())
    score = forms.IntegerField()
    status = forms.BooleanField(required=False)

class UpdateScore(UserPassesTestMixin, ListView):
    model = ToDoList
    context_object_name = 'tasks'
    template_name = 'Grades/UpdateScore.html'

    def test_func(self):
        return self.request.user.is_teacher

    def get_queryset(self):
        task_name = self.kwargs.get('task_name')
        if task_name:
            return ToDoList.objects.filter(task=task_name)
        else:
            return ToDoList.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_name'] = self.kwargs.get('task_name')
        subject_pk = self.request.session.get('subject_pk')  # Retrieve subject_pk from session
        print("Stored subject PK in session:", subject_pk)
        context['subject_pk'] = subject_pk
        return context

    def post(self, request, *args, **kwargs):
        form = UpdateScoreForm(request.POST)
        if form.is_valid():
            task_id = form.cleaned_data['task_id']
            score = form.cleaned_data['score']
            status = form.cleaned_data['status']
            task = ToDoList.objects.get(id=task_id)
            task.score = score
            task.status = status
            task.save()

            student = task.assigned_user
            message = f"Your score for the task '{task.task}' has been updated. You received a score of {task.score} out of {task.perfect}."
            NotificationManager.send_notification(recipients=[student], message=message)
        return redirect('scoreupdate', task_name=self.kwargs.get('task_name'))
    

        
class Scoring(LoginRequiredMixin, UpdateView):
    model = ToDoList
    fields = ['score', 'status']
    template_name = 'Grades/Scoring.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        task = self.object
        task_name = task.task
        student = task.assigned_user

        # Send notification to the student assigned to the task
        message = f"Your task '{task_name}' has been graded. You received a score of {task.score} out of {task.perfect}."
        NotificationManager.send_notification(recipients=[student], message=message)

        return redirect('scoreupdate', task_name=task_name)
    
class UserScheduleView(View):
    template_name = 'todolist/ViewSchedule.html'
    context_object_name = 'subject'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user_subjects = request.user.enrolled_subjects.all()
            schedule = {}
            times = ['07:00 AM', '07:30 AM', '08:00 AM', '08:30 AM', '09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM',
                     '11:00 AM', '11:30 AM', '12:00 PM', '12:30 PM', '01:00 PM', '01:30 PM', '02:00 PM', '02:30 PM',
                     '03:00 PM', '03:30 PM', '04:00 PM', '04:30 PM', '05:00 PM', '05:30 PM', '06:00 PM', '06:30 PM',
                     '07:00 PM', '07:30 PM', '08:00 PM', '08:30 PM', '09:00 PM', '09:30 PM', '10:00 PM']

            days = range(1, 7)
            for day in days:
                schedule[day] = []

            # Creating a nested dictionary to store subjects and their duration
            day_to_time_subject = {day: {time: None for time in times} for day in days}

            for subject in user_subjects:
                subject_schedules = subject.subjectschedule_set.all()
                for subject_schedule in subject_schedules:
                    start_time = subject_schedule.start_time.strftime('%I:%M %p')
                    end_time = subject_schedule.end_time.strftime('%I:%M %p')

                    start_time_obj = datetime.combine(datetime.today(), subject_schedule.start_time)
                    end_time_obj = datetime.combine(datetime.today(), subject_schedule.end_time)
                    duration = (end_time_obj - start_time_obj).seconds // 1800  # Duration in 30 min intervals

                    for i in range(duration):
                        current_time = (start_time_obj + timedelta(minutes=30 * i)).strftime('%I:%M %p')
                        if i == 0:
                            day_to_time_subject[subject_schedule.day_of_week][current_time] = {
                                'name': subject.Subject_Name,
                                'duration': duration,
                                'merged': False
                            }
                        else:
                            day_to_time_subject[subject_schedule.day_of_week][current_time] = {
                                'name': subject.Subject_Name,
                                'duration': 0,
                                'merged': True
                            }

            return render(request, self.template_name, {
                'schedule': {'day_to_time_subject': day_to_time_subject},
                'times': times,
                'user_subjects': user_subjects,
                'user': request.user,
                'days': days,
            })
        else:
            return redirect('login')
        

class StudentGrades(ListView):
    model = ToDoList
    context_object_name = 'tasks'
    template_name = 'Grades/StudentGrades.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(assigned_user=self.request.user)
        search_input = self.request.GET.get('search area') or ''
        if search_input:
            context['tasks'] = context['tasks'].filter(Subject_Code__Subject_Code__icontains=search_input)
        context['search_input'] = search_input

        completed_tasks_count = context['tasks'].filter(status=True).count()
        context['completed_tasks_count'] = completed_tasks_count

        # Calculate average grade and completed tasks count for each subject
        subject_grades = []
        for subject in self.request.user.enrolled_subjects.all():
            completed_tasks = ToDoList.objects.filter(assigned_user=self.request.user, Subject_Code=subject, status=True)
            
            total_score = completed_tasks.aggregate(total_score=Sum('score'))['total_score'] or 0
            total_possible_score = completed_tasks.aggregate(total_possible_score=Sum('perfect'))['total_possible_score'] or 0
            
            average_grade = (total_score / total_possible_score) * 100 if total_possible_score > 0 else 0
            subject_data = {
                'subject_code': subject.Subject_Code,
                'subject_name': subject.Subject_Name,
                'average_grade': round(average_grade, 2),
                'completed_tasks_count': completed_tasks.count(),
            }
            subject_grades.append(subject_data)

        context['subject_grades'] = subject_grades

        # Calculate overall average grade for the student
        total_student_average = 0
        subject_count = 0

        for subject_data in subject_grades:
            if subject_data['average_grade'] > 0:
                total_student_average += subject_data['average_grade']
                subject_count += 1

        if subject_count > 0:
            student_average = total_student_average / subject_count
            context['student_average'] = round(student_average, 2)
        else:
            context['student_average'] = 0

        return context
    
class NotificationManager:
    @staticmethod
    def send_notification(recipients, message):
        notification = Notification.objects.create(message=message)
        notification.recipients.set(recipients)

    @staticmethod
    def get_notifications_for_user(user):
        """
        Get all notifications for a specific user.
        Args:
            user (User): The User object representing the user.
        Returns:
            QuerySet: A queryset of Notification objects for the user.
        """
        return Notification.objects.filter(recipients=user).order_by('-timestamp')

    # @staticmethod
    # def mark_as_read(notification):
    #     """
    #     Mark a notification as read.
    #     Args:
    #         notification (Notification): The Notification object to mark as read.
    #     """
    #     notification.is_read = True
    #     notification.save()

    # @staticmethod
    # def mark_all_as_read(user):
    #     """
    #     Mark all notifications for a user as read.
    #     Args:
    #         user (User): The User object representing the user.
    #     """
    #     Notification.objects.filter(recipients=user).update(is_read=True)


@receiver(post_save, sender=ToDoList)
def send_task_reminder(sender, instance, created, **kwargs):
    if created:
        # Get the current date and time
        current_date = timezone.now().date()

        # Calculate the date one day before the task's deadline
        reminder_date = instance.deadline - timedelta(days=1)

        # Check if the reminder date is equal to or greater than the current date
        if reminder_date >= current_date:
            # Send a reminder notification to the student one day before the deadline
            student = instance.assigned_user
            message = f"Reminder: The deadline for the task '{instance.task}' is tomorrow ({instance.deadline})."
            NotificationManager.send_notification(recipients=[student], message=message)
    



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