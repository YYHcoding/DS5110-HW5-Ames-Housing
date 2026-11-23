# HW5 Report — Ames Housing Data Quality and Leakage

## 1. Provenance

Dean De Cock’s [Ames Housing data](https://jse.amstat.org/v19n3/decock/AmesHousing.txt) (2011) were accessed on November 19, 2026. The raw file contains 2,930 sales and 82 columns. The downloader preserves any existing raw copy. The README links the data dictionary and JSE’s teaching-use policy.

## 2. Validation

The raw file failed the two year checks listed in Table 1. We set the offending cells to missing and retained all 2,930 rows. The resulting data pass the schema, range, category, and cross-column checks.

## 3. Sentinels and structural absence

We loaded the TSV with pandas defaults and again with `keep_default_na=False, na_values=[""]`. The default load masked the literal `NA` and `None` values listed in Table 2. The dictionary identifies all 14 literal-`NA` columns as structural absence. We recoded their `NA` to the category `None`, preserved the existing veneer category `None`, and kept blank cells missing. Recorded zeros remain numeric, with their field-specific meanings in Table 3.

## 4. Keys and duplicates

We chose `Order` as the sale key because it is the observation number. `PID` identifies the parcel. Each key had zero missing values and zero duplicates, and there were zero exact duplicate rows. The dictionary-based neighborhood lookup matched all 2,930 rows in a validated many-to-one merge. The analysis retains the original neighborhood codes.

## 5. Missingness mechanism

Frontage is missing in 490 sales (16.72%), and masonry veneer area is missing in 23 (0.78%). Table 4 compares the two groups for each variable. Frontage is missing for 48.9% of cul-de-sac lots versus 12.8% of inside lots, evidence against MCAR. MAR conditional on observed property characteristics is a working assumption. If frontage is MNAR, assessors might omit measurements below a minimum usable frontage for wedge-shaped lots, even among lots with the same recorded layout and area.

Missing veneer areas occur in homes with higher median quality and sale price. This is descriptive evidence against MCAR, with only 23 missing cases. MAR is plausible if recording varies with observed house quality or value. The comparisons cannot establish MAR or rule out dependence on the unseen measurements themselves.

## 6. Imputation strategy

I choose the neighborhood median because frontage plausibly depends on observed local development patterns under MAR. It preserves more of the observed dispersion and association with lot area than the global median (Table 5 and Figure 1). The global median is the fallback when training data contain no measured frontage for a neighborhood. Both fills compress variation.

## 7. Leakage-safe evaluation

Linear regression predicts log sale price with 11 numeric predictors and five shuffled folds (seed 5110). Table 6 reports log-scale RMSE.

1. **Which estimate is valid, and how do the others leak?** C fits neighborhood medians only on the training fold. A uses the target to define the imputation groups. B uses validation-fold frontage measurements in the full-table medians.
2. **Which variant cannot price an unsold house?** A requires the realized sale price to assign a missing frontage to a price quintile.
3. **How large is B versus C, and why?** C is higher by 0.00001658 on the log-price RMSE scale. Most frontages are measured, and removing one fold typically changes a neighborhood median only modestly. Those factors can explain the small change even though B leaks.

## 8. Limits

The missing measurements prevent direct verification of fill accuracy. The audit provides no causal evidence, and random cross-validation on Ames sales does not establish performance in another market or period.

## Tables and figure

**Table 1. Raw validation failures**

| Rule | Count | Repair |
|---|---:|---|
| Year Built > Yr Sold | 1 | Set Year Built to missing |
| Year Remod/Add < Year Built | 1 | Set Year Remod/Add to missing |

**Table 2. Literal tokens masked by default pandas parsing**

| Raw token | Columns (counts) | Dictionary meaning |
|---|---|---|
| NA | Alley (2,732) | No alley access |
| NA | Bsmt Qual, Bsmt Cond, Bsmt Exposure, BsmtFin Type 1, BsmtFin Type 2 (79 each) | No basement |
| NA | Fireplace Qu (1,422) | No fireplace |
| NA | Garage Type, Garage Finish (157 each), Garage Qual, Garage Cond (158 each) | No garage, as defined for these fields |
| NA | Pool QC (2,917) | No pool |
| NA | Fence (2,358) | No fence |
| NA | Misc Feature (2,824) | No listed miscellaneous feature |
| None | Mas Vnr Type (1,752) | No masonry veneer |
| Empty cell | Present across multiple fields | Unrecorded value; keep missing |

**Table 3. Meaning of numeric zeros in the source**

| Field(s) containing zero | Why zero is retained |
|---|---|
| Mas Vnr Area | Zero measured veneer area indicates absence; an empty cell records no measurement. |
| BsmtFin SF 1, BsmtFin SF 2, Bsmt Unf SF | Zero is the area of the corresponding portion. A basement can have zero area of one portion. |
| Total Bsmt SF, 2nd Flr SF, Low Qual Fin SF | Zero square feet means the corresponding space is absent. |
| Bsmt Full Bath, Bsmt Half Bath | Zero is a count of bathrooms of that type, including homes without a basement. |
| Full Bath, Half Bath, Bedroom AbvGr, Kitchen AbvGr | Zero is the recorded count in the relevant scope. |
| Fireplaces | Zero counts no fireplaces. |
| Garage Cars, Garage Area | Zero capacity and area describe absent garages. |
| Wood Deck SF, Open Porch SF, Enclosed Porch, 3Ssn Porch, Screen Porch, Pool Area | Zero square feet means the specified amenity is absent. |
| Misc Val | Zero is the recorded dollar contribution of miscellaneous features. |

**Table 4. Comparisons by missingness**

| Target | Observed column and summary | Target observed | Target missing |
|---|---|---:|---:|
| Lot Frontage | Lot Area, median sq ft | 9,248.5 | 10,397.5 |
| Lot Frontage | SalePrice, median USD | 157,500 | 173,000 |
| Lot Frontage | Overall Qual, median | 6 | 6 |
| Lot Frontage | Lot Config, cul-de-sac share | 92/2,440 (3.8%) | 88/490 (18.0%) |
| Mas Vnr Area | Lot Area, median sq ft | 9,430 | 9,965 |
| Mas Vnr Area | SalePrice, median USD | 160,000 | 207,500 |
| Mas Vnr Area | Overall Qual, median | 6 | 7 |
| Mas Vnr Area | Lot Config, cul-de-sac share | 178/2,907 (6.1%) | 2/23 (8.7%) |

**Table 5. Imputation cost**

| Metric | Observed | Global median | Neighborhood median |
|---|---:|---:|---:|
| Standard deviation | 23.3653 | 21.3264 | 21.7185 |
| Correlation with Lot Area | 0.4913 | 0.3628 | 0.3891 |

**Table 6. Cross-validation results**

| Method | Mean RMSE | SD |
|---|---:|---:|
| Baseline, foldwise global median | 0.1589 | 0.0140 |
| A, price quintile before CV | 0.1588 | 0.0141 |
| B, neighborhood before CV | 0.15888687 | 0.0140 |
| C, foldwise neighborhood | 0.15890345 | 0.0140 |

![Figure 1. Lot Frontage distributions before and after each imputation strategy](figures/imputation_comparison.png)
