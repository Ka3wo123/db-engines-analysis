import importlib
import json
from functools import wraps
from inspect import signature
from datetime import timedelta
from openpyxl import Workbook

from measurements.docker_helper import get_resources_peak

db_modules = {
    "mysql": "measurements.sql.mysql.mysql_ops",
    "postgresql": "measurements.sql.postgresql.postgresql_ops",
    "cassandra": "measurements.nosql.cassandra.cassandra_ops",
    "neo4j": "measurements.nosql.neo4j.neo4j_ops",
}

db_containers = {
    "mysql":"mysql",
    "postgresql":"postgresql",
    "cassandra":"cassandra",
    "neo4j":"neo4j",
}


def measure_performance(func):
    """CPU, RAM and execution time measurement decorator DQL operations for any database"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        num_records = kwargs.get("records", 1000)
        container = kwargs.get("container")

        if container is None:
            db_metrics = func(*args, **kwargs, container=None)
            return {
                "operation": func.__name__,
                "peak_cpu": 0,
                "peak_ram": 0,
                "records_amount": num_records,
                "db_metrics": db_metrics,
            }

        peak_ram, peak_cpu = get_resources_peak(container)
        db_metrics = func(*args, **kwargs)

        stats = {
            "operation": func.__name__,
            "peak_cpu": peak_cpu,
            "peak_ram": peak_ram,
            "records_amount": num_records,
            "db_metrics": db_metrics,
        }

        if db_metrics and isinstance(db_metrics, dict):
            stats.update(db_metrics)

            
            if isinstance(stats.get("execution_time_ms"), timedelta):
                stats["execution_time_ms"] = (
                    stats["execution_time_ms"].total_seconds() * 1000
                )
        return stats

    wrapper._is_measurable = True

    return wrapper


def run_measurement(databases, records=1000, repeats=5, no_stats=False):
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
            if func == __doc__:
                continue
            if not func:
                print(f"Function {op} not found. Skipping...")
                continue
            if callable(func) and getattr(func, "_is_measurable", False):
                print(f"- Running {op}() for {repeats} repetitions...")

                cpu_values = []
                ram_values = []
                stats = None

                for _ in range(repeats):
                    if no_stats:
                        stats = func()
                        cpu_values.append(0)
                        ram_values.append(0)
                    else:
                        stats = func(container=db_containers[db_name])
                        cpu_values.append(stats["peak_cpu"])
                        ram_values.append(stats["peak_ram"])

                results.append({
                    "database": db_name,
                    "operation": op,
                    "records_amount": records,
                    "peak_cpu": sum(cpu_values) / repeats,
                    "peak_ram": sum(ram_values) / repeats,
                    "execution_time_ms": stats["execution_time_ms"]
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

    ws.append(["Database", "Operation", "CPU Peak (%) (avg)", "RAM Peak (MB) (avg)", "Records", "Execution Time (ms)"])

    for r in results:
        execution_time = r.get("execution_time_ms")
        ws.append([
            r["database"],
            r["operation"],
            round(r.get("peak_cpu", 0), 2),
            round(r.get("peak_ram", 0), 2),
            r.get("records_amount", 0),
            round(execution_time, 3) if execution_time is not None else None
        ])

    wb.save(filename)
    print(f"Results saved: {filename}")
