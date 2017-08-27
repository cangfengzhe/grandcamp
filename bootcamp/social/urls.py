from django.conf.urls import url

from bootcamp.social import views

urlpatterns = [
    url(r'^$', views.social, name='social'),
]
