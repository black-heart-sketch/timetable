from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .engine import generate_timetable
from .models import Teacher, Class, Subject, Availability, PeriodControl

class LandingView(TemplateView):
    template_name = 'landing.html'

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib import messages

class LoginView(TemplateView):
    template_name = 'login.html'

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            return render(request, self.template_name, {'error': 'Invalid username or password.'})

class SignupView(TemplateView):
    template_name = 'signup.html'

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username or not password:
            return render(request, self.template_name, {'error': 'Please fill in all fields.'})
        if User.objects.filter(username=username).exists():
            return render(request, self.template_name, {'error': 'Username already exists.'})
        user = User.objects.create_user(username=username, password=password)
        user.save()
        return redirect('/login/')

class GenerateTimetableView(APIView):
    def post(self, request):
        # Load all data from MongoDB
        teachers = list(Teacher.objects.all().as_pymongo())
        classes = list(Class.objects.all().as_pymongo())
        subjects = list(Subject.objects.all().as_pymongo())
        availabilities = list(Availability.objects.all().as_pymongo())
        period_controls = list(PeriodControl.objects.all().as_pymongo())
        # Call the AI engine
        result = generate_timetable(classes, teachers, subjects, availabilities, period_controls)
        return Response(result, status=status.HTTP_200_OK)

# Frontend test page
from django.views import View
class TestTimetableView(View):
    def get(self, request):
        return render(request, 'scheduler/test_timetable.html')
