import json
import psutil
import socket
import platform
import asyncio
import time
import glob
import os
import pandas as pd
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import StopConsumer
from .dockerstats import get_docker_info

class SystemMonitorConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.monitor_task = None
        self.connected = False

    async def connect(self):
        self.connected = True
        await self.accept()
        await self.send_static_data()
        self.monitor_task = asyncio.create_task(self.send_dynamic_data_loop())

    async def disconnect(self, close_code):
        self.connected = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        raise StopConsumer()

    async def receive(self, text_data):
        """Método necessário para receber mensagens do cliente"""
        try:
            data = json.loads(text_data)
            if data.get('type') == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'status': 'connected'
                }))
        except json.JSONDecodeError:
            pass

    async def send_dynamic_data_loop(self):
        while self.connected:
            try:
                await self.send_dynamic_data()
                await asyncio.sleep(2)  # Atualiza a cada 2 segundos
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in dynamic data loop: {e}")
                await asyncio.sleep(5)

    async def send_dynamic_data(self):
        try:
            # Coletar métricas básicas do sistema
            mem = psutil.virtual_memory()
            disk = self.get_disk_usage()
            net = psutil.net_io_counters()
            temp_data = self.get_temperature_data()
            
            # Coletar informações dos processos
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'username', 'status']):
                try:
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cpu_percent': round(proc.info['cpu_percent'], 1),
                        'memory_percent': round(proc.info['memory_percent'], 1),
                        'username': proc.info['username'],
                        'status': proc.info['status']

                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # Ordenar por uso de CPU e pegar os top 10
            top_processes = sorted(
                processes,
                key=lambda p: p['cpu_percent'],
                reverse=True
            )[:10]

            # Construir payload final
            dynamic = {
                "type": "dynamic_data",
                # Métricas do sistema
                "cpu_per_core_usage": [x for x in psutil.cpu_percent(percpu=True)],
                "cpu_total_percent": psutil.cpu_percent(),
                "ram_percent": mem.percent,
                "ram_total_gb": round(mem.total / (1024 ** 3), 1),
                "ram_used_gb": round(mem.used / (1024 ** 3), 1),
                "disk_percent": disk['percent'],
                "disk_total_gb": disk['total_gb'],
                "disk_used_gb": disk['used_gb'],
                "net_sent_rate": round(net.bytes_sent / 1024, 1),
                "net_recv_rate": round(net.bytes_recv / 1024, 1),
                "net_connections": len(psutil.net_connections()),
                # Temperaturas
                "cpu_temp": temp_data.get('cpu_temp'),
                "cpu_hotspot_temp": temp_data.get('cpu_hotspot_temp'),
                "gpu_temp": temp_data.get('gpu_temp'),
                "ssd_temp": temp_data.get('ssd_temp'),
                # Processos
                "top_processes": top_processes,
                "status": "connected"
            }

            await self.send(text_data=json.dumps(dynamic))
            
        except Exception as e:
            print(f"Error collecting dynamic data: {e}")
            await self.send(text_data=json.dumps({
                "type": "dynamic_data",
                "error": str(e),
                "status": "error"
            }))

    async def send_static_data(self):
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime("%d/%m/%Y %H:%M:%S")
            disk_info = self.get_disk_usage()
            
            static = {
                "type": "static_data",
                "hostname": socket.gethostname(),
                "os": f"{platform.system()} {platform.release()}",
                "boot_time": boot_time,
                "uptime": int(time.time() - psutil.boot_time()),
                "cpu_cores": psutil.cpu_count(logical=False) or 1,
                "cpu_threads": psutil.cpu_count(logical=True) or 1,
                "disk_total_gb": disk_info['total_gb'],
                "disk_main_partition": self.get_main_disk_mountpoint(),
                "status": "connected"
            }
            
            await self.send(text_data=json.dumps(static))
        except Exception as e:
            print(f"Error collecting static data: {e}")
            await self.send(text_data=json.dumps({
                "type": "static_data",
                "error": str(e),
                "status": "error"
            }))

    def get_disk_usage(self):
        try:
            partitions = psutil.disk_partitions()
            for part in partitions:
                if part.mountpoint == '/':
                    usage = psutil.disk_usage(part.mountpoint)
                    return {
                        'percent': usage.percent,
                        'total_gb': round(usage.total / (1024 ** 3), 1),
                        'used_gb': round(usage.used / (1024 ** 3), 1)
                    }
            usage = psutil.disk_usage(partitions[0].mountpoint)
            return {
                'percent': usage.percent,
                'total_gb': round(usage.total / (1024 ** 3), 1),
                'used_gb': round(usage.used / (1024 ** 3), 1)
            }
        except Exception:
            return {
                'percent': 0,
                'total_gb': 0,
                'used_gb': 0
            }

    def get_main_disk_mountpoint(self):
        try:
            partitions = psutil.disk_partitions()
            for part in partitions:
                if part.mountpoint == '/':
                    return part.mountpoint
            return partitions[0].mountpoint if partitions else "N/A"
        except Exception:
            return "N/A"
    

    
    def get_temperature_data(self):
        REL_PATH = 'C:/Users/T-Gamer/Desktop/PROJETOS_PROGRAMACAO/py_watcher/py_watcher/OpenHardwareMonitor/'
        try:
            files = glob.glob(os.path.join(REL_PATH,'OpenHardwareMonitorLog-*.csv'))
            if not files: return {}
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
                    continue
            
            return temp_data
        except Exception as e:
            print(f"Error reading temperature data: {e}")
            return {}


class DockerMonitorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send_docker_data()
        
    async def disconnect(self, close_code):
        pass
        
    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('type') == 'refresh':
            await self.send_docker_data()
    
    async def send_docker_data(self):
        while True:
            try:
                docker_data = get_docker_info()  # Use sua função existente
                await self.send(json.dumps({
                    "type": "docker_data",
                    "containers": docker_data['containers'],
                    "summary": docker_data['summary']
                }))
            except Exception as e:
                print(f"Error sending docker data: {e}")
                await self.send(json.dumps({
                    "type": "error",
                    "message": str(e)
                }))
            await asyncio.sleep(2) 