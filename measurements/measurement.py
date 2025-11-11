import importlib
import time
from functools import wraps
from inspect import signature
import psutil
from openpyxl import Workbook


CRUD_OPERATIONS = ['create', 'read', 'update', 'delete', 'truncate']


def measure_performance(func):
    """CPU, RAM and execution time measurement decorator for any CRUD operation for any database"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        num_records = kwargs.get("records", 1000)
        process = psutil.Process()
        cpu_before = psutil.cpu_percent(interval=None)

        try:
            mem_before = process.memory_info().rss / (1024 * 1024)
        except AttributeError:
            mem_before = process.memory_full_info().rss / (1024 * 1024)

        start_time = time.perf_counter()
        call = func(*args, **kwargs)
        end_time = time.perf_counter()

        cpu_after = psutil.cpu_percent(interval=None)

        try:
            mem_after = process.memory_info().rss / (1024 * 1024)
        except AttributeError:
            mem_after = process.memory_full_info().rss / (1024 * 1024)

        return {
            "operation": func.__name__,
            "time_sec": end_time - start_time,
            "cpu_percent": (cpu_after + cpu_before) / 2,
            "mem_usage_mb": mem_after - mem_before,
            "records_amount": num_records
        }

    return wrapper


def run_measurement(databases, records):
    results = []
    db_modules = {
        "mysql": "measurements.sqlcrud.mysql.mysql_ops",
        "postgresql": "measurements.sqlcrud.postgresql.postgresql_ops",
        "cassandra": "measurements.nosqlcrud.cassandra.cassandra_ops",
        "neo4j": "measurements.nosqlcrud.neo4j.neo4j_ops",
    }

    for db_name in databases:
        if db_name not in db_modules:
            print(f"Unknown database name (available: {db_modules.keys()}). Skipping...")
            continue

        module = importlib.import_module(db_modules[db_name])
        print(f"\n=== Running benchmarks for {db_name.upper()} ===")

        for op in CRUD_OPERATIONS:
            func = getattr(module, op)
            print(f"Running {op}()...")
            sig = signature(func)
            if 'records' in sig.parameters:
                stats = func(records=records)
            else:
                stats = func()
            stats['database'] = db_name
            results.append(stats)
    return results


def save_to_excel(results, filename="db_performance.xlsx"):
    wb = Workbook()
    ws = wb.active
    ws.title = "Performance"

    ws.append(["Database", "Operation", "Time (s)", "CPU (%)", "RAM Change (MB)", "Records amount"])

    for r in results:
        ws.append([
            r["database"],
            r["operation"],
            round(r["time_sec"], 4),
            round(r["cpu_percent"], 2),
            round(r["mem_usage_mb"], 2),
            r['records_amount']

        ])

    wb.save(filename)
    print(f"Results saved: {filename}")
