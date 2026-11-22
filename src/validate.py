"""Part 2: validation as code. Raise once, listing every failure (notebook §1)."""
import sys
import pandas as pd


class ValidationError(Exception):
    pass


# Each rule needs a source. Put it in the comment.
RANGES = {
    # Source: physical meaning of lot area (square feet).
    "Lot Area": (1, None),

    # Source: physical meaning of street frontage (linear feet).
    "Lot Frontage": (1, None),

    # Source: positive recorded sale transaction amount.
    "SalePrice": (1, None),

    # Source: construction year and study period.
    "Year Built": (1800, 2010),

    # Source: Ames Housing study period, 2006–2010.
    "Yr Sold": (2006, 2010),

    # Source: Ames Housing data dictionary, Overall Qual.
    "Overall Qual": (1, 10),

    # Source: Ames Housing data dictionary, Overall Cond.
    "Overall Cond": (1, 10),

    # Source: nonnegative count of full bathrooms.
    "Full Bath": (0, None),
}
ALLOWED = {
    # Source: Ames Housing DataDocumentation.txt
    "Street": {"Grvl", "Pave"},
    "Lot Shape": {"Reg", "IR1", "IR2", "IR3"},
    "Central Air": {"Y", "N"},
    "Paved Drive": {"Y", "P", "N"},
}
# Expected numeric columns based on the Ames Housing data dictionary.
# MS SubClass is a categorical code stored numerically.
NUMERIC_COLUMNS = {
    "Order", "PID", "MS SubClass",
    "Lot Frontage", "Lot Area",
    "Overall Qual", "Overall Cond",
    "Year Built", "Year Remod/Add",
    "Mas Vnr Area",
    "BsmtFin SF 1", "BsmtFin SF 2",
    "Bsmt Unf SF", "Total Bsmt SF",
    "1st Flr SF", "2nd Flr SF",
    "Low Qual Fin SF", "Gr Liv Area",
    "Bsmt Full Bath", "Bsmt Half Bath",
    "Full Bath", "Half Bath",
    "Bedroom AbvGr", "Kitchen AbvGr",
    "TotRms AbvGrd", "Fireplaces",
    "Garage Yr Blt", "Garage Cars",
    "Garage Area", "Wood Deck SF",
    "Open Porch SF", "Enclosed Porch",
    "3Ssn Porch", "Screen Porch",
    "Pool Area", "Misc Val",
    "Mo Sold", "Yr Sold", "SalePrice",
}

TEXT_COLUMNS = {
    "MS Zoning", "Street", "Alley",
    "Lot Shape", "Land Contour",
    "Utilities", "Lot Config", "Land Slope",
    "Neighborhood", "Condition 1", "Condition 2",
    "Bldg Type", "House Style",
    "Roof Style", "Roof Matl",
    "Exterior 1st", "Exterior 2nd",
    "Mas Vnr Type", "Exter Qual", "Exter Cond",
    "Foundation", "Bsmt Qual", "Bsmt Cond",
    "Bsmt Exposure", "BsmtFin Type 1",
    "BsmtFin Type 2", "Heating", "Heating QC",
    "Central Air", "Electrical", "Kitchen Qual",
    "Functional", "Fireplace Qu",
    "Garage Type", "Garage Finish",
    "Garage Qual", "Garage Cond",
    "Paved Drive", "Pool QC", "Fence",
    "Misc Feature", "Sale Type", "Sale Condition",
}

EXPECTED_COLUMNS = NUMERIC_COLUMNS | TEXT_COLUMNS


def check_schema(df: pd.DataFrame) -> list[str]:
    errors = []

    actual_columns = set(df.columns)

    missing_columns = EXPECTED_COLUMNS - actual_columns
    extra_columns = actual_columns - EXPECTED_COLUMNS

    if missing_columns:
        errors.append(f"Missing columns: {sorted(missing_columns)}")

    if extra_columns:
        errors.append(f"Unexpected columns: {sorted(extra_columns)}")

    if df.columns.duplicated().any():
        errors.append("Duplicate column names detected")

    for column in NUMERIC_COLUMNS & actual_columns:
        if not pd.api.types.is_numeric_dtype(df[column]):
            errors.append(
                f"{column}: expected numeric, got {df[column].dtype}"
            )

    for column in TEXT_COLUMNS & actual_columns:
        if not (
            pd.api.types.is_string_dtype(df[column])
            or pd.api.types.is_object_dtype(df[column])
        ):
            errors.append(
                f"{column}: expected text, got {df[column].dtype}"
            )

    return errors


def check_ranges(df: pd.DataFrame) -> list[str]:
    errors = []

    for column, (lower, upper) in RANGES.items():
        values = pd.to_numeric(df[column], errors="coerce")

        bad = pd.Series(False, index=df.index)

        if lower is not None:
            bad = bad | (values < lower)

        if upper is not None:
            bad = bad | (values > upper)

        count = int(bad.sum())

        if count > 0:
            errors.append(
                f"{column}: {count} values outside "
                f"allowed range [{lower}, {upper}]"
            )

    return errors


def check_allowed(df: pd.DataFrame) -> list[str]:
    errors = []

    for column, allowed_values in ALLOWED.items():
        # Ignore genuine missing values; check non-missing categories.
        invalid = df[column].notna() & ~df[column].isin(allowed_values)

        if invalid.any():
            bad_values = df.loc[invalid, column].value_counts().to_dict()

            errors.append(
                f"{column}: {int(invalid.sum())} invalid values; "
                f"details: {bad_values}"
            )

    return errors


def check_cross_column(df: pd.DataFrame) -> list[str]:
    errors = []

    # A house should not be built after its recorded sale year.
    bad_built = df["Year Built"] > df["Yr Sold"]

    if bad_built.any():
        errors.append(
            f"Year Built > Yr Sold: {bad_built.sum()} violations"
        )

    # Remodeling year should not precede construction year.
    bad_remod = df["Year Remod/Add"] < df["Year Built"]

    if bad_remod.any():
        errors.append(
            f"Year Remod/Add < Year Built: {bad_remod.sum()} violations"
        )

    return errors


def validate(df: pd.DataFrame) -> pd.DataFrame:
    errors = check_schema(df) + check_ranges(df) + check_allowed(df) + check_cross_column(df)
    if errors:
        raise ValidationError("\n".join(errors))
    return df


if __name__ == "__main__":
    path = sys.argv[1]
    raw = "--raw" in sys.argv
    df = pd.read_csv(path, sep="\t" if raw else ",", keep_default_na=False, na_values=[""])
    try:
        validate(df)
        print(f"PASS {path}")
    except ValidationError as e:
        print(f"FAIL {path}\n{e}")
        sys.exit(1)
