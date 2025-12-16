# uav-traffic-occlusion-simulator
Interactive UAV–traffic occlusion simulation for road inspection
# UAV Traffic Occlusion Simulation for Road Inspection

This repository provides the Python simulation code used in the paper:

**Traffic-Aware UAV Speed Optimization and Occlusion-Resilient Image Stitching
for Road Infrastructure Inspection under Dynamic Traffic Conditions**
(submitted to Transportation Research Part C)

## Overview
The script implements an interactive simulation to illustrate:
- UAV scanning along a roadway
- Dynamic traffic flow with vehicle-induced occlusion
- Visibility completeness of road segments under different UAV speeds and traffic densities

The simulator visually demonstrates how multi-frame observation compensates for
transient occlusion in traffic-active environments.

## Requirements
- Python >= 3.8
- numpy
- matplotlib

Install dependencies:
```bash
pip install -r requirements.txt
