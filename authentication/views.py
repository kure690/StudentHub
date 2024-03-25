from django.http import HttpResponse
from .models import CustomUser
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from StudentHub import settings
from django.core.mail import send_mail
from django.contrib.auth.views import PasswordResetView
from django.db import IntegrityError
from django.contrib.auth.forms import PasswordResetForm



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
            message ="Hello " + myuser.first_name + " and Welcome to Student Hub!"
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
            fname = user.first_name
            return render(request, "studentdashboard/dashboard.html", {'fname': fname})

        else:
            messages.error(request, "Bad Credentials")
            return redirect('signin')


    return render(request, "authentication/signin.html")

def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!")
    return redirect('home')


def dashboard(request):
    user = request.user
    enrolled_subjects = ["Math", "English", "Science"]  # Replace with actual enrolled subjects data

    return render(request, "studentdashboard/dashboard.html", {'user': user, 'enrolled_subjects': enrolled_subjects})

def passreset_view(request):
    if request.method == "POST":
        # Check if the email has already been submitted for password reset
        if 'email_submitted' in request.session:
            # Email has already been submitted, show a message or redirect
            messages.info(request, 'Password reset email has already been sent.')
            return redirect('password_reset_done')

        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            # Send password reset email
            send_password_reset_email(email)
            # Mark email as submitted in session to prevent re-submission
            request.session['email_submitted'] = True
            return redirect('password_reset_done')
    else:
        form = PasswordResetForm()
    return render(request, 'authentication/forgetpass.html', {'form': form})

def send_password_reset_email(email):
    # Implement your logic to send the password reset email here
    # You can use Django's send_mail function or any other email sending library
    subject = 'Password Reset Request'
    message = 'Please follow the link to reset your password.'
    from_email = settings.EMAIL_HOST_USER
    send_mail(subject, message, from_email, [email])

#def passresetdone(request):
    
def changepass(request):
    return render (request, '')


    

     


#     # #Welcome Email
#     # subject ="Welcome to StudentHub!!"
#     # message ="Hello and Welcome to Student Hub!"
#     # from_email = settings.EMAIL_HOST_USER
#     # to_list = [CustomUser.email]
#     # send_mail(subject, message, from_email, to_list, fail_silently=False)


#     # Your logic here

