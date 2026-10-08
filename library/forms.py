from django import forms
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
