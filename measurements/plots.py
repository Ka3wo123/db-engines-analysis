import pandas as pd
import matplotlib.pyplot as plt
import os


def load_and_plot(filename, output_dir="plots"):
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join("./results", filename)

    if not os.path.exists(filename):
        print(f"File '{filename}' does not exist!")
        return

    df = pd.read_excel(filename)

    col = "Execution Time (ms)"

    df[col] = (
        df[col]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

    plt.figure(figsize=(10, 6))
    for operation in df["Operation"].unique():
        plt.figure(figsize=(10, 6))

        subset = df[df["Operation"] == operation]
        records = subset["Records"].iloc[0]

        plt.plot(
            subset["Database"],
            subset["Execution Time (ms)"],
            marker="o"
        )

        plt.title(f"Execution Time – {operation} ({records} records)")
        plt.xlabel("Database")
        plt.ylabel("Execution Time (ms)")
        plt.grid(True)
        plt.tight_layout()

        filename = f"{operation}_{records}.png"
        plt.savefig(os.path.join(output_dir, filename))
        plt.close()

    print(f"Plots saved in: {output_dir}")
