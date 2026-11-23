"""Part 7: variants A, B, C with the given model (notebook §6.1 to §6.3)."""
import sys
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from src.impute import neighborhood_median_impute
from sklearn.base import BaseEstimator, TransformerMixin
FEATURES = [
    "Lot Frontage",
    "Lot Area",
    "Overall Qual",
    "Overall Cond",
    "Year Built",
    "Year Remod/Add",
    "Gr Liv Area",
    "Total Bsmt SF",
    "Garage Cars",
    "Full Bath",
    "TotRms AbvGrd",
]
class NeighborhoodMedianImputer(BaseEstimator, TransformerMixin):

    def fit(self, X, y=None):
        self.global_median_ = X["Lot Frontage"].median()

        self.neighborhood_medians_ = (
            X.groupby("Neighborhood")["Lot Frontage"].median()
        )

        return self

    def transform(self, X):
        result = X.copy()

        neighborhood_values = result["Neighborhood"].map(
            self.neighborhood_medians_
        )

        result["Lot Frontage"] = (
            result["Lot Frontage"]
            .fillna(neighborhood_values)
            .fillna(self.global_median_)
        )

        return result.drop(columns=["Neighborhood"])

def evaluate_baseline(df: pd.DataFrame) -> None:
    X = df[FEATURES]
    y = np.log(df["SalePrice"])

    pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", LinearRegression()),
    ])

    cv = KFold(
        n_splits=5,
        shuffle=True,
        random_state=5110,
    )

    scores = cross_val_score(
        pipeline,
        X,
        y,
        cv=cv,
        scoring="neg_root_mean_squared_error",
    )

    rmse = -scores

    print("Fold RMSE:", rmse.round(4))
    print("Mean RMSE:", round(rmse.mean(), 8))
    print("SD RMSE:", round(rmse.std(), 4))
NUMERIC_FEATURES: list[str] = []   # 8 to 15 columns, including "Lot Frontage"
CV = KFold(n_splits=5, shuffle=True, random_state=5110)


def rmse(estimator, X: pd.DataFrame, y: pd.Series) -> float:
    return -cross_val_score(estimator, X, y, cv=CV, scoring="neg_root_mean_squared_error").mean()


'''if __name__ == "__main__":
    df = pd.read_csv(sys.argv[1])
    y = np.log(df["SalePrice"])
    raise NotImplementedError'''

def evaluate_method_b(df: pd.DataFrame) -> None:
    filled = neighborhood_median_impute(df)

    X = filled[FEATURES]
    y = np.log(filled["SalePrice"])

    pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", LinearRegression()),
    ])

    cv = KFold(
        n_splits=5,
        shuffle=True,
        random_state=5110,
    )

    scores = cross_val_score(
        pipeline,
        X,
        y,
        cv=cv,
        scoring="neg_root_mean_squared_error",
    )

    rmse = -scores

    print("Method B Fold RMSE:", rmse.round(4))
    print("Method B Mean RMSE:", round(rmse.mean(), 8))
    print("Method B SD RMSE:", round(rmse.std(), 4))
def evaluate_method_c(df: pd.DataFrame) -> None:
    X = df[FEATURES + ["Neighborhood"]]
    y = np.log(df["SalePrice"])

    pipeline = Pipeline([
        ("neighborhood_imputer", NeighborhoodMedianImputer()),
        ("remaining_imputer", SimpleImputer(strategy="median")),
        ("model", LinearRegression()),
    ])

    cv = KFold(
        n_splits=5,
        shuffle=True,
        random_state=5110,
    )

    scores = cross_val_score(
        pipeline,
        X,
        y,
        cv=cv,
        scoring="neg_root_mean_squared_error",
    )

    rmse = -scores

    print("Method C Fold RMSE:", rmse.round(4))
    print("Method C Mean RMSE:", round(rmse.mean(), 8))
    print("Method C SD RMSE:", round(rmse.std(), 4))

def evaluate_method_a(df: pd.DataFrame) -> None:
    result = df.copy()

    # Create five price groups using the full dataset.
    price_groups = pd.qcut(
        result["SalePrice"],
        q=5,
        labels=False,
        duplicates="drop",
    )

    # Compute frontage medians using target-conditioned groups.
    group_medians = result.groupby(price_groups)[
        "Lot Frontage"
    ].transform("median")

    result["Lot Frontage"] = (
        result["Lot Frontage"]
        .fillna(group_medians)
        .fillna(result["Lot Frontage"].median())
    )

    X = result[FEATURES]
    y = np.log(result["SalePrice"])

    pipeline = Pipeline([
        ("remaining_imputer", SimpleImputer(strategy="median")),
        ("model", LinearRegression()),
    ])

    cv = KFold(
        n_splits=5,
        shuffle=True,
        random_state=5110,
    )

    scores = cross_val_score(
        pipeline,
        X,
        y,
        cv=cv,
        scoring="neg_root_mean_squared_error",
    )

    rmse = -scores

    print("Method A Fold RMSE:", rmse.round(4))
    print("Method A Mean RMSE:", round(rmse.mean(), 8))
    print("Method A SD RMSE:", round(rmse.std(), 4))

def main():
    df = pd.read_csv(
        "data/processed/ames_clean.csv",
        keep_default_na=False,
        na_values=[""],
    )
    print("\n=== Baseline ===")
    evaluate_baseline(df)

    print("\n=== Method A ===")
    evaluate_method_a(df)

    print("\n=== Method B ===")
    evaluate_method_b(df)

    print("\n=== Method C ===")
    evaluate_method_c(df)


if __name__ == "__main__":
    main()