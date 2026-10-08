import io
import zipfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase

from .forms import DocumentForm


class DocumentFileValidationTests(SimpleTestCase):
    def _form(self, uploaded_file):
        return DocumentForm(
            data={
                'title': 'Тест документ',
                'author': '',
                'category': '',
                'tags': '',
                'description': '',
            },
            files={'file': uploaded_file},
        )

    def test_accepts_real_pdf(self):
        uploaded = SimpleUploadedFile(
            'document.pdf',
            b'%PDF-1.4\n% test pdf',
            content_type='application/pdf',
        )
        form = self._form(uploaded)
        self.assertTrue(form.is_valid(), form.errors)

    def test_rejects_fake_pdf(self):
        uploaded = SimpleUploadedFile(
            'document.pdf',
            b'not really a pdf',
            content_type='application/pdf',
        )
        form = self._form(uploaded)
        self.assertFalse(form.is_valid())
        self.assertIn('file', form.errors)

    def test_accepts_real_docx_container(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as archive:
            archive.writestr('[Content_Types].xml', '<Types></Types>')
            archive.writestr('word/document.xml', '<w:document></w:document>')

        uploaded = SimpleUploadedFile(
            'document.docx',
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        )
        form = self._form(uploaded)
        self.assertTrue(form.is_valid(), form.errors)

    def test_rejects_fake_docx(self):
        uploaded = SimpleUploadedFile(
            'document.docx',
            b'not really a docx',
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        )
        form = self._form(uploaded)
        self.assertFalse(form.is_valid())
        self.assertIn('file', form.errors)
