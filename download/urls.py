from django.urls import path

from . import views

urlpatterns = [
    path('', views.download, name='download'),
    path('preview', views.preview, name='preview'),
]