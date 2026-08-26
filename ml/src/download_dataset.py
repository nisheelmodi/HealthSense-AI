"""
HealthSense AI — Dataset Download Script
=========================================
Run this script ONCE to download the Heart Disease Health Indicators dataset
from a public GitHub mirror into the correct project directory.

Usage:
    python ml/src/download_dataset.py

Requirements:
    pip install requests
    (or: pip install -r ml/requirements.txt  — pandas already installs requests indirectly)
"""

import os
import sys
import pathlib

# ---------------------------------------------------------------------------
# Target path
# ---------------------------------------------------------------------------
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent   # ml/src/
ML_DIR = SCRIPT_DIR.parent                              # ml/
DEST_DIR  = ML_DIR / "data" / "raw"
DEST_FILE = DEST_DIR / "heart_disease_health_indicators_BRFSS2015.csv"

# Multiple mirror URLs — try them in order
DATASET_URLS = [
    # Primary: GitHub mirror (CC0 public domain)
    "https://raw.githubusercontent.com/doguilmak/Heart-Diseaseor-Attack-Classification/main/heart_disease_health_indicators_BRFSS2015.csv",
    # Fallback: another common mirror
    "https://raw.githubusercontent.com/dsrscientist/dataset1/master/heart_disease_health_indicators_BRFSS2015.csv",
]


def download(url: str, dest: pathlib.Path) -> bool:
    """Download file from url to dest. Returns True on success."""
    try:
        import urllib.request
        import urllib.error

        print(f"Attempting download from:\n  {url}")
        dest.parent.mkdir(parents=True, exist_ok=True)

        with urllib.request.urlopen(url, timeout=60) as response:
            total = int(response.headers.get("Content-Length", 0))
            downloaded = 0
            chunk_size = 1024 * 64  # 64 KB chunks

            with open(dest, "wb") as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total > 0:
                        pct = downloaded / total * 100
                        print(f"  Progress: {downloaded:,} / {total:,} bytes ({pct:.1f}%)", end="\r")

        print(f"\n✅ Download complete: {dest}")
        return True

    except Exception as e:
        print(f"\n  ❌ Failed: {e}")
        return False


def verify(dest: pathlib.Path) -> None:
    """Quick sanity-check on the downloaded CSV."""
    try:
        import csv
        with open(dest, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            row_count = sum(1 for _ in reader)

        print(f"\n📊 Verification:")
        print(f"  Columns : {len(header)}")
        print(f"  Header  : {', '.join(header[:5])} ...")
        print(f"  Rows    : {row_count:,}")

        expected_cols = {"HeartDiseaseorAttack", "BMI", "Smoker", "PhysActivity", "Age", "Sex"}
        missing = expected_cols - set(header)
        if missing:
            print(f"  ⚠️  Expected columns missing: {missing}")
        else:
            print("  ✅ All expected columns present.")

    except Exception as e:
        print(f"  ❌ Verification failed: {e}")


if __name__ == "__main__":
    if DEST_FILE.exists():
        size_kb = DEST_FILE.stat().st_size / 1024
        print(f"✅ Dataset already exists: {DEST_FILE}  ({size_kb:.1f} KB)")
        print("   Delete the file and re-run this script to re-download.")
        verify(DEST_FILE)
        sys.exit(0)

    print("=" * 60)
    print("HealthSense AI — Dataset Downloader")
    print("=" * 60)
    print(f"Destination: {DEST_FILE}\n")

    success = False
    for url in DATASET_URLS:
        success = download(url, DEST_FILE)
        if success:
            break

    if not success:
        print("\n❌ All download attempts failed.")
        print("\nManual download instructions:")
        print("  1. Visit: https://www.kaggle.com/datasets/alexteboul/heart-disease-health-indicators-dataset")
        print("  2. Download: heart_disease_health_indicators_BRFSS2015.csv")
        print(f"  3. Save to: {DEST_FILE}")
        sys.exit(1)

    verify(DEST_FILE)
    print("\n🚀 Ready! Run the inspection script:")
    print("   python ml/src/inspect_dataset.py")
