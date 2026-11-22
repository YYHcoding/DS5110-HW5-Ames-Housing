
# DS5110 HW5 — Run everything with: make all

PY    := python
RAW   := data/raw/AmesHousing.txt
CLEAN := data/processed/ames_clean.csv

.PHONY: all validate analysis clean

all: validate analysis

$(RAW):
	$(PY) src/download.py $(RAW)

$(CLEAN): $(RAW) src/clean.py src/validate.py
	mkdir -p data/processed
	$(PY) src/clean.py $(RAW) $(CLEAN)

# Raw validation must fail; cleaned validation must pass.
validate: $(RAW) $(CLEAN)
	! $(PY) src/validate.py $(RAW) --raw
	$(PY) src/validate.py $(CLEAN)

analysis: $(CLEAN) src/missingness.py src/impute.py src/evaluate.py
	mkdir -p reports/figures reports/results
	$(PY) -m src.missingness $(CLEAN)
	$(PY) -m src.impute $(CLEAN)
	$(PY) -m src.evaluate
	@echo "Analysis completed. See reports/report.md."

clean:
	rm -rf data/processed reports/figures reports/results
