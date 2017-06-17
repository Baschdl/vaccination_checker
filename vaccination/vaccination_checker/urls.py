from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    #url(r'^$', views.image_selector, name='image_selector'),
    url(r'^$', views.summary, name='summary'),
]