from django.http import HttpResponse
from django.contrib.auth.models import User
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

        myuser = User.objects.create_user(username, email, password1)
        myuser.first_name = fname
        myuser.last_name =lname

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
            return render(request, "dashboard/dashboard.html", {'fname': fname})

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

    return render(request, "dashboard/dashboard.html", {'user': user, 'enrolled_subjects': enrolled_subjects})