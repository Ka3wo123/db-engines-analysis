import importlib
import os.path
from datetime import timedelta
from functools import wraps
from inspect import signature

from openpyxl import Workbook

db_modules = {
    "mysql": "measurements.sql.mysql.mysql_ops",
    "postgresql": "measurements.sql.postgresql.postgresql_ops",
    "cassandra": "measurements.nosql.cassandra.cassandra_ops",
    "neo4j": "measurements.nosql.neo4j.neo4j_ops",
}

db_containers = {
    "mysql": "mysql",
    "postgresql": "postgresql",
    "cassandra": "cassandra",
    "neo4j": "neo4j",
}


def measure_performance(func):
    """Execution time measurement decorator DQL operations for any database"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        num_records = kwargs.get("records", 1000)

        db_metrics = func(*args, **kwargs)

        stats = {
            "operation": func.__name__,
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
            if func == __doc__:
                continue
            if not func:
                print(f"Function {op} not found. Skipping...")
                continue
            if callable(func) and getattr(func, "_is_measurable", False):
                print(f"- Running {op}() for {repeats} repetitions...")

                execution_times = []
                for repeat in range(repeats):
                    stats = func()
                    execution_times.append(stats["execution_time_ms"])

                mean_execution_time = sum(execution_times) / repeats
                results.append({
                    "database": db_name,
                    "operation": op,
                    "records_amount": records,
                    "execution_time_ms": mean_execution_time
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

    ws.append(["Database", "Operation", "Records", "Execution Time (ms)"])

    for r in results:
        ws.append([
            r.get("database", None),
            r.get("operation", None),
            r.get("records_amount", 0),
            r.get("execution_time_ms", 0)
        ])

    os.makedirs("results", exist_ok=True)
    wb.save(os.path.join("./results/", filename))
    print(f"Results saved: {filename}")
