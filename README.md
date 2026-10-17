# Composite Liveability Index for Dublin Small Areas (Python)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![GeoPandas](https://img.shields.io/badge/GeoPandas-vector%20analysis-green.svg)](https://geopandas.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview
A Python version of my ArcGIS Pro workflow that scores Dublin's CSO Small Areas on liveability using OpenStreetMap data. Four indicators are combined into one index:
- healthcare within 500 m (hospital, doctors, pharmacy)
- public transport within 400 m (bus, tram, rail)
- green space ratio
- active travel path density (cycleways, footways, paths)

The repository has two parts:
- **`liveability_demo.py`** runs on synthetic data and needs no downloads. It illustrates the index method only.
- **`dublin_liveability_analysis.py`** is the full GeoPandas workflow for the real data (see `DATA.md`). Raw data is not included, and no real-data results are published here.

## Method
1. Flag Small Areas within a buffer of healthcare and transport points (merged buffers, binary 0/1).
2. Calculate green space ratio and active travel density (km per km²) per Small Area.
3. Normalise: continuous indicators divided by their maximum, binary indicators kept as 0/1.
4. Composite Liveability Index = mean of the four scores.
5. Classify into five classes (Very Low to Very High) using Natural Breaks (Jenks).
6. Optional planning queries: Small Areas with no healthcare and no transport access, and Small Areas with under 5% green space and over 40% building coverage.

## Repository structure
```
liveability_demo.py                # synthetic-data demo
dublin_liveability_analysis.py     # real-data workflow
DATA.md                            # data sources
requirements.txt
LICENSE
```

## Run
```
pip install -r requirements.txt
python liveability_demo.py
```

## Limitations
- Equal weights and only four indicators.
- Buffers use straight-line distance, not walking routes.
- Small Areas vary greatly in size, so large suburban or rural areas can score low.
- OpenStreetMap completeness varies between layers.

## Author
Aung Kaung Myat, MSc GIS & Remote Sensing, University College Dublin.
