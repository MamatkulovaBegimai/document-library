import os
import zipfile

from django import forms
from django.core.files.uploadedfile import UploadedFile

from .models import Document


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'author', 'category', 'tags', 'description', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Документтин аталышы'}),
            'author': forms.TextInput(attrs={'placeholder': 'Автору'}),
            'category': forms.TextInput(attrs={'placeholder': 'мис. Математика, Тарых…'}),
            'tags': forms.TextInput(attrs={'placeholder': 'лекция, 1-курс, экзамен'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_file(self):
        file = self.cleaned_data['file']
        max_size = 100 * 1024 * 1024
        if file.size > max_size:
            raise forms.ValidationError('Файл өлчөмү 100 MB\'ден ашпашы керек.')

        # Мазмунду жаңы жүктөлгөн файлдар үчүн гана текшеребиз.
        # Редактирлөөдө мурдагы R2 файлын кайра окуу талап кылынбайт.
        if not isinstance(file, UploadedFile):
            return file

        ext = os.path.splitext(file.name)[1].lower()

        try:
            file.seek(0)

            if ext == '.pdf':
                if file.read(5) != b'%PDF-':
                    raise forms.ValidationError(
                        'Бул файл чыныгы PDF файлы эмес. Туура PDF файл жүктөңүз.'
                    )

            elif ext == '.docx':
                try:
                    with zipfile.ZipFile(file) as archive:
                        names = set(archive.namelist())
                        required = {'[Content_Types].xml', 'word/document.xml'}
                        if not required.issubset(names):
                            raise forms.ValidationError(
                                'Бул файл чыныгы DOCX документи эмес. Туура Word файлын жүктөңүз.'
                            )
                except zipfile.BadZipFile:
                    raise forms.ValidationError(
                        'Бул файл чыныгы DOCX документи эмес. Туура Word файлын жүктөңүз.'
                    )

        finally:
            file.seek(0)

        return file


class TeacherProfileForm(forms.ModelForm):
    class Meta:
        from django.contrib.auth import get_user_model
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Аты',
            'last_name': 'Фамилиясы',
            'email': 'Email',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if not email:
            raise forms.ValidationError('Email дарегин көрсөтүңүз.')

        User = self._meta.model
        qs = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Бул email башка аккаунтка катталган.')
        return email
