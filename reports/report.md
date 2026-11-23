# HW5 Report — Ames Housing Data Quality and Leakage

## 1. Provenance

This analysis uses the Ames Housing dataset described by De Cock (2011), *Ames, Iowa: Alternative to the Boston Housing Data as an End of Semester Regression Project*, *Journal of Statistics Education*, 19(3). The original tab-delimited dataset was downloaded on November 19, 2026, from https://jse.amstat.org/v19n3/decock/AmesHousing.txt. The accompanying data dictionary is available at https://jse.amstat.org/v19n3/decock/DataDocumentation.txt.

The dataset contains 2,930 observations and 82 original columns. The download script does not overwrite an existing raw file. Applicable reuse terms have not yet been independently verified.

## 2. Validation: Failures on the Raw File

Validation covered the 82-column schema, numeric ranges, categorical constraints, and cross-column consistency. The raw dataset failed two checks:

| Rule | Violations |
|---|---:|
| Year Built > Yr Sold | 1 |
| Year Remod/Add < Year Built | 1 |

The cleaning procedure marks the conflicting year values as missing rather than inventing replacements. All 2,930 observations are retained, and the processed dataset passes the implemented validation checks. Passing validation does not guarantee that every recorded value is correct.

## 3. Sentinels and Structural Absence

The dataset distinguishes structural absence from genuinely unknown values. In selected basement, garage, and amenity fields, `"NA"` means that a feature does not exist, rather than that its value is unknown. These structural markers were converted to the explicit category `"None"`.

Empty cells remain missing values. The loading procedure uses `keep_default_na=False` and `na_values=[""]` to preserve meaningful `"NA"` strings during initial import. Structural absence is also distinct from a recorded numeric zero.

## 4. Keys and Duplicates

Both `Order` and `PID` were checked for missing and duplicate identifiers. Each was unique across all 2,930 observations, and no duplicate rows were found.

A neighborhood code-to-name lookup was prepared with a `many_to_one` merge validation rule. The lookup is intended to preserve the original observation count and ensure that every neighborhood code has a corresponding name. The modeling dataset retains the original `Neighborhood` codes.

## 5. Missingness Mechanism

`Lot Frontage` is missing in 490 observations (16.72%), while `Garage Yr Blt` is missing in 159 (5.43%). Of the latter, 157 observations have no garage, representing structural absence; two detached-garage records have unknown construction years.

For `Lot Frontage`, median `Lot Area` differs between observed and missing groups (9,248.5 versus 10,397.5), as does median `SalePrice` ($157,500 versus $173,000). Missingness also varies by neighborhood.

These associations argue against a simple MCAR assumption. MAR is a plausible working assumption conditional on observed characteristics, but it cannot be established from these comparisons. MNAR cannot be excluded.

## 6. Imputation Strategy and Defense

Two methods were compared for `Lot Frontage`: global-median imputation and neighborhood-median imputation.

| Metric | Observed | Global Median | Neighborhood Median |
|---|---:|---:|---:|
| Standard deviation | 23.3653 | 21.3264 | 21.7185 |
| Correlation with Lot Area | 0.4913 | 0.3628 | 0.3891 |

![Lot Frontage imputation comparison](figures/imputation_comparison.png)

Neighborhood-median imputation reflects local differences and retains slightly more variation and correlation with `Lot Area` than global-median imputation. A global-median fallback handles neighborhoods lacking observed frontage values. Both methods reduce dispersion, however, and neither can recover unknown true values with certainty. These descriptive statistics do not establish imputation accuracy. For predictive evaluation, imputation parameters must be estimated from training folds only.

## 7. Leakage-Safe Evaluation

The prediction target was `log(SalePrice)`. Linear regression used 11 numeric predictors and five-fold shuffled cross-validation (`random_state=5110`). Performance was measured using RMSE on the log-price scale. All experiments used the cleaned dataset (`data/processed/ames_clean.csv`).

| Method | Mean RMSE | SD |
|---|---:|---:|
| Baseline: median imputation inside pipeline | 0.1589 | 0.0140 |
| A: SalePrice-quintile imputation before CV | 0.1588 | 0.0141 |
| B: neighborhood imputation before CV | 0.1589 | 0.0140 |
| C: neighborhood imputation inside CV pipeline | 0.1589 | 0.0140 |

Method A leaks target information because `SalePrice` determines the imputed frontage values. Method B estimates neighborhood medians using the full dataset before cross-validation, allowing validation-fold information into preprocessing. Method C learns neighborhood medians within each training fold, avoiding this preprocessing leakage.

The reported RMSE differences are negligible. Method A's slightly lower RMSE does not establish better predictive performance or justify target leakage.

## 8. What This Data Cannot Tell You

Observed associations cannot establish causality or prove a missingness mechanism. Because the true missing frontage values are unavailable, imputation accuracy cannot be directly verified. Results from Ames also cannot establish generalization to other housing markets. Cross-validation estimates performance under the selected modeling and sampling assumptions; it does not guarantee future predictive accuracy.