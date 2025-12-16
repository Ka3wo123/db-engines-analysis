import pandas as pd
import matplotlib.pyplot as plt
import os


def load_and_plot(filename, output_dir="plots"):
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(filename):
        print(f"File '{filename}' does not exist!")
        return

    df = pd.read_excel(filename)

    # bezpieczeństwo typów (Excel lubi psuć formaty)
    numeric_cols = [
        "CPU Peak (%) (avg)",
        "RAM Peak (MB) (avg)",
        "Execution Time (ms)"
    ]

    for col in numeric_cols:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", ".", regex=False)
            .astype(float)
        )

    # ======================
    # CPU
    # ======================
    plt.figure(figsize=(10, 6))
    for db in df["Database"].unique():
        subset = df[df["Database"] == db]
        plt.plot(
            subset["Operation"],
            subset["CPU Peak (%) (avg)"],
            marker="o",
            label=db
        )

    plt.title("CPU Usage by Database")
    plt.xlabel("Operation")
    plt.ylabel("CPU Peak (%) (avg)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "cpu.png"))
    plt.close()

    # ======================
    # RAM
    # ======================
    plt.figure(figsize=(10, 6))
    for db in df["Database"].unique():
        subset = df[df["Database"] == db]
        plt.plot(
            subset["Operation"],
            subset["RAM Peak (MB) (avg)"],
            marker="o",
            label=db
        )

    plt.title("RAM Usage by Database")
    plt.xlabel("Operation")
    plt.ylabel("RAM Peak (MB) (avg)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "ram.png"))
    plt.close()

    # ======================
    # EXECUTION TIME
    # ======================
    plt.figure(figsize=(10, 6))
    for db in df["Database"].unique():
        subset = df[df["Database"] == db]
        plt.plot(
            subset["Operation"],
            subset["Execution Time (ms)"],
            marker="o",
            label=db
        )

    plt.title("Execution Time by Database")
    plt.xlabel("Operation")
    plt.ylabel("Execution Time (ms)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "execution_time.png"))
    plt.close()

    print(f"Wykresy zapisane w katalogu: {output_dir}")
