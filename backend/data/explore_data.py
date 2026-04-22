# backend/data/explore_data.py

import pandas as pd
import numpy as np

# Load dataset
df = pd.read_csv("crop_data.csv")

print("=" * 50)
print("DATASET SHAPE")
print("=" * 50)
print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")

print("\n" + "=" * 50)
print("FIRST 5 ROWS")
print("=" * 50)
print(df.head())

print("\n" + "=" * 50)
print("COLUMN DATA TYPES")
print("=" * 50)
print(df.dtypes)

print("\n" + "=" * 50)
print("MISSING VALUES")
print("=" * 50)
print(df.isnull().sum())

print("\n" + "=" * 50)
print("BASIC STATISTICS")
print("=" * 50)
print(df.describe())

print("\n" + "=" * 50)
print("CROP DISTRIBUTION (label counts)")
print("=" * 50)
print(df['label'].value_counts())

print("\n" + "=" * 50)
print("FEATURE RANGES PER CROP (sample: rice)")
print("=" * 50)
print(df[df['label'] == 'rice'].describe())