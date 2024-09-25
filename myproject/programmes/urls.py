from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('programmes/', views.programmes_view, name='programmes'),
    path('ug/<int:ug_id>/', views.ug_branch_view, name='ug_branch'),
    path('pg/<int:pg_id>/', views.pg_branch_view, name='pg_branch'),
]
