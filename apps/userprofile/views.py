from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

from apps.algos.meta import Metadata

from .forms import SignUpForm

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()

            mds = Metadata()
            username = user.username
            age = user.age
            gender = user.gender
            occupation = user.occupation
            
            mds.add(username, age, gender, occupation)

            login(request, user)

            return redirect('frontpage')
    else:
        form = SignUpForm()
    
    return render(request, 'signup.html', {'form' : form})

@login_required
def myaccount(request):
    return render(request, 'myaccount.html')

