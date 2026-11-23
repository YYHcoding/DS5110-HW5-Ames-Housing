"""Parts 3 and 4: decode true missing values, keep structural "none", check keys."""
import sys
import pandas as pd
import numpy as np

# Columns where the dictionary defines "NA" as "none", not "unknown".
NA_MEANS_NONE = [
    "Pool QC",
    "Misc Feature",
    "Alley",
    "Fence",
    "Fireplace Qu",
    "Garage Qual",
    "Garage Cond",
    "Garage Type",
    "Garage Finish",
    "Bsmt Qual",
    "Bsmt Cond",
    "Bsmt Exposure",
    "BsmtFin Type 1",
    "BsmtFin Type 2",
]
NEIGHBORHOOD_NAMES = {
    "Blmngtn": "Bloomington Heights",
    "Blueste": "Bluestem",
    "BrDale": "Briardale",
    "BrkSide": "Brookside",
    "ClearCr": "Clear Creek",
    "CollgCr": "College Creek",
    "Crawfor": "Crawford",
    "Edwards": "Edwards",
    "Gilbert": "Gilbert",
    "Greens": "Greens",
    "GrnHill": "Green Hills",
    "IDOTRR": "Iowa DOT and Rail Road",
    "Landmrk": "Landmark",
    "MeadowV": "Meadow Village",
    "Mitchel": "Mitchell",
    "NAmes": "North Ames",
    "NoRidge": "Northridge",
    "NPkVill": "Northpark Villa",
    "NridgHt": "Northridge Heights",
    "NWAmes": "Northwest Ames",
    "OldTown": "Old Town",
    "SWISU": "South & West of Iowa State University",
    "Sawyer": "Sawyer",
    "SawyerW": "Sawyer West",
    "Somerst": "Somerset",
    "StoneBr": "Stone Brook",
    "Timber": "Timberland",
    "Veenker": "Veenker",
}

def load_raw(path: str) -> pd.DataFrame:
    """Load with keep_default_na=False so that "NA" and "None" survive as strings."""
    default = pd.read_csv(path, sep="\t")
    preserved = pd.read_csv(
        path,
        sep="\t",
        keep_default_na=False,
        na_values=[""],
    )
    for column in preserved.columns:
        masked = preserved.loc[default[column].isna() & preserved[column].notna(), column]
        if not masked.empty:
            print(f"{column}: default masks {masked.value_counts().to_dict()}")
    return preserved

def decode_missing(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    for column in NA_MEANS_NONE:
        df[column] = df[column].replace("NA", "None")

    return df


def check_keys(df: pd.DataFrame) -> None:
    for key in ["Order", "PID"]:
        if key not in df.columns:
            raise ValueError(f"Missing key column: {key}")

        missing = df[key].isna().sum()
        duplicates = df[key].duplicated().sum()

        if missing > 0 or duplicates > 0:
            raise ValueError(
                f"{key}: {missing} missing, "
                f"{duplicates} duplicates"
            )

    print("PASS: Order and PID each have zero missing or duplicate keys")
    print(f"Exact duplicate rows: {df.duplicated().sum()}")

def join_neighborhood(df: pd.DataFrame) -> pd.DataFrame:
    lookup = pd.DataFrame(
        list(NEIGHBORHOOD_NAMES.items()),
        columns=["Neighborhood", "Neighborhood Full Name"]
    )

    merged = df.merge(
        lookup,
        on="Neighborhood",
        how="left",
        validate="many_to_one"
    )

    if len(merged) != len(df):
        raise ValueError("Join changed the number of rows")

    if merged["Neighborhood Full Name"].isna().any():
        raise ValueError("Some neighborhoods were not matched")

    print(f"Neighborhood join: {len(df)} input and {len(merged)} output rows")
    return merged

def clean_year_conflicts(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    
    invalid_built = result["Year Built"] > result["Yr Sold"]
    print("Invalid Year Built:", invalid_built.sum())
    result.loc[invalid_built, "Year Built"] = np.nan

    
    invalid_remod = (
        result["Year Remod/Add"] < result["Year Built"]
    )
    print("Invalid Year Remod/Add:", invalid_remod.sum())
    result.loc[invalid_remod, "Year Remod/Add"] = np.nan

    return result
if __name__ == "__main__":
    raw_path, out_path = sys.argv[1], sys.argv[2]

    df = decode_missing(load_raw(raw_path))
    check_keys(df)

    # Validate the neighborhood lookup and preserve the original schema.
    df = join_neighborhood(df)
    df = df.drop(columns=["Neighborhood Full Name"])

    df = clean_year_conflicts(df)

    df.to_csv(out_path, index=False)