from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
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
    Document.objects.filter(pk=pk).update(downloads=doc.downloads + 1)
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
            doc = form.save()
            messages.success(request, f'«{doc.title}» ийгиликтүү кошулду.')
            return redirect('library:document_detail', pk=doc.pk)
    else:
        form = DocumentForm()

    return render(request, 'library/document_upload.html', {'form': form})

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
