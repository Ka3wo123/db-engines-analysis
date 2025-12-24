import argparse
from collections import defaultdict

from measurements.measurement import run_measurement, save_to_excel
from measurements.plots import load_and_plot

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Database benchmark runner")
    parser.add_argument(
        "databases", nargs="*", default=['mysql', 'postgresql', 'cassandra', 'neo4j'],
        help="specify databases which performance will be tested"
    )
    parser.add_argument(
        "--records", type=int, default=1000,
        help="data amount"
    )

    args = parser.parse_args()

    print(f"Databases that will be measured: {', '.join(args.databases)} with {args.records} records")

    results = run_measurement(databases=args.databases, records=args.records, repeats=1)

    grouped = defaultdict(list)
    for r in results:
        grouped[r["operation"]].append(r)

    for operation, op_results in grouped.items():
        filename = f"{operation}_{args.records}.xlsx"
        save_to_excel(op_results, filename)
        load_and_plot(filename)
