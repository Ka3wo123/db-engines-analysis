import importlib
import json
import time
from functools import wraps
from inspect import signature
import psutil
from openpyxl import Workbook

DQL_OPS = ['read']


def measure_performance(func):
    """CPU, RAM and execution time measurement decorator DQL operations for any database"""

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
        db_metrics = func(*args, **kwargs)
        end_time = time.perf_counter()

        cpu_after = psutil.cpu_percent(interval=None)

        try:
            mem_after = process.memory_info().rss / (1024 * 1024)
        except AttributeError:
            mem_after = process.memory_full_info().rss / (1024 * 1024)

        stats = {
            "operation": func.__name__,
            "time_sec": end_time - start_time,
            "cpu_percent": (cpu_after + cpu_before) / 2,
            "mem_usage_mb": mem_after - mem_before,
            "records_amount": num_records,
            "db_metrics": db_metrics,
        }

        if db_metrics and isinstance(db_metrics, dict):
            stats.update(db_metrics)

        return stats

    return wrapper


def run_measurement(databases, records, repeats=5):
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

        for op in DQL_OPS:
            func = getattr(module, op, None)
            if func is None:
                print(f"Function {op} not found. Skipping...")
                continue

            print(f"Running {op}() for {repeats} repetitions...")

            run_times = []
            cpu_values = []
            ram_values = []
            stats = None

            for _ in range(repeats):
                sig = signature(func)
                # Run the benchmark once
                if 'records' in sig.parameters:
                    stats = func(records=records)
                else:
                    stats = func()

                run_times.append(stats["time_sec"])
                cpu_values.append(stats["cpu_percent"])
                ram_values.append(stats["mem_usage_mb"])

            # Store averages
            results.append({
                "database": db_name,
                "operation": op,
                "time_sec": sum(run_times) / repeats,
                "cpu_percent": sum(cpu_values) / repeats,
                "mem_usage_mb": sum(ram_values) / repeats,
                "records_amount": records,
                "db_raw": stats["db_metrics"]
            })

    return results


def save_to_excel(results, filename="db_performance.xlsx"):
    wb = Workbook()
    ws = wb.active
    ws.title = "Performance"

    ws.append(["Database", "Operation", "Time (s) (avg)", "CPU (%) (avg)", "RAM Change (MB) (avg)", "Records amount",
               "db metrics"])

    for r in results:
        ws.append([
            r["database"],
            r["operation"],
            round(r["time_sec"], 4),
            round(r["cpu_percent"], 2),
            round(r["mem_usage_mb"], 2),
            r['records_amount'],
            json.dumps(r['db_raw'])
        ])

    wb.save(filename)
    print(f"Results saved: {filename}")
