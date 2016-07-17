from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.login_page, name='index'),
    url(r'^login', views.login_page, name='login'),
    url(r'^logout', views.logout_page, name='logout'),
    url(r'^change_pwd', views.change_pwd, name='change_pwd'),
    url(r'index', views.index, name='index'),
    url(r'users', views.users, name='users'),
    url(r'groups', views.groups, name='groups'),
    url(r'cmd_sets', views.cmd_sets, name='cmd_sets'),
    url(r'logs', views.logs, name='logs'),
    url(r'settings', views.settings, name='settings'),
    url(r'help', views.help_page, name='help'),
]
