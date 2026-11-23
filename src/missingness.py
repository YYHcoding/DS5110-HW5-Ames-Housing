"""Part 5: evidence about the missingness mechanism (notebook §4.1 pattern)."""
import sys
import pandas as pd



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

    for target in ["Lot Frontage", "Mas Vnr Area"]:
        missing = df[target].isna()
        print(f"\n{target}: {missing.sum()} missing ({missing.mean():.2%})")
        comparison = compare_groups(
            df, target, ["Lot Area", "SalePrice", "Overall Qual", "Lot Config"]
        )
        print(comparison.to_string(index=False))
        print(pd.crosstab(df["Lot Config"], missing))
