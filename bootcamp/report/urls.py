from django.conf.urls import url

from bootcamp.report import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^id/$', views.report, name='report'),
    url(r'^form/$', views.report_form, name='report_form')
]
