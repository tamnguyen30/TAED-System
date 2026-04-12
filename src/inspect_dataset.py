#!/usr/bin/env python3
"""Simple utility for inspecting the combined phishing dataset.

Run this after you have created `data/unified_phishing_dataset.csv` (or the
balanced version) to verify that the cleaning pipeline produced sensible
emails.  It prints basic statistics, length distributions, and a few random
examples from each label so you can eyeball whether headers/metadata remain.
"""

import pandas as pd
import numpy as np
import os
import textwrap

DATA_FILE = 'data/unified_phishing_dataset.csv'

if not os.path.exists(DATA_FILE):
    print(f"ERROR: {DATA_FILE} not found. Run process_data.py first.")
    exit(1)

print(f"Loading dataset from {DATA_FILE}...\n")
df = pd.read_csv(DATA_FILE)

print("--- Overall dataset ---")
print(f"total rows: {len(df)}")
print(df['label'].value_counts().to_string())

# length stats
lengths = df['text'].astype(str).str.len()
print("\n--- Length statistics (characters) ---")
print(f"min: {lengths.min()}, max: {lengths.max()}, mean: {lengths.mean():.1f}")
print(lengths.quantile([0.25, 0.5, 0.75, 0.9]).to_string())

# look for weird header artifacts
patterns = ['Subject:', 'From:', 'To:', 'Cc:', 'Date:']
print("\nRows containing header-like tokens (first 5 shown):")
mask = df['text'].astype(str).str.contains('|'.join(patterns), case=False, na=False)
print(df[mask].head(5).to_string(index=False))

# show sample texts per class
for lbl in sorted(df['label'].unique()):
    print(f"\n--- random examples for label={lbl} ---")
    samples = df[df['label'] == lbl]['text'].dropna().sample(3, random_state=42)
    for i, txt in enumerate(samples, 1):
        print(f"\n[{lbl} sample {i}]\n" + textwrap.fill(txt, width=80)[:1000])

print("\nInspection complete. Use this output to decide if further cleaning is required.")
