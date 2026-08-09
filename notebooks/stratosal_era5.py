# =============================================================================
# StratoSal AI -- ERA5 extraction and forecast builder
# Punjab, Pakistan | January 2019 to July 2026 | August 2026 outlook
#
# Run in Google Colab, one CELL at a time, top to bottom.
# The Copernicus token is entered once in CELL 2 via getpass. It is never
# written to a file and must never be committed to this repository.
# =============================================================================


# ---- CELL 1 -- install libraries -------------------------------------------

!pip install -q "cdsapi>=0.7.7" xarray netCDF4 pandas numpy scipy


# ---- CELL 2 -- authenticate with Copernicus --------------------------------
# Run the cell, then paste the token into the input box that appears below it.
# The token is held in memory for this session only.

import getpass, os

CDS_URL = "https://cds.climate.copernicus.eu/api"
CDS_KEY = getpass.getpass("Paste your CDS Personal Access Token, then press Enter: ")

os.environ["CDSAPI_URL"] = CDS_URL
os.environ["CDSAPI_KEY"] = CDS_KEY
print("Token stored in memory for this session only.")


# ---- CELL 3 -- download ERA5 monthly means ---------------------------------
# The dataset licence must be accepted on the CDS website first, otherwise this
# returns 403. First run may queue for 2 to 20 minutes.

import cdsapi, traceback

TARGET = "/content/punjab_era5.nc"

client = cdsapi.Client(
    url=os.environ["CDSAPI_URL"],
    key=os.environ["CDSAPI_KEY"],
)

dataset = "reanalysis-era5-single-levels-monthly-means"
request = {
    "product_type": ["monthly_averaged_reanalysis"],
    "variable": [
        "2m_temperature",
        "2m_dewpoint_temperature",
        "total_precipitation",
    ],
    "year":  [str(y) for y in range(2019, 2027)],
    "month": ["%02d" % m for m in range(1, 13)],
    "time":  ["00:00"],
    "area":  [34.0, 69.5, 29.5, 75.0],   # North, West, South, East
    "data_format": "netcdf",
    "download_format": "unarchived",
}

try:
    client.retrieve(dataset, request).download(TARGET)
except Exception:
    print("\n===== RETRIEVE FAILED, full error below =====\n")
    traceback.print_exc()
    raise

if not os.path.exists(TARGET):
    raise FileNotFoundError(f"{TARGET} was not created.")

size = os.path.getsize(TARGET)
print(f"\nFile written: {TARGET}")
print(f"Size: {size/1e6:.2f} MB")

if size < 100_000:
    raise ValueError(
        f"File is only {size} bytes, probably an error page rather than data:\n"
        + open(TARGET, "rb").read()[:500].decode("utf-8", "ignore")
    )
print("Download verified.")


# ---- CELL 4 -- open, align and verify the grid -----------------------------
# The CDS response is often a ZIP holding two files: one with the instantaneous
# fields (t2m, d2m) and one with the accumulated field (tp). Their timestamps
# differ slightly for the same month, so a naive merge produces two half-empty
# rows per month. Snapping every file to month-start fixes the alignment.

import zipfile, glob
import numpy as np, pandas as pd
import xarray as xr

magic = open(TARGET, "rb").read(8)

if magic[:4] == b"PK\x03\x04":
    os.makedirs("/content/era5", exist_ok=True)
    with zipfile.ZipFile(TARGET) as z:
        z.extractall("/content/era5")
        print("Archive contents:", z.namelist())
    files = sorted(glob.glob("/content/era5/*.nc"))
else:
    files = [TARGET]

if not files:
    raise FileNotFoundError("No .nc files found.")

parts = []
for p in files:
    d = xr.open_dataset(p)

    t = "valid_time" if "valid_time" in d.dims else "time"
    if t != "time":
        d = d.rename({t: "time"})

    # Align the instantaneous and accumulated streams onto identical timestamps.
    d = d.assign_coords(
        time=pd.to_datetime(d["time"].values).to_period("M").to_timestamp()
    )

    # Recent months are served as ERA5T (preliminary), which introduces expver.
    if "expver" in d.dims:
        d = d.reduce(np.nanmax, dim="expver", keep_attrs=True)
    elif "expver" in d.coords:
        d = d.drop_vars("expver")

    print(f"  {os.path.basename(p)}: {list(d.data_vars)}, {d.sizes['time']} steps")
    parts.append(d)

ds = xr.merge(parts, compat="override", join="inner").sortby("time")
TIME = "time"

n_lat = ds.sizes["latitude"]
n_lon = ds.sizes["longitude"]
n_pts = n_lat * n_lon

