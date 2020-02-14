from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# Create your views here.
def signupuser(request):
    if request.method == 'GET':
        return render(request, 'todo_app/signupuser.html', {'form':UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodos')
            except IntegrityError:
                return render(request, 'todo_app/signupuser.html', {'form':UserCreationForm(), 'error':'That username is already in use, please choose another username.'})
        else:
            return render(request, 'todo_app/signupuser.html', {'form':UserCreationForm(), 'error':'Passwords did not match.'})
@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

def loginuser(request):
    if request.method == 'GET':
        return render(request, 'todo_app/loginuser.html', {'form':AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todo/loginuser.html', {'form':AuthenticationForm(), 'error':'Username and Password do not match. Please try again.'})
        else:
            login(request, user)
            return redirect('currenttodos')

def home(request):
    return render(request, 'todo_app/home.html')

@login_required
def currenttodos(request):
    todos = Todo.objects.filter(user=request.user, date_completed__isnull=True)
    return render(request, 'todo_app/currenttodos.html', {'todos':todos})

@login_required
def completedtodos(request):
    todos = Todo.objects.filter(user=request.user, date_completed__isnull=False).order_by('-date_completed')
    return render(request, 'todo_app/completedtodos.html', {'todos':todos})

@login_required
def createtodo(request):
    if request.method == 'GET':
        return render(request, 'todo_app/createtodo.html', {'form':TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            newTodo = form.save(commit=False)
            newTodo.user = request.user
            newTodo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo_app/createtodo.html', {'form':TodoForm(), 'error':'Bad data'})

@login_required
def viewtodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request, 'todo_app/viewtodo.html', {'todo':todo, 'form':form})
    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo_app/viewtodo.html', {'todo':todo, 'error':'Bad data'})

@login_required
def completetodo(request, todo_pk):
        todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
        if request.method == 'POST':
            todo.date_completed=timezone.now()
            todo.save()
            return redirect('currenttodos')

@login_required
def deletetodo(request, todo_pk):
        todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
        if request.method == 'POST':
            todo.delete()
            return redirect('currenttodos')
