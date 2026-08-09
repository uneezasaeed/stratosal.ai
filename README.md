# StratoSal AI

**Climate-driven infectious disease early warning for Punjab, Pakistan.**

StratoSal AI converts ERA5 satellite reanalysis climate data into district-level
dengue transmission risk, with the aim of giving district health officers a
4 to 6 week window to act before cases reach clinics.

Live prototype: https://uneezasaeed.github.io/stratosal.ai/

---

## What this is

An early-stage, open-source prototype. It reads 91 months of ERA5 climate data
(January 2019 to July 2026) across 437 grid points over Punjab and produces a
transparent climate suitability classification for ten pilot districts.

Temperature between 26 and 35°C, relative humidity above 65 percent, and monsoon
rainfall sufficient to leave standing water together define the conditions in
which *Aedes aegypti* populations expand. Those conditions appear in the climate
record weeks before cases appear in clinics.

## What this is not

This is **not** a trained machine learning classifier, and no accuracy figure is
claimed. The current method is a rule-based index with thresholds drawn from the
published transmission literature.

Validation is by seasonal concordance: the suitability index peaks in August,
ahead of Punjab's recorded September to October case peak. Interannual validation
against seven years of provincial case totals is not statistically significant,
because annual totals are dominated by population immunity, serotype turnover,
vector-control intensity and surveillance coverage rather than by climate.
Isolating the climate signal requires district-level monthly case data. Obtaining
that data is the primary partnership objective of this pilot.

## Repository structure

| Path | Purpose |
|---|---|
| `index.html` | Prototype interface, reads from `data/` |
| `data/forecast.json` | ERA5 output, written by the notebook |
| `data/dengue.json` | Punjab dengue surveillance, 2019 to 2026 |
| `data/SOURCES.md` | Citation for every figure displayed |
| `notebooks/stratosal_era5.py` | Extraction and forecast builder |
| `LICENSE` | MIT |

No figure on the site is entered by hand. Every value is read from the data
files, which makes a mismatch between the page and the underlying data
structurally impossible.

## Reproducing the data

1. Create a free account at https://cds.climate.copernicus.eu
2. Accept the licence for the `reanalysis-era5-single-levels-monthly-means` dataset
3. Open `notebooks/stratosal_era5.py` in Google Colab and run the cells in order
4. The notebook writes `forecast.json`, which replaces `data/forecast.json`

The notebook hard-stops if the grid is not 19 × 23 = 437 points, if precipitation
values fall outside a physically plausible range, or if the output would contain
`NaN`.

## Data sources

- **Climate:** ERA5 monthly means, ECMWF, distributed via the Copernicus Climate
  Change Service Climate Data Store. Relative humidity derived from 2 m
  temperature and 2 m dewpoint using the Magnus formula (Alduchov and Eskridge, 1996).
- **Disease:** National Institute of Health Islamabad, WHO, and the peer-reviewed
  literature. Full citations in [`data/SOURCES.md`](data/SOURCES.md).

## Method foundation

> Shabbir, W., Pilz, J. and Naeem, A. (2020). A spatial-temporal study for the
> spread of dengue depending on climate factors in Pakistan (2006-2017).
> *BMC Public Health*, 20(1), 995. DOI: 10.1186/s12889-020-08846-8

## Alignment

SDG 3 (Good Health and Well-being) · SDG 13 (Climate Action) · One Health framework

## Licence

MIT. See [LICENSE](LICENSE).

---

Developed by **Uneeza Saeed**, Founder, StratoSal AI.
