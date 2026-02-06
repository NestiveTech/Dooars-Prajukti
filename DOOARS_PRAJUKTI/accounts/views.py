from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
# Create your views here.
def login(request):
    return render(request, 'login.html')

def signup(request):
    return render(request, 'register.html')