from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.shortcuts import render, redirect, get_object_or_404

from .models import Document
from .forms import DocumentForm, TeacherProfileForm

PAGE_SIZE = 12


def teacher_required(view_func):
    """Кирүү укугу: суперпайдалануучу же 'Teachers' тобунун мүчөсү гана."""
    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        is_teacher = request.user.is_superuser or request.user.groups.filter(name='Teachers').exists()
        if not is_teacher:
            raise PermissionDenied('Бул бөлүккө мугалимдер жана админдер гана кире алат.')
        return view_func(request, *args, **kwargs)
    return wrapper


def _teacher_document_or_404(request, pk):
    """Мугалим өз документин гана өзгөртө/өчүрө алат; суперпайдалануучу — баарын."""
    docs = Document.objects.all()
    if not request.user.is_superuser:
        docs = docs.filter(uploaded_by=request.user)
    return get_object_or_404(docs, pk=pk)


def document_list(request):
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()

    docs = Document.objects.all()

    if category:
        docs = docs.filter(category=category)

    if query:
        docs = docs.filter(
            Q(title__icontains=query)
            | Q(author__icontains=query)
            | Q(description__icontains=query)
            | Q(tags__icontains=query)
        )

    categories = (
        Document.objects.exclude(category='')
        .values_list('category', flat=True)
        .distinct()
        .order_by('category')
    )

    paginator = Paginator(docs, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'active_category': category,
        'total': paginator.count,
    }
    return render(request, 'library/document_list.html', context)


def document_detail(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    return render(request, 'library/document_detail.html', {'doc': doc})


def document_download(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    Document.objects.filter(pk=pk).update(downloads=F('downloads') + 1)
    return redirect(doc.file.url)


def document_read(request, pk):
    """Документти браузерде түз ачуу ('Оку онлайн')."""
    doc = get_object_or_404(Document, pk=pk)
    absolute_file_url = request.build_absolute_uri(doc.file.url)
    return render(request, 'library/document_read.html', {
        'doc': doc,
        'absolute_file_url': absolute_file_url,
    })


@teacher_required
def document_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.uploaded_by = request.user
            doc.save()
            messages.success(request, f'«{doc.title}» ийгиликтүү кошулду.')
            return redirect('library:teacher_documents')
    else:
        form = DocumentForm()

    return render(request, 'library/document_upload.html', {'form': form})


@teacher_required
def teacher_documents(request):
    """Мугалимдин жеке кабинети — өзүнүн документтери."""
    docs = Document.objects.filter(uploaded_by=request.user)
    if request.user.is_superuser:
        docs = Document.objects.all()

    paginator = Paginator(docs, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'library/teacher_documents.html', {
        'page_obj': page_obj,
        'total': paginator.count,
    })


@teacher_required
def document_edit(request, pk):
    doc = _teacher_document_or_404(request, pk)

    if request.method == 'POST':
        old_file_name = doc.file.name
        form = DocumentForm(request.POST, request.FILES, instance=doc)
        if form.is_valid():
            updated = form.save()
            if old_file_name and updated.file.name != old_file_name:
                updated.file.storage.delete(old_file_name)
            messages.success(request, f'«{updated.title}» өзгөртүүлөрү сакталды.')
            return redirect('library:teacher_documents')
    else:
        form = DocumentForm(instance=doc)

    return render(request, 'library/document_edit.html', {
        'form': form,
        'doc': doc,
    })


@teacher_required
def document_delete(request, pk):
    doc = _teacher_document_or_404(request, pk)

    if request.method == 'POST':
        title = doc.title
        if doc.file:
            doc.file.delete(save=False)
        doc.delete()
        messages.success(request, f'«{title}» өчүрүлдү.')
        return redirect('library:teacher_documents')

    return render(request, 'library/document_delete_confirm.html', {'doc': doc})


@teacher_required
def teacher_profile(request):
    """Мугалимдин профили: аты-жөнү, email жана сырсөздү өзгөртүү."""
    profile_form = TeacherProfileForm(instance=request.user, prefix='profile')
    password_form = PasswordChangeForm(user=request.user, prefix='password')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'profile':
            profile_form = TeacherProfileForm(
                request.POST,
                instance=request.user,
                prefix='profile'
            )
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Профиль маалыматы сакталды.')
                return redirect('library:teacher_profile')

        elif action == 'password':
            password_form = PasswordChangeForm(
                user=request.user,
                data=request.POST,
                prefix='password'
            )
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Сырсөз ийгиликтүү өзгөртүлдү.')
                return redirect('library:teacher_profile')

    return render(request, 'library/teacher_profile.html', {
        'profile_form': profile_form,
        'password_form': password_form,
    })
