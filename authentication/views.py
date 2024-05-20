from .models import CustomUser, DEPARTMENT_CHOICES
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.shortcuts import redirect, render
from StudentHub import settings
from django.core.mail import send_mail
from django.db import IntegrityError
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from django.http import Http404, JsonResponse
from ToDoList.views import ToDo, ClassView
from django.utils.safestring import mark_safe
import calendar
from calendar import HTMLCalendar
from datetime import datetime, date
from django.db.models import Sum
from ToDoList.models import Notification, ToDoList
from django import forms



# Create your views here.
def home(request):
    return render(request, "authentication/index.html")

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        role = request.POST.get('role')
        department = request.POST.get('department')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose a different username.")
            return redirect('signup')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "This email address is already in use")
            return redirect('signup')

        try:
            myuser = CustomUser.objects.create_user(username=username, email=email, password=password1)
            myuser.first_name = fname
            myuser.last_name = lname
            if role == 'student':
                myuser.is_student = True
                myuser.is_teacher = False
                myuser.department = department  # Set the department for the student
            elif role == 'teacher':
                myuser.is_student = False
                myuser.is_teacher = True
            myuser.save()
            messages.success(request, "Your Account has been successfully created.")

            # Welcome Email
            subject = "Welcome to StudentHub!!"
            message = f"Hello {myuser.first_name} {myuser.last_name} and Welcome to Student Hub!"
            from_email = settings.EMAIL_HOST_USER
            to_list = [myuser.email]
            send_mail(subject, message, from_email, to_list, fail_silently=False)

            return redirect('signin')
        except IntegrityError:
            messages.error(request, "An error occurred while creating your account. Please try again later.")
            return redirect('signup')

    departments = DEPARTMENT_CHOICES
    return render(request, "authentication/signup.html", {'department_choices': departments})

def signin(request):

    if request.method == "POST":
        username = request.POST['username']
        password1 = request.POST['password1']

        user = authenticate(username=username, password=password1)

        if user is not None:
            login(request, user)

            return redirect('dashboard')

        else:
            messages.error(request, "Bad Credentials")
            return redirect('signin')


    return render(request, "authentication/signin.html")

def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!")
    return redirect('home')

