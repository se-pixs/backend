from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('changeFormat', views.change_format, name='detail'),
]