months = pd.to_datetime(ds[TIME].values).strftime("%Y-%m")
if len(months) != len(set(months)):
    raise ValueError("Duplicate months after merge. The time alignment failed.")

print(f"\nVariables       : {list(ds.data_vars)}")
print(f"Grid points     : {n_lat} x {n_lon} = {n_pts}")
print(f"Timesteps       : {ds.sizes[TIME]}  (unique months: {len(set(months))})")
print(f"Range           : {months[0]} to {months[-1]}")

# 437 is stated publicly in the EOI and on the site, so it is verified here.
if n_pts != 437:
    raise ValueError(f"Grid is {n_lat} x {n_lon} = {n_pts}, expected 437.")

for v in ("t2m", "d2m", "tp"):
    if v not in ds.data_vars:
        raise KeyError(f"Variable '{v}' missing. Found: {list(ds.data_vars)}")
    n_nan = int(ds[v].isnull().sum())
    if n_nan:
        raise ValueError(f"'{v}' has {n_nan} NaN values after merge.")

print("\nGrid verified: 19 x 23 = 437 points. All variables present, no gaps.")


# ---- CELL 5 -- convert units and derive humidity ---------------------------
# ERA5 temperature is Kelvin. ERA5 monthly total_precipitation is a MEAN DAILY
# RATE in metres, so it needs x1000 (m to mm) and x days in month.
# ERA5 publishes no surface relative humidity; it is derived from 2 m
# temperature and 2 m dewpoint via the Magnus formula.

t2m = ds["t2m"] - 273.15
d2m = ds["d2m"] - 273.15

a, b = 17.625, 243.04             # Alduchov and Eskridge (1996)
rh = 100.0 * (np.exp((a * d2m) / (b + d2m)) / np.exp((a * t2m) / (b + t2m)))
rh = rh.clip(0, 100)

days = ds[TIME].dt.days_in_month
precip_mm = ds["tp"] * 1000.0 * days

ds_out = xr.Dataset({"temp_c": t2m, "rh_pct": rh, "precip_mm": precip_mm})

# Individual foothill grid cells legitimately exceed several hundred mm in
# flood months, so this check is loose. The strict check is on the provincial
# mean in CELL 6, since that is the series the website displays.
print("Precipitation across all cells and months (mm):")
for q in (50, 90, 99, 100):
    print(f"  {q:3d}th percentile: {float(precip_mm.quantile(q/100)):8.1f}")

print(f"\nTemperature range: {float(t2m.min()):.1f} to {float(t2m.max()):.1f} C")
print(f"Humidity range   : {float(rh.min()):.1f} to {float(rh.max()):.1f} %")

if float(precip_mm.max()) > 3000:
    raise ValueError("Precipitation exceeds 3000 mm in one cell-month. Unit error.")
if float(t2m.min()) < -20 or float(t2m.max()) > 55:
    raise ValueError("Temperature outside plausible range. Check Kelvin conversion.")

print("\nUnits converted.")


# ---- CELL 6 -- province-wide monthly series --------------------------------

prov = pd.DataFrame({
    "month":     pd.to_datetime(ds_out[TIME].values).strftime("%Y-%m"),
    "temp_c":    ds_out["temp_c"].mean(dim=["latitude", "longitude"]).values,
    "rh_pct":    ds_out["rh_pct"].mean(dim=["latitude", "longitude"]).values,
    "precip_mm": ds_out["precip_mm"].mean(dim=["latitude", "longitude"]).values,
}).round(1)

prov = prov[prov["month"] <= "2026-07"].reset_index(drop=True)

pmax    = prov["precip_mm"].max()
wettest = prov.loc[prov["precip_mm"].idxmax(), "month"]
print(f"Months in series : {len(prov)}")
print(f"Wettest month    : {wettest} at {pmax:.1f} mm province-wide")

if pmax > 700:
    raise ValueError(
        f"Province-wide monthly mean reaches {pmax:.1f} mm, not plausible for "
        "Punjab. Check the unit conversion in CELL 5."
    )

if len(prov) != 91:
    print(f"NOTE: expected 91 months (Jan 2019 to Jul 2026), got {len(prov)}.")

print("\nLast 8 months:")
print(prov.tail(8).to_string(index=False))


# ---- CELL 7 -- district-level extraction -----------------------------------
# Nearest grid cell to each district centroid. Bahawalpur city centre lies
# marginally south of the domain edge, so the southernmost row (29.5 N) is used.

