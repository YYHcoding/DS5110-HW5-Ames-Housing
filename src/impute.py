"""Part 6: at least two strategies for Lot Frontage, and their costs (notebook §5 pattern)."""
import sys
import pandas as pd

import matplotlib.pyplot as plt
from pathlib import Path


def global_median_impute(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    median_value = result["Lot Frontage"].median()

    result["Lot Frontage"] = result["Lot Frontage"].fillna(
        median_value
    )

    return result

def neighborhood_median_impute(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    global_median = result["Lot Frontage"].median()

    neighborhood_medians = result.groupby("Neighborhood")[
        "Lot Frontage"
    ].transform("median")

    result["Lot Frontage"] = result["Lot Frontage"].fillna(
        neighborhood_medians
    )

    result["Lot Frontage"] = result["Lot Frontage"].fillna(
        global_median
    )

    return result

def cost_table(before: pd.Series, after: pd.Series, other: pd.Series) -> pd.Series:
    """Compare standard deviation and correlation before and after imputation."""
    return pd.Series({
        "SD Before": before.std(),
        "SD After": after.std(),
        "Correlation Before": before.corr(other),
        "Correlation After": after.corr(other),
    })


'''if __name__ == "__main__":
    df = pd.read_csv(sys.argv[1])
    raise NotImplementedError'''

def plot_imputations(df: pd.DataFrame) -> None:
    global_df = global_median_impute(df)
    neighborhood_df = neighborhood_median_impute(df)

    Path("reports/figures").mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    datasets = [
        (df["Lot Frontage"].dropna(), "Observed"),
        (global_df["Lot Frontage"], "Global Median"),
        (neighborhood_df["Lot Frontage"], "Neighborhood Median"),
    ]

    for ax, (values, title) in zip(axes, datasets):
        ax.hist(values, bins=30, edgecolor="black")
        ax.set_title(title)
        ax.set_xlabel("Lot Frontage")
        ax.set_ylabel("Count")
        ax.set_xlim(0, 320)

    fig.tight_layout()
    fig.savefig("reports/figures/imputation_comparison.png", dpi=150)
    plt.close(fig)

    print("Saved: reports/figures/imputation_comparison.png")
    
def main():
    df = pd.read_csv(
        sys.argv[1],
        keep_default_na=False,
        na_values=[""],
    )

    global_df = global_median_impute(df)
    neighborhood_df = neighborhood_median_impute(df)

    print("\n=== Global Median Imputation ===")
    print(
        cost_table(
            df["Lot Frontage"],
            global_df["Lot Frontage"],
            df["Lot Area"],
        ).round(4)
    )

    print("\n=== Neighborhood Median Imputation ===")
    print(
        cost_table(
            df["Lot Frontage"],
            neighborhood_df["Lot Frontage"],
            df["Lot Area"],
        ).round(4)
    )

    plot_imputations(df)


if __name__ == "__main__":
    main()