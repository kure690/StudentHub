from django.http import HttpResponse
from .models import CustomUser
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.shortcuts import redirect, render
from StudentHub import settings
from django.core.mail import send_mail
from django.contrib.auth.views import PasswordResetView
from django.db import IntegrityError
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.http import HttpRequest
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import Http404
from ToDoList.views import ToDo, ClassView



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

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose a different username.")
            return redirect('signup')
        
        if CustomUser.objects.filter(email = email).exists():
            messages.error(request, "This email address is already in use")
            return redirect('signup')
        

        try:
            myuser = CustomUser.objects.create_user(username=username, email=email, password=password1)
            myuser.first_name = fname
            myuser.last_name =lname

            if role == 'student':
                myuser.is_student = True
                myuser.is_teacher = False
            elif role == 'teacher':
                myuser.is_student = False
                myuser.is_teacher = True

            myuser.save()

            messages.success(request, "Your Account has been successfully created.")

            #Welcome Email
            subject ="Welcome to StudentHub!!"
            message ="Hello " + myuser.first_name + myuser.last_name + " and Welcome to Student Hub!"
            from_email = settings.EMAIL_HOST_USER
            to_list = [myuser.email]
            send_mail(subject, message, from_email, to_list, fail_silently=False)
        
            return redirect('signin')
        except IntegrityError:
            messages.error(request, "An error occurred while creating your account. Please try again later.")
            return redirect('signup')
    


    return render(request, "authentication/signup.html")

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

@login_required
def dashboard(request):
    role = 'teacher' if request.user.is_teacher else 'student'
    todo_view = ToDo()
    tasks = todo_view.get_queryset().filter(user=request.user)
    class_view = ClassView()
    subject = class_view.get_queryset()
    print(subject)
    print
    username = request.user.username
    id = request.user.id
    pk = request.user.pk
    if role == 'teacher':
        return render(request, "teacherdashboard/dashboard.html", {'username': username, 'id': id, 'pk': pk, 'tasks': tasks, 'subjects': subject})
    
    elif role == 'student':
        return render(request, "studentdashboard/dashboard.html", {'username': username, 'id': id, 'pk': pk, 'tasks': tasks})

class InfoUpdate(LoginRequiredMixin, UpdateView):
    model = CustomUser
    fields = ['first_name', 'last_name', 'email']
    template_name = 'authentication/editprofile.html'
    success_url = reverse_lazy('dashboard')

    def get_object(self, queryset=None):
        # Get the object being edited
        obj = super().get_object(queryset)

        # Check if the current user is the owner of the profile being edited
        if obj != self.request.user:
            raise Http404("You are not allowed to access this page.")
        
        return obj

@login_required
def Change_Password(request):
    if request.method=='POST':
        form = PasswordChangeForm(user=request.user,data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request,form.user)
            messages.success(request, 'Your password has been successfully changed.')
            return redirect('dashboard')
    else:
        form = PasswordChangeForm(user=request.user)
    pk=request.user.pk
    return render(request, 'authentication/changepass.html', {'form': form, 'pk': pk})
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

