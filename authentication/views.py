from django.http import HttpResponse
from .models import CustomUser
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render


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
        
        return redirect('signin')
    


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
            return redirect('home')


    return render(request, "authentication/signin.html")

def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!")
    return redirect('home')


def dashboard(request):
    user = request.user
    enrolled_subjects = ["Math", "English", "Science"]  # Replace with actual enrolled subjects data

    return render(request, "studentdashboard/dashboard.html", {'user': user, 'enrolled_subjects': enrolled_subjects})