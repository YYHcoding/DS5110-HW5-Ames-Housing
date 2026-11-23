# HW5: Ames Housing quality audit

## How to run

```
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make all
```


## Provenance (Part 1)

| Item | Value |
| --- | --- |
| Source URL | https://jse.amstat.org/v19n3/decock/AmesHousing.txt |
| Downloaded on | 2026-11-19 |
| Citation | De Cock, D. (2011). Ames, Iowa: Alternative to the Boston Housing Data as an End of Semester Regression Project. Journal of Statistics Education, 19(3). |
| Data dictionary | https://jse.amstat.org/v19n3/decock/DataDocumentation.txt |
| Terms of use | JSE permits teaching use without prior permission with attribution (dataset, contributor and access date), and requires the contributor’s consent and notification of the editor for use in published work ([JSE data-use policy](https://jse.amstat.org/jse_users.htm)). |
| Rows, columns on arrival | 2,930 rows, 82 columns |

## Features used in Part 7

The linear regression experiments use 11 numeric predictors:

- `Lot Frontage` — street frontage, the primary variable investigated for missingness and imputation.
- `Lot Area` — property lot size.
- `Overall Qual` — overall material and finish quality.
- `Overall Cond` — overall property condition.
- `Year Built` — original construction year.
- `Year Remod/Add` — remodeling or addition year.
- `Gr Liv Area` — above-ground living area.
- `Total Bsmt SF` — total basement area.
- `Garage Cars` — garage capacity.
- `Full Bath` — number of full bathrooms.
- `TotRms AbvGrd` — total above-ground rooms.

These variables represent lot characteristics, building quality, age, size, and amenities. The prediction target is `log(SalePrice)`, which is excluded from the predictor matrix. Five-fold shuffled cross-validation uses `random_state=5110`.

For Method C, `Neighborhood` is additionally passed to the preprocessing pipeline to learn neighborhood-specific frontage medians within each training fold. It is dropped before fitting the linear regression model.

## AI assistance

OpenAI ChatGPT (GPT-6) was used to assist with Python implementation, debugging, interpretation of statistical results, and report drafting.

Assistance covered `src/download.py`, `src/validate.py`, `src/clean.py`, `src/missingness.py`, `src/impute.py`, `src/evaluate.py`, `Makefile`, `README.md`, and `reports/report.md`.

The scripts were executed locally, and their outputs were inspected during development. The submitted work remains subject to the author's review and verification.