class HighlightedHTMLCalendar(HTMLCalendar):
    def __init__(self, year, month, pending_task_deadlines=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.year = year
        self.month = month
        self.today = date.today()
        self.pending_task_deadlines = pending_task_deadlines or []

    def formatday(self, day, weekday):
        if day == 0:
            return '<td class="noday">&nbsp;</td>'  # Day outside month
        else:
            if day in self.pending_task_deadlines:
                return f'<td class="pending-deadline">{day}</td>'  # Highlight pending task deadline
            elif day == self.today.day and self.month == self.today.month and self.year == self.today.year:
                return f'<td class="today">{day}</td>'  # Highlight current day
            else:
                return f'<td>{day}</td>'
            

@login_required
def dashboard(request):
    role = 'teacher' if request.user.is_teacher else 'student'
    todo_view = ToDo()
    tasks = todo_view.get_queryset().filter(assigned_user=request.user)

    if role == 'teacher':
        taught_subjects = request.user.taught_subjects.all()

        for subject in taught_subjects:
            students = subject.students.all()
            all_tasks = ToDoList.objects.filter(Subject_Code=subject)

            total_student_average = 0
            for student in students:
                total_score = 0
                total_possible_score = 0
                for task in all_tasks:
                    assigned_task = ToDoList.objects.filter(task=task.task, assigned_user=student).first()
                    if assigned_task and assigned_task.status:
                        total_score += assigned_task.score
                        total_possible_score += task.perfect
                
                average_grade = (total_score / total_possible_score) * 100 if total_possible_score > 0 else 0
                total_student_average += average_grade

            class_average = total_student_average / len(students) if len(students) > 0 else 0
            subject.class_average = round(class_average, 2)

        return render(request, "teacherdashboard/dashboard.html", {
            'username': request.user.username,
            'id': request.user.id,
            'pk': request.user.pk,
            'tasks': tasks,
            'subjects': taught_subjects
        })
    
    elif role == 'student':
        enrolled_subjects = request.user.enrolled_subjects.all()
        
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        pending_task_deadlines = [task.deadline.day for task in tasks if not task.status 
                                and task.deadline.month == current_month 
                                and task.deadline.year == current_year]
        
        cal = HighlightedHTMLCalendar(current_year, current_month, pending_task_deadlines).formatmonth(current_year, current_month)
        
        completed_tasks = tasks.filter(status=True)
        total_quiz_score = completed_tasks.filter(task_type='quiz').aggregate(Sum('score'))['score__sum'] or 0
        total_quiz_perfect = completed_tasks.filter(task_type='quiz').aggregate(Sum('perfect'))['perfect__sum'] or 0
        total_activity_score = completed_tasks.filter(task_type='activity').aggregate(Sum('score'))['score__sum'] or 0
        total_activity_perfect = completed_tasks.filter(task_type='activity').aggregate(Sum('perfect'))['perfect__sum'] or 0
        total_perfect_scores = 0
        for task in tasks:
            if task.task_type == 'quiz' and task.score == task.perfect:
                total_perfect_scores += 1
            elif task.task_type == 'activi  ty' and task.score == task.perfect:
                total_perfect_scores += 1

        total_high_scores = 0
        for task in tasks:
            if task.task_type == 'quiz' and task.score >= task.perfect * 0.8:
                total_high_scores += 1
            elif task.task_type == 'activity' and task.score >= task.perfect * 0.8:
                total_high_scores += 1

        total_low_scores = 0
        for task in completed_tasks:
            if task.task_type == 'quiz' and task.score < task.perfect * 0.6:
                total_low_scores += 1
            elif task.task_type == 'activity' and task.score < task.perfect * 0.6:
                total_low_scores += 1

        quiz_percentage = (total_quiz_score / total_quiz_perfect) * 100 if total_quiz_perfect > 0 else 0
        activity_percentage = (total_activity_score / total_activity_perfect) * 100 if total_activity_perfect > 0 else 0
        
        weighted_quiz_score = quiz_percentage * 0.6
        weighted_activity_score = activity_percentage * 0.4
        final_grade_percentage = round(weighted_quiz_score + weighted_activity_score, 2)
        
        if final_grade_percentage >= 90:
            final_grade = 5
        elif final_grade_percentage >= 80:
            final_grade = 4
        elif final_grade_percentage >= 70:
            final_grade = 3
        elif final_grade_percentage >= 60:
            final_grade = 2
        else:
            final_grade = 1

        notifications = Notification.objects.filter(recipients=request.user).order_by('-timestamp')
        
        return render(request, "studentdashboard/dashboard.html", {
            'username': request.user.username, 'id': request.user.id, 'pk': request.user.pk,
            'tasks': tasks, 'subjects': enrolled_subjects, 'calendar': mark_safe(cal),
            'quiz_count': tasks.filter(task_type='quiz').count(),
            'activity_count': tasks.filter(task_type='activity').count(),
            'final_grade_percentage': final_grade_percentage,
            'final_grade': final_grade, 'total_perfect_scores': total_perfect_scores,
            'total_high_scores': total_high_scores, 'total_low_scores': total_low_scores,
            'completed_task': tasks.filter(status=True).count(),
            'notifications': notifications,
            'calendar': cal,
        })
    
@login_required
def delete_notification(request, notification_id):
    if request.method == 'POST':
        try:
            notification = Notification.objects.get(id=notification_id, recipients=request.user)
            notification.delete()
        except Notification.DoesNotExist:
            pass
    return redirect('dashboard')
        
        
        
        


    # def calendar(request):
    #     now = datetime.now
    #     current_year = now.year
    #     current_month = now.month
    #     month_number = list(calendar.month_name).index(current_month)
    #     cal = HTMLCalendar().formatmonth(current_year, month_number)


class InfoUpdate(LoginRequiredMixin, UpdateView):
    model = CustomUser
    fields = ['first_name', 'last_name', 'email', 'profile_picture']
    template_name = 'authentication/editprofile.html'

    def get_success_url(self):
        return reverse_lazy('editprofile', kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        # Get the object being edited
        obj = super().get_object(queryset)
        # Check if the current user is the owner of the profile being edited
        if obj != self.request.user:
            raise Http404("You are not allowed to access this page.")
        return obj

    def form_valid(self, form):
        # Save the form and handle the profile picture upload
        response = super().form_valid(form)
        if 'profile_picture' in self.request.FILES:
            form.instance.profile_picture = self.request.FILES['profile_picture']
            form.instance.save()
        return response

@login_required
def Change_Password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been successfully changed.')
            return redirect(get_success_url(request))
        else:
            form = PasswordChangeForm(user=request.user)
            pk = request.user.pk
            return render(request, 'authentication/changepass.html', {'form': form, 'pk': pk})
    else:
        form = PasswordChangeForm(user=request.user)
        pk = request.user.pk
        return render(request, 'authentication/changepass.html', {'form': form, 'pk': pk})

def get_success_url(request):
    return reverse_lazy('editprofile', kwargs={'pk': request.user.pk})

























# def passreset_view(request):
#     if request.method == "POST":
#         # Check if the email has already been submitted for password reset
#         if 'email_submitted' in request.session:
#             # Email has already been submitted, show a message or redirect
#             messages.info(request, 'Password reset email has already been sent.')
#             return redirect('changepass')

#         form = PasswordResetForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data['email']
#             # Send password reset email
#             send_password_reset_email(email)
#             # Mark email as submitted in session to prevent re-submission
#             request.session['email_submitted'] = True
#             return redirect('changepass')
#     else:
#         form = PasswordResetForm()
#     return render(request, 'authentication/forgetpass.html', {'form': form})
# def passreset_view(request):
#     if request.method == "POST":
#         form = PasswordResetForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data['email']
#             try:
#                 # Check if a user with this email exists
#                 user = CustomUser.objects.get(email=email)
#                 # Send password reset email
#                 send_password_reset_email(request, email)
#                 # Mark email as submitted in session to prevent re-submission
#                 request.session['email_submitted'] = True
#                 # Redirect to a success page or render a success message
#                 return redirect('resetpass')
#             except CustomUser.DoesNotExist:
#                 # Handle case where no user is found with the provided email
#                 return redirect('resetpass')
#     else:
#         form = PasswordResetForm()
#     return render(request, 'authentication/forgetpass.html', {'form': form})

# def send_password_reset_email(email):
#     user = CustomUser.objects.get(email=email)  # Retrieve the user object

#     # Generate a token for the user
#     token_generator = PasswordResetTokenGenerator()
#     uid = urlsafe_base64_encode(force_bytes(user.pk))  # Use user's primary key directly
#     token = token_generator.make_token(user)

#     # Decode uid to a string
#     uid_str = force_str(urlsafe_base64_decode(uid))

#     # Construct the reset URL with the token
#     #reset_url = reverse('resetpass') + f'?uid={uid_str}&token={token}'
#     reset_url = request.build_absolute_uri(reverse('password_reset_confirm', kwargs={'uidb64': user.pk, 'token': token}))

#     # Email content
#     subject = 'Password Reset Request'
#     message = f'Please follow the link to reset your password: {reset_url}'
#     from_email = settings.EMAIL_HOST_USER

#     # Send email
#     send_mail(subject, message, from_email, [email])
# def send_password_reset_email(request, email):  # Add request as an argument here
#     user = CustomUser.objects.get(email=email)  # Retrieve the user object

#     # Generate a token for the user
#     token = default_token_generator.make_token(user)

#     # Construct the reset URL with the token
#     reset_url = request.build_absolute_uri(reverse('password_reset_confirm', kwargs={'uidb64': user.pk, 'token': token}))

#     # Email content
#     subject = 'Password Reset Request'
#     message = f'Please follow the link to reset your password: {reset_url}'
#     from_email = settings.EMAIL_HOST_USER

#     # Send email
#     send_mail(subject, message, from_email, [email])
# #def passresetdone(request):

# def resetpass(request):
#     return render(request, 'authentication/resetpass.html')


    



#     # Your logic here

