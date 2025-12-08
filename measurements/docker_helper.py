import json
import time

import docker


def get_resources_peak(container_name):
    client = docker.from_env()
    container = client.containers.get(container_name)
    peak_cpu = 0.0
    peak_ram = 0.0
    duration = 5

    start = time.time()
    for raw in container.stats(stream=True):
        stats = json.loads(raw.decode("utf-8"))
        cpu = _calc_cpu_percent(stats)
        ram = stats["memory_stats"]["usage"] / (1024 ** 2)

        peak_cpu = max(peak_cpu, cpu)
        peak_ram = max(peak_ram, ram)

        if time.time() - start > duration:
            break

    return peak_cpu, peak_ram


def _calc_cpu_percent(stats):
    cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - stats["precpu_stats"]["cpu_usage"]["total_usage"]
    system_delta = stats["cpu_stats"]["system_cpu_usage"] - stats["precpu_stats"]["system_cpu_usage"]
    number_cpus = stats["cpu_stats"]["online_cpus"]
    return (cpu_delta / system_delta) * number_cpus * 100


