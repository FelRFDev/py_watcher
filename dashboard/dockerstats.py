import docker

def get_docker_info():
    """
    Coleta informações e estatísticas de todos os containers Docker disponíveis no host.

    Retorna um dicionário com duas chaves:
    - 'containers': lista de dicionários com dados de cada container, contendo:
        * 'id': ID curto do container
        * 'name': nome do container
        * 'status': status atual (ex: running, paused, exited)
        * 'image': tag da imagem usada ou "Sem tag" se não existir
        * 'cpu_percent': uso de CPU em percentual calculado pelo _calc_cpu_percent
        * 'mem_usage': uso de memória em bytes
        * 'mem_limit': limite de memória em bytes
    Se ocorrer erro ao coletar stats, valores padrão zerados são retornados para o container e o erro é impresso.

    - 'summary': dicionário com contagem dos containers por status:
        * 'total': total de containers
        * 'running': containers em execução
        * 'paused': containers pausados
        * 'exited': containers finalizados

    Usa a API oficial do Docker via python 'docker.from_env()'.

    Uso típico:
        dados = get_docker_info()
        print(dados['summary'])
        for c in dados['containers']:
            print(c['name'], c['cpu_percent'], c['mem_usage'])
    """
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
    """
    Calcula o percentual de uso de CPU para um container Docker com base nas estatísticas fornecidas.

    A fórmula compara o uso total de CPU entre duas medições consecutivas, normalizando pelo número de CPUs e 
    tempo do sistema, retornando um valor percentual arredondado com duas casas decimais.

    Se houver erros (dados ausentes ou divisão por zero), retorna 0.0.

    Parâmetros:
        stats (dict): dicionário de estatísticas coletadas do container (ex: container.stats(stream=False))

    Retorna:
        float: percentual de uso da CPU.
    """
    try:
        cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
        system_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
        if system_delta > 0 and cpu_delta > 0:
            return round((cpu_delta / system_delta) * len(stats['cpu_stats']['cpu_usage']['percpu_usage']) * 100.0, 2)
    except (KeyError, ZeroDivisionError):
        pass
    return 0.0
