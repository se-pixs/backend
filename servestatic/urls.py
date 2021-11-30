from django.urls import path

from . import views

urlpatterns = [
    path('icon/<str:icon_name>/', views.static_icon, name='icon'),
]