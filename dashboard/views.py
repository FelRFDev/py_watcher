from django.shortcuts import render
from .dockerstats import get_docker_info
import glob, os, pandas as pd

def get_temperature_data():
    """
    Lê o arquivo CSV mais recente gerado pelo OpenHardwareMonitor 
    e extrai as temperaturas da CPU, Hotspot da CPU, GPU e SSD.

    Returns:
        dict: Dicionário contendo os dados de temperatura:
            - 'cpu_temp': Temperatura da CPU principal
            - 'cpu_hotspot_temp': Temperatura do hotspot da CPU
            - 'gpu_temp': Temperatura da GPU
            - 'ssd_temp': Temperatura do SSD
            Valores podem ser None caso não encontrados.
    """
    files = glob.glob(os.path.join(
        'C:/Users/T-Gamer/Desktop/PROJETOS_PROGRAMACAO/py_watcher/py_watcher/OpenHardwareMonitor/',
        'OpenHardwareMonitorLog-*.csv'
    ))

    if not files:
        return {}

    latest = max(files, key=os.path.getctime)
    df = pd.read_csv(latest)
    row = df.iloc[-1]

    temp_data = {
        'cpu_temp': None,
        'cpu_hotspot_temp': None,
        'gpu_temp': None,
        'ssd_temp': None
    }

    for name, value in row.items():
        try:
            v = float(value)
            if '/amdcpu/0/temperature/0' in name:
                temp_data['cpu_temp'] = round(v, 1)
            elif '/amdcpu/0/temperature/4' in name:
                temp_data['cpu_hotspot_temp'] = round(v, 1)
            elif '/atigpu/0/temperature/0' in name:
                temp_data['gpu_temp'] = round(v, 1)
            elif '/hdd/0/temperature/0' in name:
                temp_data['ssd_temp'] = round(v, 1)
        except:
            # Ignora valores que não podem ser convertidos para float
            pass

    return temp_data


def index(request):
    """
    View principal que renderiza a página inicial com os dados de temperatura do sistema.

    Args:
        request (HttpRequest): Objeto de requisição HTTP do Django.

    Returns:
        HttpResponse: Página renderizada com as temperaturas do hardware.
    """
    temp_data = get_temperature_data()
    print('TESTE DE RECEBIMENTO DE DADOS')
    print(temp_data)
    return render(request, 'index.html', {'temperature_list': temp_data})


def docker_dashboard(request):
    """
    View que renderiza o painel de monitoramento de containers Docker.

    Coleta informações como containers ativos, pausados, finalizados e total.

    Args:
        request (HttpRequest): Objeto de requisição HTTP do Django.

    Returns:
        HttpResponse: Página renderizada com informações dos containers Docker.
    """
    try:
        docker_data = get_docker_info()
        return render(request, 'dockerdash.html', {
            'containers': docker_data['containers'],
            'summary': docker_data['summary']
        })
    except Exception as e:
        print(f"Erro ao carregar dados Docker: {e}")
        # Fallback com dados vazios
        return render(request, 'dockerdash.html', {
            'containers': [],
            'summary': {
                'total': 0,
                'running': 0,
                'paused': 0,
                'exited': 0
            }
        })
