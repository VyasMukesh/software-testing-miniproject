from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.db.models import Q, Count
from .models import Task, Category, Project, Comment
from .forms import TaskForm, CategoryForm, ProjectForm, CommentForm


def home(request):
    """Home page view"""
    if request.user.is_authenticated:
        return redirect('task_list')
    return render(request, 'tasks/home.html')


def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('task_list')
    else:
        form = UserCreationForm()
    return render(request, 'tasks/register.html', {'form': form})


def user_login(request):
    """User login view"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('task_list')
    else:
        form = AuthenticationForm()
    return render(request, 'tasks/login.html', {'form': form})


def user_logout(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def task_list(request):
    """Display all tasks with filtering and searching"""
    tasks = Task.objects.filter(
        Q(created_by=request.user) | Q(assigned_to=request.user)
    ).distinct()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        # Using Django ORM (safe from SQL injection)
        tasks = tasks.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    # Filter by priority
    priority_filter = request.GET.get('priority', '')
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    
    # Filter by category
    category_filter = request.GET.get('category', '')
    if category_filter:
        tasks = tasks.filter(category_id=category_filter)
    
    # Statistics
    stats = {
        'total': tasks.count(),
        'todo': tasks.filter(status='todo').count(),
        'in_progress': tasks.filter(status='in_progress').count(),
        'review': tasks.filter(status='review').count(),
        'done': tasks.filter(status='done').count(),
    }
    
    categories = Category.objects.filter(created_by=request.user)
    
    context = {
        'tasks': tasks,
        'stats': stats,
        'categories': categories,
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
    }
    return render(request, 'tasks/task_list.html', context)


@login_required
def task_create(request):
    """Create a new task"""
    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            messages.success(request, 'Task created successfully!')
            return redirect('task_list')
    else:
        form = TaskForm(user=request.user)
    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'Create'})


@login_required
def task_update(request, pk):
    """Update an existing task"""
    task = get_object_or_404(Task, pk=pk, created_by=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('task_detail', pk=task.pk)
    else:
        form = TaskForm(instance=task, user=request.user)
    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'Update'})


@login_required
def task_delete(request, pk):
    """Delete a task"""
    task = get_object_or_404(Task, pk=pk, created_by=request.user)
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully!')
        return redirect('task_list')
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})


@login_required
def task_detail(request, pk):
    """View task details"""
    task = get_object_or_404(Task, pk=pk)
    comments = task.comments.all()
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.task = task
            comment.user = request.user
            comment.save()
            messages.success(request, 'Comment added!')
            return redirect('task_detail', pk=task.pk)
    else:
        comment_form = CommentForm()
    
    context = {
        'task': task,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'tasks/task_detail.html', context)


@login_required
def category_list(request):
    """List all categories"""
    categories = Category.objects.filter(created_by=request.user).annotate(
        task_count=Count('tasks')
    )
    return render(request, 'tasks/category_list.html', {'categories': categories})


@login_required
def category_create(request):
    """Create a new category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.created_by = request.user
            category.save()
            messages.success(request, 'Category created successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'tasks/category_form.html', {'form': form})


@login_required
def category_delete(request, pk):
    """Delete a category - will test PROTECT constraint"""
    category = get_object_or_404(Category, pk=pk, created_by=request.user)
    if request.method == 'POST':
        try:
            category.delete()
            messages.success(request, 'Category deleted successfully!')
        except Exception as e:
            messages.error(request, f'Cannot delete category: {str(e)}')
        return redirect('category_list')
    return render(request, 'tasks/category_confirm_delete.html', {'category': category})


@login_required
def project_list(request):
    """List all projects"""
    projects = Project.objects.filter(owner=request.user).annotate(
        task_count=Count('tasks')
    )
    return render(request, 'tasks/project_list.html', {'projects': projects})


@login_required
def project_create(request):
    """Create a new project"""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            messages.success(request, 'Project created successfully!')
            return redirect('project_list')
    else:
        form = ProjectForm()
    return render(request, 'tasks/project_form.html', {'form': form})


@login_required
def project_delete(request, pk):
    """Delete a project - will cascade delete all related tasks"""
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    if request.method == 'POST':
        task_count = project.tasks.count()
        project.delete()
        messages.success(request, f'Project and {task_count} related tasks deleted!')
        return redirect('project_list')
    return render(request, 'tasks/project_confirm_delete.html', {'project': project})
