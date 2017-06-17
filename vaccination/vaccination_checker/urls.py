from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^image_selector/$', views.image_selector, name='image_selector'),
    url(r'^summary/$', views.summary, name='summary'),
    url(r'^worldmap/$', views.worldmap, name='worldmap'),
]