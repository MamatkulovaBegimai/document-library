from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'uploaded_by', 'category', 'file_type', 'downloads', 'created_at')
    list_filter = ('category', 'uploaded_by')
    search_fields = ('title', 'author', 'description', 'tags', 'uploaded_by__username', 'uploaded_by__email')
    readonly_fields = ('id', 'file_size', 'downloads', 'created_at')
