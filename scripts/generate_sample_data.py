"""Generate deterministic fake freight data for the portfolio demo.

The generated CSVs mimic the original Oracle tables without exposing real
customer names, addresses, or shipment volumes.
"""

from __future__ import annotations

import csv
import random
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
COORD_PATH = ROOT / "시군구(중심좌표).xlsx"
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
SEED = 20260512


@dataclass(frozen=True)
class Customer:
    cu_id: str
    cu_nm: str
    cu_add: str
    sig_cd: str
    sig_kor_nm: str
    lat_no: float
    lon_no: float
    industry: str
    region_group: str
    size_factor: float


INDUSTRIES = [
    ("Retail", 1.00),
    ("Convenience", 0.72),
    ("Food Service", 1.18),
    ("E-commerce", 1.45),
    ("Manufacturing", 1.32),
    ("Pharma", 0.84),
]

SERVICE_TYPES = [
    ("Standard", 0.78),
    ("Cold Chain", 0.14),
    ("Priority", 0.08),
]

REGION_WEIGHTS = {
    "서울특별시": 1.55,
    "경기도": 1.45,
    "인천광역시": 1.20,
    "부산광역시": 1.18,
    "대구광역시": 1.02,
    "대전광역시": 0.96,
    "광주광역시": 0.92,
    "울산광역시": 0.88,
    "세종특별자치시": 0.72,
    "강원도": 0.70,
    "충청북도": 0.78,
    "충청남도": 0.86,
    "전라북도": 0.76,
    "전라남도": 0.74,
    "경상북도": 0.84,
    "경상남도": 0.90,
    "제주특별자치도": 0.62,
}


def month_range(start: date, months: int) -> list[str]:
    values: list[str] = []
    year = start.year
    month = start.month
    for _ in range(months):
        values.append(f"{year}-{month:02d}")
        month += 1
        if month == 13:
            year += 1
            month = 1
    return values


def region_group(sig_kor_nm: str) -> str:
    return sig_kor_nm.split()[0] if " " in sig_kor_nm else sig_kor_nm


def jitter(value: float, width: float) -> float:
    return round(value + random.uniform(-width, width), 9)


def build_customers(count: int = 420) -> list[Customer]:
    coords = pd.read_excel(COORD_PATH)
    coords = coords.dropna(subset=["SIG_CD", "SIG_KOR_NM", "x", "y"]).copy()
    coords["region_group"] = coords["SIG_KOR_NM"].map(region_group)
    coords["region_weight"] = coords["region_group"].map(REGION_WEIGHTS).fillna(0.75)

    sampled = coords.sample(
        n=count,
        replace=True,
        weights=coords["region_weight"],
        random_state=SEED,
    ).reset_index(drop=True)

    customers: list[Customer] = []
    for idx, row in sampled.iterrows():
        industry, industry_factor = random.choice(INDUSTRIES)
        size_factor = random.triangular(0.45, 2.4, 0.95) * industry_factor
        brand_no = idx + 1
        customers.append(
            Customer(
                cu_id=f"CU{brand_no:05d}",
                cu_nm=f"Sample {industry.replace(' ', '')} {brand_no:04d}",
                cu_add=f"{row['SIG_KOR_NM']} 데모로 {random.randint(10, 299)}",
                sig_cd=str(int(row["SIG_CD"])),
                sig_kor_nm=str(row["SIG_KOR_NM"]),
                lat_no=jitter(float(row["y"]), 0.035),
                lon_no=jitter(float(row["x"]), 0.035),
                industry=industry,
                region_group=str(row["region_group"]),
                size_factor=size_factor,
            )
        )
    return customers


def seasonal_index(month: str) -> float:
    mm = int(month[-2:])
    peak = {
        1: 1.06,
        2: 0.92,
        3: 0.98,
        4: 1.04,
        5: 1.08,
        6: 1.02,
        7: 1.12,
        8: 1.18,
        9: 1.04,
        10: 1.10,
        11: 1.22,
        12: 1.34,
    }
    return peak[mm]


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    random.seed(SEED)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    customers = build_customers()
    months = month_range(date(2024, 1, 1), 18)

    cu_rows = [
        {
            "CU_ID": c.cu_id,
            "CU_NM": c.cu_nm,
            "CU_ADD": c.cu_add,
            "SIG_CD": c.sig_cd,
            "SIG_KOR_NM": c.sig_kor_nm,
            "LAT_NO": c.lat_no,
            "LON_NO": c.lon_no,
            "INDUSTRY": c.industry,
            "REGION_GROUP": c.region_group,
        }
        for c in customers
    ]

    out_rows: list[dict[str, object]] = []
    out_id = 1
    for c in customers:
        active_months = random.sample(months, k=random.randint(11, len(months)))
        for ship_ym in sorted(active_months):
            region_factor = REGION_WEIGHTS.get(c.region_group, 0.75)
            base = 90 * c.size_factor * region_factor * seasonal_index(ship_ym)
            noise = random.lognormvariate(0, 0.28)
            order_cnt = max(1, round(base * noise / random.uniform(8.5, 17.5)))
            box_tot = round(order_cnt * random.uniform(7.0, 15.5), 3)
            service_type = random.choices(
                [s[0] for s in SERVICE_TYPES],
                weights=[s[1] for s in SERVICE_TYPES],
                k=1,
            )[0]
            out_rows.append(
                {
                    "OUT_ID": f"OUT{out_id:07d}",
                    "STO_NM": c.cu_nm,
                    "SHIP_YM": ship_ym,
                    "SERVICE_TYPE": service_type,
                    "ORDER_CNT": order_cnt,
                    "BOX_TOT": box_tot,
                    "WEIGHT_KG": round(box_tot * random.uniform(3.2, 9.8), 2),
                }
            )
            out_id += 1

    totals: dict[str, float] = {}
    for row in out_rows:
        totals[row["STO_NM"]] = totals.get(row["STO_NM"], 0.0) + float(row["BOX_TOT"])

    geo_rows = [
        {
            "CU_NM": c.cu_nm,
            "STO": c.sig_kor_nm,
            "ADDR": c.cu_add,
            "LAT_NO": c.lat_no,
            "LON_NO": c.lon_no,
            "BOX_TOT": round(totals[c.cu_nm], 3),
            "INDUSTRY": c.industry,
            "REGION_GROUP": c.region_group,
        }
        for c in customers
    ]

    write_csv(
        RAW_DIR / "kyo_cu_mst_sample.csv",
        cu_rows,
        ["CU_ID", "CU_NM", "CU_ADD", "SIG_CD", "SIG_KOR_NM", "LAT_NO", "LON_NO", "INDUSTRY", "REGION_GROUP"],
    )
    write_csv(
        RAW_DIR / "kyo_out_sample.csv",
        out_rows,
        ["OUT_ID", "STO_NM", "SHIP_YM", "SERVICE_TYPE", "ORDER_CNT", "BOX_TOT", "WEIGHT_KG"],
    )
    write_csv(
        PROCESSED_DIR / "geo_box_sample.csv",
        geo_rows,
        ["CU_NM", "STO", "ADDR", "LAT_NO", "LON_NO", "BOX_TOT", "INDUSTRY", "REGION_GROUP"],
    )

    print(f"Generated {len(cu_rows):,} customers")
    print(f"Generated {len(out_rows):,} outbound records")
    print(f"Generated {len(geo_rows):,} processed geocoded rows")


if __name__ == "__main__":
    main()
