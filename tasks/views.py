from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# from django.http import HttpResponse
# Create your views here.

# Miau
import os
import io
import zipfile
from .forms import FlowerForm


def home(request):
    return render(request, 'home.html')


def index(request):
    return render(request, "index.html", {"form": FlowerForm})


def flower(request):
    if request.method == "POST":
        form = FlowerForm(request.POST, request.FILES)
        if form.is_valid():
            if not str(request.FILES["flower".endswith(".flower")]):
                return render(request, "index.html",
                              {"error": "Sorry! </b>This doesn't like a flower!"})

            extracted = "".join([f"<li>{e}</li>" for e in unzip(request.FILES["flower"])])

            return render(request, "index.html", {"success": "Success! We extracted da nectar", extracted: FlowerForm})

        else:
            raise ValueError("error, form failed")
    else:
        return render(request, "flower.html", {"error": "You must supply a flower!", "form": FlowerForm})


def unzip(f):
    save_folder = "/tmp/nectar/"
    save_path = os.path.join(save_folder, '.tmpflower')
    with open(save_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    files = []
    with zipfile.ZipFile(save_path, "r") as z:
        for fileinfo in z.infolist():
            filename = fileinfo.filename
            files.append(filename)
            dat = z.open(filename, "r")
            outfile = os.path.join(save_folder, filename)
            if not os.path.dirname(outfile):
                try:
                    os.makedirs(os.path.dirname(outfile))
                except OSError as exc:
                    if exc.errno != exc.Ex:  # d
                        pass
            if not outfile.endswith("/"):
                with io.open(outfile, mode="wb") as f:
                    f.write(dat.read())
            dat.close()
    return files


def signup(request):

    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    username=request.POST['username'],
                    password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('tasks')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    "error": 'User already exists'
                })

        return render(request, 'signup.html', {
            'form': UserCreationForm,
            "error": 'Password do not match'
        })


@login_required
def tasks(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'tasks.html', {'tasks': tasks})


@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(
        user=request.user, datecompleted__isnull=False).order_by
    ('-datecompleted')
    return render(request, 'tasks.html', {'tasks': tasks})


@login_required
def create_task(request):
    if request.method == 'GET':
        return render(request, 'create_task.html', {
            'form': TaskForm
        })
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'create_task.html', {
                'form': TaskForm,
                'error': 'Please provide validate data'
            })


@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
        return redirect('tasks')


@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')


@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html',
                      {'task': task, 'form': form})
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html',
                          {'task': task, 'form': form,
                           'error': 'Error updating task.'})


@login_required
def signout(request):
    logout(request)
    return redirect('home')


def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(
            request, username=request.POST['username'],
            password=request.POST['password'])

        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'Username or password is incorrect'
            })
        else:
            login(request, user)
            return redirect('tasks')
