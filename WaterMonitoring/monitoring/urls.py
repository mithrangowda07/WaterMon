from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # URL for the home page
    path('real_time/', views.real_time, name='real_time'),  # URL for the real_time page
    path('about_proj/', views.about_proj, name='about_proj'),  # URL for the about_proj page
    path('analysis_bill/', views.analysis_bill, name='analysis_bill'),
]
