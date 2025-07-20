from django.shortcuts import render
from .dockerstats import get_docker_info
import glob, os, pandas as pd

def get_temperature_data():
    files = glob.glob(os.path.join('C:/Users/T-Gamer/Desktop/PROJETOS_PROGRAMACAO/py_watcher/py_watcher/OpenHardwareMonitor/', 'OpenHardwareMonitorLog-*.csv'))
    if not files: return {}
    latest = max(files, key=os.path.getctime)
    df = pd.read_csv(latest)
    row = df.iloc[-1]
    
    # Filtra apenas os sensores importantes
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
            pass
    
    return temp_data

def index(request):
    temp_data = get_temperature_data()
    print('TESTE DE RECEBIMENTO DE DADOS')
    print(temp_data)
    return render(request, 'index.html', {'temperature_list': temp_data})




def docker_dashboard(request):
    # Carrega apenas o essencial para a primeira renderização
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