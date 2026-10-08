from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import Document, Teacher


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'uploaded_by', 'category', 'file_type', 'downloads', 'created_at')
    list_filter = ('category', 'uploaded_by')
    search_fields = ('title', 'author', 'description', 'tags', 'uploaded_by__username', 'uploaded_by__email')
    readonly_fields = ('id', 'file_size', 'downloads', 'created_at')


@admin.register(Teacher)
class TeacherAdmin(UserAdmin):
    """Отдельный раздел админки для преподавателей."""

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(groups__name='Teachers').distinct()

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        teachers_group, _ = Group.objects.get_or_create(name='Teachers')
        obj.groups.add(teachers_group)

    def delete_model(self, request, obj):
        # Удаление через раздел "Преподаватели" удаляет сам аккаунт.
        super().delete_model(request, obj)

    list_display = ('username', 'first_name', 'last_name', 'email', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('username', 'first_name', 'last_name', 'email')
