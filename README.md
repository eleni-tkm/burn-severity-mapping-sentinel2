![Python Version](https://img.shields.io/badge/python-3.13-blue)\
_See how to add badges: https://shields.io/badges_

#  Burned Area and Burn Severity Mapping with Sentinel-2 Level-2A (RBR)

## 📌 Overview

This repository contains three Python scripts that implement a **burned area mapping workflow** using **Sentinel-2 Level-2A (L2A) optical satellite imagery**. 
The final objective is the calculation of the **Relativized Burn Ratio (RBR)** to detect and map burned areas and burn severity following wildfire events.

The workflow follows standard practices in Earth Observation (EO) and remote sensing of wildfires, using surface reflectance data and well-established spectral indices.

---

## 🛰️ Sentinel-2 Level-2A Products

Sentinel-2 is part of the **Copernicus Programme** of the European Space Agency (ESA). The satellites carry the **MultiSpectral Instrument (MSI)**, which measures reflected solar radiation in 13 spectral bands (visible, near-infrared, and shortwave infrared).

### Level-2A (L2A):

- Provides **Bottom-Of-Atmosphere (BOA) surface reflectance**
- Atmospheric effects are corrected using the **Sen2Cor processor**
- Includes a **Scene Classification Layer (SCL)** for cloud, shadow, snow, and water masking
- Suitable for spectral index computation without additional atmospheric correction

📘 https://sentiwiki.copernicus.eu/web/s2-products

---

## 🌞 Surface Reflectance

**Surface reflectance** is the fraction of incoming solar radiation reflected by the Earth’s surface in a given spectral band.

- Unitless physical quantity
- Typically ranges between **0 and 1**
- Burned areas are characterized by **decreased NIR reflectance** and **increased SWIR reflectance**

---

## 📁 Repository Structure

| Script | Description |
|------|------------|
| `01_preprocess_sentinel2.py` | Band extraction, resampling, reflectance scaling |
| `02_compute_nbr.py` | Spectral index computation (NBR) with cloud & water masking |
| `03_compute_dnbr_rbr.py` | dNBR and RBR computation |

---

## 🛠️ Part A — Preprocessing

The preprocessing step prepares Sentinel-2 L2A data for spectral analysis by:

- Extracting required spectral bands
- Resampling all inputs to a common 10 m grid
- Converting digital numbers to **physical surface reflectance** (reflectance = digital_number / 10000)
- Preserving categorical classification layers

## 🛠️ Part B — NBR with cloud & water masking

- NBR = (NIR - SWIR) / (NIR + SWIR)
- Sentinel-2:
  - NIR → Band 8
  - SWIR → Band 12
- Healthy vegetation → high NBR / Burned areas → low or negative NBR
- **NDWI > 0 → water or very moist surfaces**

### Masking Strategy  

Pixels are excluded from analysis if classified as:
- Clouds
- Cloud shadows
- Snow / ice
- Water (via SCL and NDWI)

This ensures indices are computed only on valid land surface pixels.

📘 https://custom-scripts.sentinel-hub.com/custom-scripts/sentinel-2/scene-classification/

## 🛠️ Part C — Burn Metrics

### Differenced Normalized Burn Ratio (dNBR)
dNBR highlights fire-induced spectral change between pre- and post-fire images.

### Relativized Burn Ratio (RBR)
RBR normalizes burn severity by pre-fire vegetation conditions, improving comparability across areas with different biomass levels.

📘 [Parks et al. (2014)](https://www.mdpi.com/2072-4292/6/3/1827)

## Burn Severity Thresholds (RBR)
Burn severity thresholds are ecosystem-dependent and primarily intended as indicative values.
For applications requiring high thematic accuracy, thresholds should be calibrated using field-based severity metrics (e.g. Composite Burn Index) or validated regional studies.

## Typical RBR values
| RBR value | Interpretation |
|----------|---------------|
| `< 0.1` | Unburned / unchanged |
| `0.1 – 0.27` | Low severity |
| `0.27 – 0.44` | Moderate-low severity |
| `0.44 – 0.66` | Moderate-high severity |
| `> 0.66` | High severity |

_Thresholds may require **local calibration** using field data (e.g. CBI) or region-specific studies._
