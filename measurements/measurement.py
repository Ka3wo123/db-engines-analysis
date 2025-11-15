import importlib
import json
import time
from functools import wraps
from inspect import signature

import psutil
from openpyxl import Workbook

db_modules = {
    "mysql": "measurements.sql.mysql.mysql_ops",
    "postgresql": "measurements.sql.postgresql.postgresql_ops",
    "cassandra": "measurements.nosql.cassandra.cassandra_ops",
    "neo4j": "measurements.nosql.neo4j.neo4j_ops",
}


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

    wrapper._is_measurable = True

    return wrapper


def run_measurement(databases, records=1000, repeats=5):
    """
    For each database:
    1. Run DML create
    2. Measure DQL operations
    3. Truncate table after measurement
    """
    results = []

    for db_name in databases:
        if db_name not in db_modules:
            print(f"Unknown database name (available: {db_modules.keys()}). Skipping...")
            continue

        module = importlib.import_module(db_modules[db_name])
        print(f"\n=== Running benchmarks for {db_name.upper()} ===")

        create_func = getattr(module, "create", None)
        if create_func:
            print(f"Creating records for {db_name.upper()}...", end='')
            sig = signature(create_func)
            if "records" in sig.parameters:
                create_func(records=records)
            else:
                create_func()
            print("Finished.")

        for op in dir(module):
            func = getattr(module, op, None)
            if not func:
                print(f"Function {op} not found. Skipping...")
                continue
            if callable(func) and getattr(func, "_is_measurable", False):
                print(f"- Running {op}() for {repeats} repetitions...")

                run_times = []
                cpu_values = []
                ram_values = []
                stats = None

                for _ in range(repeats):
                    stats = func()
                    run_times.append(stats["time_sec"])
                    cpu_values.append(stats["cpu_percent"])
                    ram_values.append(stats["mem_usage_mb"])

                results.append({
                    "database": db_name,
                    "operation": op,
                    "records_amount": records,
                    "time_sec": sum(run_times) / repeats,
                    "cpu_percent": sum(cpu_values) / repeats,
                    "mem_usage_mb": sum(ram_values) / repeats,
                    "db_raw": stats["db_metrics"]
                })

        truncate_func = getattr(module, "truncate", None)
        if truncate_func:
            print(f"Truncating table for {db_name.upper()}...", end='')
            truncate_func()
            print("Finished.")

    return results


def save_to_excel(results, filename="db_performance.xlsx"):
    wb = Workbook()
    ws = wb.active
    ws.title = "Performance"

    ws.append(["Database", "Operation", "Time (s) (avg)", "CPU (%) (avg)", "RAM Change (MB) (avg)", "Records", "DB metrics"])

    for r in results:
        ws.append([
            r["database"],
            r["operation"],
            round(r["time_sec"], 4),
            round(r["cpu_percent"], 2),
            round(r["mem_usage_mb"], 2),
            r["records_amount"],
            json.dumps(r['db_raw'])
        ])

    wb.save(filename)
    print(f"Results saved: {filename}")
