import os, sys, asyncio, json, psutil
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()
from channels.layers import get_channel_layer

async def broadcast_loop():
    """
    Loop assíncrono que coleta métricas do sistema a cada segundo e as transmite via Django Channels.

    Métricas coletadas:
    - Uso da CPU geral e por núcleo (%)
    - Uso da memória RAM (% e GB usados/total)
    - Uso do disco (% e GB usados/total)
    - Taxa de envio e recebimento de dados na rede (KB/s)
    - Temperatura média da CPU (se disponível)
    - Top 5 processos ordenados por uso de CPU (PID, nome, % CPU, % memória)

    O payload das métricas é serializado em JSON e enviado para o grupo 'system_monitor' 
    através do channel layer do Django Channels.

    O loop roda indefinidamente com pausa de 1 segundo entre as iterações.

    Exceções na coleta de dados do disco e processos são capturadas para evitar falhas.

    Uso típico:
        Executar este script para iniciar a transmissão contínua das métricas do sistema.
    """
    layer = get_channel_layer()
    prev_net = psutil.net_io_counters()

    while True:
        cpu = psutil.cpu_percent()
        per_core = psutil.cpu_percent(percpu=True)
        ram = psutil.virtual_memory()

        # Disco
        try:
            mount = psutil.disk_partitions()[0].mountpoint
            du = psutil.disk_usage(mount)
            disk_pct = du.percent
            disk_used = round(du.used / (1024**3), 1)
            disk_total = round(du.total / (1024**3), 1)
        except:
            disk_pct = disk_used = disk_total = 0

        # Rede
        cur_net = psutil.net_io_counters()
        sent_rate = (cur_net.bytes_sent - prev_net.bytes_sent) / 1024  # KB/s enviados
        recv_rate = (cur_net.bytes_recv - prev_net.bytes_recv) / 1024  # KB/s recebidos
        prev_net = cur_net

        # Temperatura da CPU
        temps = psutil.sensors_temperatures()
        cpu_temp = None
        if 'coretemp' in temps:
            cpu_temp = sum(t.current for t in temps['coretemp']) / len(temps['coretemp'])

        # Top 5 processos por CPU
        procs = []
        for proc in psutil.process_iter(['pid','name','cpu_percent','memory_percent']):
            try:
                with proc.oneshot():
                    procs.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        procs = sorted(procs, key=lambda p: p['cpu_percent'], reverse=True)[:5]

        payload = {
            "type": "dynamic_data",
            "cpu_per_core_usage": per_core,
            "ram_percent": ram.percent,
            "ram_used_gb": round(ram.used/(1024**3),1),
            "ram_total_gb": round(ram.total/(1024**3),1),
            "disk_percent": disk_pct,
            "disk_used_gb": disk_used,
            "disk_total_gb": disk_total,
            "net_sent_rate": sent_rate,
            "net_recv_rate": recv_rate,
            "cpu_temp": cpu_temp,
            "top_processes": procs
        }

        print("🔄 broadcast:", payload)
        await layer.group_send("system_monitor", {
            "type": "dynamic_data",
            "text": json.dumps(payload)
        })
        await asyncio.sleep(1)

if __name__ == "__main__":
    """
    Ponto de entrada do script.
    Inicializa o loop assíncrono de broadcast de métricas do sistema.
    """
    print("⚙️ Broadcast iniciando...")
    asyncio.run(broadcast_loop())