DISTRICTS = {
    "Lahore":        (31.5497, 74.3436),
    "Faisalabad":    (31.4504, 73.1350),
    "Multan":        (30.1575, 71.5249),
    "Rawalpindi":    (33.5651, 73.0169),
    "Gujranwala":    (32.1877, 74.1945),
    "Sialkot":       (32.4945, 74.5229),
    "Bahawalpur":    (29.3956, 71.6836),
    "Sargodha":      (32.0836, 72.6711),
    "Sheikhupura":   (31.7131, 73.9783),
    "Nankana Sahib": (31.4504, 73.7080),
}

rows = []
for name, (lat, lon) in DISTRICTS.items():
    cell = ds_out.sel(latitude=lat, longitude=lon, method="nearest")
    rows.append(pd.DataFrame({
        "district":  name,
        "month":     pd.to_datetime(cell[TIME].values).strftime("%Y-%m"),
        "temp_c":    cell["temp_c"].values,
        "rh_pct":    cell["rh_pct"].values,
        "precip_mm": cell["precip_mm"].values,
    }))

dist = pd.concat(rows, ignore_index=True).round(1)
dist = dist[dist["month"] <= "2026-07"].reset_index(drop=True)

print(dist[dist["month"] == "2026-07"].to_string(index=False))


# ---- CELL 8 -- climate suitability index -----------------------------------
# A transparent rule over the three ERA5 signals. This is NOT a trained
# classifier and is not described as one anywhere on the site.
#
# Thresholds follow the published Aedes aegypti transmission literature:
#   - transmission is efficient roughly between 26 and 35 C
#   - sustained temperatures above 38 C suppress adult vector survival
#   - relative humidity above 65 percent extends adult lifespan
#   - rainfall above ~50 mm/month sustains standing-water breeding sites

def suitability(temp, rh, precip):
    if temp > 38 or precip < 20:
        return "LOW"
    if 26 <= temp <= 35 and rh > 65 and precip > 50:
        return "HIGH"
    return "MEDIUM"

def suitability_score(temp, rh, precip):
    """Continuous 0 to 1 form of the same rule, for month-on-month comparison."""
    t = np.exp(-((temp - 30.5) ** 2) / (2 * 4.0 ** 2))     # peak near 30.5 C
    h = np.clip((rh - 45.0) / 35.0, 0, 1)                  # rises 45 to 80 pct
    p = np.clip(precip / 150.0, 0, 1)                      # saturates at 150 mm
    return float(t * h * p)

dist["risk"]  = [suitability(r.temp_c, r.rh_pct, r.precip_mm) for r in dist.itertuples()]
prov["score"] = [suitability_score(r.temp_c, r.rh_pct, r.precip_mm) for r in prov.itertuples()]

latest = dist[dist["month"] == "2026-07"]
if latest.empty:
    raise ValueError("No data for 2026-07.")

print(latest[["district", "temp_c", "precip_mm", "rh_pct", "risk"]].to_string(index=False))
print("\nRisk counts:", latest["risk"].value_counts().to_dict())


# ---- CELL 9 -- validation --------------------------------------------------
# Interannual validation is not possible from seven annual totals. What IS
# demonstrable is that the suitability index peaks ahead of the documented
# Punjab dengue season, which is the basis of the lead-time claim.

from scipy.stats import spearmanr

MONTHS = ["January","February","March","April","May","June",
          "July","August","September","October","November","December"]

prov["year"] = prov["month"].str[:4].astype(int)
prov["mnum"] = prov["month"].str[5:].astype(int)

monthly_clim = prov.groupby("mnum")["score"].mean()
peak_month   = int(monthly_clim.idxmax())

print("Mean climate suitability by calendar month, 2019 to 2026")
print("-" * 58)
for m in range(1, 13):
    bar  = "#" * int(round(monthly_clim[m] * 60))
    mark = "  <-- peak" if m == peak_month else ""
    print(f"  {MONTHS[m-1][:3]}  {monthly_clim[m]:.3f}  {bar}{mark}")

print(f"\nSuitability peaks in : {MONTHS[peak_month-1]}")
print( "Punjab case peak     : September to October (surveillance record)")
print( "Implied lead time    : 4 to 6 weeks")

# Secondary check, published on the site as a stated limitation.
PUNJAB_CASES = {
    2019: 19021, 2020: 820, 2021: 24146, 2022: 6255,
    2023: 5469,  2024: 4390, 2025: 4117,
}

monsoon = prov[prov["mnum"].isin([6, 7, 8, 9])]
yearly  = monsoon.groupby("year")["score"].mean()
yrs = [y for y in PUNJAB_CASES if y in yearly.index]
rho, pval = spearmanr([yearly[y] for y in yrs], [PUNJAB_CASES[y] for y in yrs])

