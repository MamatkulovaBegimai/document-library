import os
import uuid

from django.core.validators import FileExtensionValidator
from django.db import models


def document_upload_path(instance, filename):
    ext = filename.split('.')[-1].lower()
    return f'documents/{instance.id}.{ext}'


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField('Аталышы', max_length=255)
    author = models.CharField('Автору', max_length=255, blank=True)
    description = models.TextField('Сүрөттөмө', blank=True)
    category = models.CharField('Категория', max_length=100, blank=True, db_index=True)
    tags = models.CharField('Тегдер (үтүр менен)', max_length=255, blank=True)

    file = models.FileField(
        'Файл',
        upload_to=document_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx'])],
    )
    file_size = models.PositiveIntegerField('Файл өлчөмү (байт)', default=0, editable=False)
    downloads = models.PositiveIntegerField('Жүктөлгөн саны', default=0, editable=False)

    created_at = models.DateTimeField('Кошулган күнү', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Документ'
        verbose_name_plural = 'Документтер'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.file and not self.file_size:
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    @property
    def file_type(self):
        return os.path.splitext(self.file.name)[1].lstrip('.').lower()

    @property
    def tags_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    @property
    def call_number(self):
        return str(self.id)[:6].upper()
