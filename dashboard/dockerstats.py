import docker


import docker

def get_docker_info():
    client = docker.from_env()
    containers = client.containers.list(all=True)

    data = []
    for container in containers:
        try:
            stats = container.stats(stream=False)
            mem_stats = stats.get('memory_stats', {})
            cpu_percent = _calc_cpu_percent(stats)

            data.append({
                'id': container.short_id,
                'name': container.name,
                'status': container.status,
                'image': container.image.tags[0] if container.image.tags else "Sem tag",
                'cpu_percent': cpu_percent,
                'mem_usage': mem_stats.get('usage', 0),
                'mem_limit': mem_stats.get('limit', 0),
            })
        except Exception as e:
            print(f"[ERRO] Falha ao coletar stats do container {container.name}: {e}")
            data.append({
                'id': container.short_id,
                'name': container.name,
                'status': container.status,
                'image': container.image.tags[0] if container.image.tags else "Sem tag",
                'cpu_percent': 0.0,
                'mem_usage': 0,
                'mem_limit': 0,
            })

    # Estatísticas globais
    docker_summary = {
        'total': len(containers),
        'running': len([c for c in containers if c.status == 'running']),
        'paused': len([c for c in containers if c.status == 'paused']),
        'exited': len([c for c in containers if c.status == 'exited']),
    }

    return {
        'containers': data,
        'summary': docker_summary
    }

def _calc_cpu_percent(stats):
    try:
        cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
        system_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
        if system_delta > 0 and cpu_delta > 0:
            return round((cpu_delta / system_delta) * len(stats['cpu_stats']['cpu_usage']['percpu_usage']) * 100.0, 2)
    except (KeyError, ZeroDivisionError):
        pass
    return 0.0

