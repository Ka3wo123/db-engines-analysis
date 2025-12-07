import pandas as pd
import matplotlib.pyplot as plt
import os

def load_and_plot(filename, output_dir="plots"):

    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(filename):
        print(f"File '{filename}' does not exist!")
        return

    df = pd.read_excel(filename)

    df["Time (s) (avg)"] = df["Time (s) (avg)"].astype(str).str.replace(",", ".").astype(float)
    df["CPU (%) (avg)"] = df["CPU (%) (avg)"].astype(str).str.replace(",", ".").astype(float)
    df["RAM Change (MB) (avg)"] = df["RAM Change (MB) (avg)"].astype(str).str.replace(",", ".").astype(float)

    plt.figure(figsize=(10, 6))
    for db in df["Database"].unique():
        subset = df[df["Database"] == db]
        plt.plot(subset["Operation"], subset["Time (s) (avg)"], marker="o", label=db)

    plt.title("Operation Time by Database")
    plt.xlabel("Operation")
    plt.ylabel("Time (s) (avg)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "time.png"))


    plt.figure(figsize=(10, 6))
    for db in df["Database"].unique():
        subset = df[df["Database"] == db]
        plt.plot(subset["Operation"], subset["CPU (%) (avg)"], marker="o", label=db)

    plt.title("CPU Usage by Database")
    plt.xlabel("Operation")
    plt.ylabel("CPU (%) (avg)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "cpu.png"))

    plt.figure(figsize=(10, 6))
    for db in df["Database"].unique():
        subset = df[df["Database"] == db]
        plt.plot(subset["Operation"], subset["RAM Change (MB) (avg)"], marker="o", label=db)

    plt.title("RAM Change by Database")
    plt.xlabel("Operation")
    plt.ylabel("RAM Change (MB)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "ram.png"))


