from django.shortcuts import render
from django.views.generic.list import ListView
from .models import ToDoList

# Create your views here.

class ToDo(ListView):
    model = ToDoList