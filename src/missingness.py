"""Part 5: evidence about the missingness mechanism (notebook §4.1 pattern)."""
import sys
import pandas as pd



def analyze_missingness(df: pd.DataFrame) -> None:
    # 1. Lot Frontage missing indicator
    df = df.copy()
    df["LF_missing"] = df["Lot Frontage"].isna()

    # 2. Missing fractions
    for col in ["Lot Frontage", "Garage Yr Blt"]:
        count = df[col].isna().sum()
        fraction = df[col].isna().mean()
        print(f"{col}: {count} missing ({fraction:.2%})")

    # 3. Numeric comparisons
    print("\nNumeric comparisons:")
    print(
        df.groupby("LF_missing")[
            ["Lot Area", "SalePrice", "Year Built"]
        ].median()
    )

    # 4. Categorical comparison
    print("\nNeighborhood comparisons:")
    neighborhood = df.groupby("Neighborhood")["LF_missing"].agg(
        ["size", "sum", "mean"]
    )
    neighborhood.columns = ["Total", "Missing", "Missing_Rate"]
    neighborhood["Missing_Rate"] *= 100

    print(
        neighborhood.sort_values(
            "Missing_Rate", ascending=False
        ).round(1)
    )

    # 5. Garage structural missingness
    print("\nGarage missingness:")
    print(
        pd.crosstab(
            df["Garage Type"],
            df["Garage Yr Blt"].isna()
        )
    )


def compare_groups(
    df: pd.DataFrame,
    col: str,
    observed_cols: list[str]
) -> pd.DataFrame:
    """Compare observed and missing groups for a target column."""
    missing = df[col].isna()
    rows = []

    for feature in observed_cols:
        if pd.api.types.is_numeric_dtype(df[feature]):
            observed = df.loc[~missing, feature].median()
            missing_group = df.loc[missing, feature].median()
        else:
            observed = df.loc[~missing, feature].mode(dropna=True)
            missing_group = df.loc[missing, feature].mode(dropna=True)

            observed = observed.iloc[0] if not observed.empty else None
            missing_group = (
                missing_group.iloc[0] if not missing_group.empty else None
            )

        rows.append({
            "Feature": feature,
            "Observed_Group": observed,
            "Missing_Group": missing_group,
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = pd.read_csv(
        sys.argv[1],
        keep_default_na=False,
        na_values=[""],
    )

    analyze_missingness(df)

    print("\n=== Lot Frontage: Group Comparison ===")
    comparison = compare_groups(
        df,
        "Lot Frontage",
        ["Lot Area", "SalePrice", "Year Built", "Neighborhood"],
    )
    print(comparison.to_string(index=False))
