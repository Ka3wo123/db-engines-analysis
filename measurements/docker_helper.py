import requests_unixsocket

session = requests_unixsocket.Session()

def get_container_stats_raw(name):
    url = f"http+unix://%2Fvar%2Frun%2Fdocker.sock/containers/{name}/stats?stream=0"
    r = session.get(url)
    data = r.json()

    cpu_delta = data["cpu_stats"]["cpu_usage"]["total_usage"] - data["precpu_stats"]["cpu_usage"]["total_usage"]
    system_delta = data["cpu_stats"]["system_cpu_usage"] - data["precpu_stats"]["system_cpu_usage"]
    cpu = (cpu_delta / system_delta) * data["cpu_stats"]["cpu_usage"]["total_usage"] * 100

    mem = data["memory_stats"]["usage"] / (1024**2)

    return {"cpu_percent": cpu_delta, "mem_usage": mem}
