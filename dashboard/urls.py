from django.urls import path
from .views import index, docker_dashboard

urlpatterns = [ 
    path('', index, name='dashboard'), 
    path('docker/', docker_dashboard, name='docker_dashboard'),
]

