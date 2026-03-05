# Soil AD Pipeline

A production-ready pipeline for estimating Available Water (AD)
and soil productive potential based on soil type and granulometric composition.

---

## 🚀 Project Overview

This pipeline:

- Integrates Brazilian soil profile data (BDSolos)
- Calculates Available Water (AD) using pedotransfer equations
- Classifies soil into AD1–AD6 classes
- Estimates productive potential
- Accepts GeoJSON field boundaries as input

---

## 🏗 Architecture

Input:
- Field boundary (GeoJSON)
- Soil type
- Sand, silt, clay percentages

Processing:
- Pedotransfer calculation
- AD classification
- Productive potential estimation

Output:
- JSON response ready for dashboard/API consumption

---

## 📂 Project Structure

See `/src` for modular domain-based architecture:

- `data/` → Data ingestion and processing
- `soil/` → Domain logic (AD calculation and classification)
- `geo/` → Spatial operations
- `service/` → Orchestration layer

---

## 🔧 Installation

```bash
pip install -r requirements.txt
