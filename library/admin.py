from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'file_type', 'downloads', 'created_at')
    list_filter = ('category',)
    search_fields = ('title', 'author', 'description', 'tags')
    readonly_fields = ('id', 'file_size', 'downloads', 'created_at')
