from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import UGProgramme, PGProgramme

# Login view
def login_view(request):
    error_message = None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('programmes')
        else:
            error_message = 'Invalid username or password'
    return render(request, 'login.html', {'error_message': error_message})

# Programme view
def programmes_view(request):
    ug_programmes = UGProgramme.objects.all()
    pg_programmes = PGProgramme.objects.all()
    return render(request, 'programmes.html', {'ug_programmes': ug_programmes, 'pg_programmes': pg_programmes})

# UG Branch view
def ug_branch_view(request, ug_id):
    programme = UGProgramme.objects.get(id=ug_id)
    return render(request, 'branch.html', {'programme': programme})

# PG Branch view
def pg_branch_view(request, pg_id):
    programme = PGProgramme.objects.get(id=pg_id)
    return render(request, 'branch.html', {'programme': programme})