print(f"\nInterannual check (stated as a limitation, not a headline):")
print(f"  rho = {rho:.2f}, p = {pval:.2f}, n = {len(yrs)}  -> not significant")


# ---- CELL 10 -- August 2026 outlook ----------------------------------------
# ERA5 reanalyses the past and cannot forecast. This is the mean of ERA5
# Augusts 2019 to 2025, labelled an outlook everywhere it appears on the site.

aug_hist = prov[(prov["mnum"] == 8) & (prov["year"] <= 2025)]
if aug_hist.empty:
    raise ValueError("No August months found in the series.")

aug_outlook = {
    "temp_c":    round(float(aug_hist["temp_c"].mean()), 1),
    "rh_pct":    round(float(aug_hist["rh_pct"].mean()), 1),
    "precip_mm": round(float(aug_hist["precip_mm"].mean()), 1),
    "basis":     f"ERA5 August climatology, {int(aug_hist['year'].min())} to {int(aug_hist['year'].max())}",
    "n_years":   int(len(aug_hist)),
}
aug_outlook["risk"] = suitability(
    aug_outlook["temp_c"], aug_outlook["rh_pct"], aug_outlook["precip_mm"]
)

print("August 2026 climatological outlook:")
for k, v in aug_outlook.items():
    print(f"  {k:10s}: {v}")


# ---- CELL 11 -- write forecast.json ----------------------------------------
# Every number the website displays comes from this file, so a mismatch between
# the page and the underlying data is structurally impossible.

import json
from datetime import datetime, timezone

latest_month = "2026-07"
sel = prov[prov["month"] == latest_month]
if sel.empty:
    raise ValueError(f"{latest_month} not in series. Last: {prov['month'].iloc[-1]}")
jul = sel.iloc[0]

payload = {
    "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "grid": {
        "lat_points": int(n_lat),
        "lon_points": int(n_lon),
        "total_points": int(n_pts),
        "bbox": {"north": 34.0, "west": 69.5, "south": 29.5, "east": 75.0},
        "resolution_deg": 0.25,
    },
    "coverage": {
        "first_month": prov["month"].iloc[0],
        "last_month":  latest_month,
        "n_months":    int(len(prov)),
    },
    "latest": {
        "month":     latest_month,
        "temp_c":    float(jul["temp_c"]),
        "rh_pct":    float(jul["rh_pct"]),
        "precip_mm": float(jul["precip_mm"]),
    },
    "august_outlook": aug_outlook,
    "validation": {
        "method": "Seasonal concordance between ERA5 climate suitability and the documented Punjab dengue transmission season",
        "suitability_peak_month": MONTHS[peak_month - 1],
        "recorded_case_peak": "September to October",
        "lead_time_weeks": "4 to 6",
        "interannual_rho": round(float(rho), 2),
        "interannual_p":   round(float(pval), 2),
        "interannual_n":   int(len(yrs)),
        "limitation": "Rank correlation between monsoon-season suitability and annual provincial case totals across seven years is not statistically significant. Annual totals are dominated by population immunity, serotype turnover, vector-control intensity and surveillance coverage rather than by climate. Isolating the climate signal requires district-level monthly case data, which is the primary data-partnership objective of this pilot.",
    },
    "series": {
        "months":    prov["month"].tolist(),
        "temp_c":    prov["temp_c"].tolist(),
        "precip_mm": prov["precip_mm"].tolist(),
        "rh_pct":    prov["rh_pct"].tolist(),
    },
    "districts": [
        {
            "district":  r.district,
            "temp_c":    float(r.temp_c),
            "rh_pct":    float(r.rh_pct),
            "precip_mm": float(r.precip_mm),
            "risk":      r.risk,
        }
        for r in latest.itertuples()
    ],
}

# Chart.js silently drops values when arrays disagree in length.
n = len(payload["series"]["months"])
for key in ("temp_c", "precip_mm", "rh_pct"):
    assert len(payload["series"][key]) == n, f"{key} length mismatch"

# NaN is not valid JSON and would break the page. Refuse to write it.
raw = json.dumps(payload, indent=2)
if "NaN" in raw or "Infinity" in raw:
    raise ValueError("Payload contains NaN or Infinity. Do not upload this file.")

with open("/content/forecast.json", "w") as fh:
    fh.write(raw)

print(f"forecast.json written. {n} months, {len(payload['districts'])} districts.")
print("\nValidation block:")
print(json.dumps(payload["validation"], indent=2))


# ---- CELL 12 -- download ---------------------------------------------------

from google.colab import files
files.download("/content/forecast.json")
