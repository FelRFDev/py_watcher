from django.shortcuts import render
from .dockerstats import get_docker_info

def index(request):
    return render(request, 'index.html')




def docker_dashboard(request):
    docker_data = get_docker_info()
    return render(request, 'dockerdash.html', {
        'containers': docker_data['containers'],
        'summary': docker_data['summary']
    })