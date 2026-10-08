from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    path('', views.document_list, name='document_list'),
    path('upload/', views.document_upload, name='document_upload'),
    path('profile/', views.teacher_profile, name='teacher_profile'),
    path('documents/<uuid:pk>/', views.document_detail, name='document_detail'),
    path('documents/<uuid:pk>/download/', views.document_download, name='document_download'),
    path('documents/<uuid:pk>/read/', views.document_read, name='document_read'),
]