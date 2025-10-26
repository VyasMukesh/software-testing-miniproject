from django.contrib import admin
from .models import Category, Project, Task, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'priority', 'created_by', 'assigned_to', 'created_at']
    search_fields = ['title', 'description']
    list_filter = ['status', 'priority', 'created_at', 'category', 'project']
    date_hierarchy = 'created_at'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'created_at']
    search_fields = ['content']
    list_filter = ['created_at']
