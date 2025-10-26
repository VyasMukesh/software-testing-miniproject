from django import forms
from django.contrib.auth.models import User
from .models import Task, Category, Project, Comment


class TaskForm(forms.ModelForm):
    """Form for creating and updating tasks"""
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'priority', 
                  'assigned_to', 'category', 'project', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter task title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter task description'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'project': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filter assigned_to to only show users
            self.fields['assigned_to'].queryset = User.objects.all()
            # Filter categories and projects to user's own
            self.fields['category'].queryset = Category.objects.filter(created_by=user)
            self.fields['project'].queryset = Project.objects.filter(owner=user)


class CategoryForm(forms.ModelForm):
    """Form for creating categories"""
    
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter category description (optional)'
            }),
        }


class ProjectForm(forms.ModelForm):
    """Form for creating projects"""
    
    class Meta:
        model = Project
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter project name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter project description (optional)'
            }),
        }


class CommentForm(forms.ModelForm):
    """Form for adding comments to tasks"""
    
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add a comment...'
            }),
        }
