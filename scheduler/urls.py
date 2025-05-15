from django.urls import path
from . import views

urlpatterns = [
    path('', views.LandingView.as_view(), name='landing'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('test-timetable/', views.TestTimetableView.as_view(), name='test-timetable'),
    path('generate-timetable/', views.GenerateTimetableView.as_view(), name='generate-timetable'),
]
