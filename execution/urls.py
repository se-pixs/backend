from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:action_name>', views.execute),
    #path('changeFormat', views.change_format, name='detail'),
    #path('convertToLowPoly', views.convert_to_low_poly, name='detail'),
    #path('instagramPanoSplit', views.ig_pano_split, name='detail'),
]