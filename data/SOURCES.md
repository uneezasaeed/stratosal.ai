# Data Sources

StratoSal AI · Punjab, Pakistan · compiled 9 August 2026

Every figure displayed on the StratoSal AI prototype traces to a source listed
below. No value on the site is entered by hand: the site reads `data/dengue.json`
and `data/forecast.json`, and those files are written by the extraction notebook
and by this source register.

---

## Climate data

**ERA5 reanalysis**, produced by the European Centre for Medium-Range Weather
Forecasts (ECMWF) and distributed through the Copernicus Climate Change Service
(C3S) Climate Data Store.

- Dataset: `reanalysis-era5-single-levels-monthly-means`
- Product type: `monthly_averaged_reanalysis`
- Variables: `2m_temperature`, `2m_dewpoint_temperature`, `total_precipitation`
- Spatial domain: 29.5°N to 34.0°N, 69.5°E to 75.0°E
- Resolution: 0.25° × 0.25°, giving 19 latitude × 23 longitude = **437 grid points**
- Temporal coverage: January 2019 to July 2026
- Access: https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels-monthly-means

Citation:
> Hersbach, H. et al. (2023). *ERA5 monthly averaged data on single levels from
> 1940 to present.* Copernicus Climate Change Service (C3S) Climate Data Store
> (CDS). DOI: 10.24381/cds.f17050d7

Relative humidity is not published as an ERA5 surface field. It is derived here
from 2 m temperature and 2 m dewpoint temperature using the Magnus formula with
the coefficients of Alduchov and Eskridge (1996), a = 17.625, b = 243.04.

> Alduchov, O.A. and Eskridge, R.E. (1996). Improved Magnus form approximation of
> saturation vapor pressure. *Journal of Applied Meteorology*, 35(4), 601-609.

---

## Dengue surveillance data

### S1 — Punjab 2019
Punjab provincial health authorities, reported November 2019. Provincial total
19,021 cases; Lahore 14,145 cases (76 percent of the provincial total).
Corroborated by the WHO Disease Outbreak News entry for Pakistan, which records
47,120 confirmed cases and 75 deaths nationally between 8 July and 12 November 2019.

- https://www.who.int/emergencies/disease-outbreak-news/item/dengue-fever-pakistan

### S2 — Punjab 2020
More than 820 reported dengue cases in Punjab in the first half of 2020, of which
687 occurred in Lahore.

> COVID-19 and alarming dengue co-epidemics in the dilapidated healthcare system in
> Pakistan: Where to focus! *Journal of Infection*, 2021.
> https://www.journalofinfection.com/article/S0163-4453(21)00638-1/fulltext

### S3 — Punjab 2021
As of 25 November 2021, Punjab reported 24,146 cases and 127 deaths, being 49.4
percent of national cases and 69.4 percent of national deaths, case fatality
ratio 0.5 percent.

- WHO Eastern Mediterranean Regional Office / WHO Disease Outbreak News:
  https://www.who.int/emergencies/disease-outbreak-news/item/dengue-fever-pakistan
- IFRC DREF Operation MDRPK022, Pakistan Dengue Response:
  https://reliefweb.int/report/pakistan/pakistan-dengue-response-operation-update-report-n-1-dref-operation-n-mdrpk022

### S4 — Punjab 2022
6,255 cases as of 22 September 2022, being 29 percent of the national total at
the same reporting date.

- National Institute of Health Islamabad, Integrated Disease Surveillance and
  Response weekly bulletins:
  https://phb.nih.org.pk/integratedisease-surveillance-and-response

### S5 — Punjab 2023
5,469 confirmed cases across Punjab's 36 districts. District breakdown: Lahore
2,130; Rawalpindi 1,561; Multan 620; Gujranwala 268; Faisalabad 245.

> Battle against the dengue epidemic: Pakistan's ongoing struggle.
> *IJS Global Health*, 2024.
> https://journals.lww.com/ijsgh/fulltext/2024/03010/battle_against_the_dengue_epidemic__pakistan_s.42.aspx

### S6 — Punjab 2024
4,390 cases and 8 deaths as of early November 2024.

- National Institute of Health Islamabad, Integrated Disease Surveillance and
  Response weekly bulletins:
  https://phb.nih.org.pk/integratedisease-surveillance-and-response

### S7 — Punjab 2025
4,117 cases as of 19 November 2025; Lahore 708. Surge attributed to prolonged
monsoon rainfall and flooding.

- https://english.news.cn/asiapacific/20251119/dd00b8d5421d4ef4919f409b0ffbe26b/c.html
- https://www.nation.com.pk/19-Nov-2025/dengue-cases-surge-punjab-sindh
- https://tribune.com.pk/story/2582327/flood-aftermath-fuels-dengue-surge-across-punjab

### S8 — Punjab 2026, season in progress
Transmission season active during the 2026 monsoon. 67 cases detected province-wide
in a single day, 61 patients admitted across Punjab hospitals, 36 of them in Lahore.

- https://english.nepalnews.com/s/health/pakistan-67-dengue-cases-detected-across-punjab-in-one-day/
- National Institute of Health Islamabad, weekly bulletins, 2026 weeks 1 to 29:
  https://phb.nih.org.pk/integratedisease-surveillance-and-response

### S9 — National context series
Pakistan national annual dengue totals as reported by the National Institute of
Health, Islamabad: 2019 · 24,547 · 2020 · 3,442 · 2021 · 48,906 · 2022 · 25,932
(to 27 September) · 2023 · 21,016 · 2024 · 24,182 · 2025 · 33,394.

- https://phb.nih.org.pk/integratedisease-surveillance-and-response

---

## Provincial surveillance authority

The Dengue Expert Advisory Group (DEAG), Government of Punjab, is the provincial
clinical and surveillance authority for dengue, established in 2011 and convening
through 2026. https://deag.punjab.gov.pk/

Punjab Provincial Disaster Management Authority epidemics register:
https://pdma.punjab.gov.pk/epidemics

---

## Literature foundation for the climate-disease method

> Shabbir, W., Pilz, J. and Naeem, A. (2020). A spatial-temporal study for the
> spread of dengue depending on climate factors in Pakistan (2006-2017).
> *BMC Public Health*, 20(1), 995. DOI: 10.1186/s12889-020-08846-8

> Incidence of Dengue Fever in Pakistan. *PLOS ONE*, 2026.
> DOI: 10.1371/journal.pone.0352938
> Note: this study applies a Seasonal Mann-Kendall test and reports statistically
> significant monthly trends in Sindh and Khyber Pakhtunkhwa, but no significant
> monthly trend in Punjab over its study period. StratoSal AI forecasts outbreak
> risk from concurrent climate state rather than from a secular time trend, so a
> null trend result is not in conflict with the approach.
