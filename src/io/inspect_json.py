from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.io.json_loader import load_squareyards_json


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="Path to whitefield.json")
    args = ap.parse_args()

    data = load_squareyards_json(args.inp)

    # Pretty print the normalized dict so you can audit values quickly
    print("\n=== Normalized locality snapshot ===")
    print(json.dumps({k: v for k, v in data.items() if k != "_raw"}, indent=2, ensure_ascii=False))

    # A compact human-readable line too
    print("\n=== Key metrics ===")
    print(
        "Locality: {name}, City: {city}, Rank: {rank}\n"
        "Avg ₹/sq ft: {psf}, Avg monthly rent: {rent}, Sale listings: {sale}, Rent listings: {rl}\n"
        "Rating: {rating} from {rc} reviews, Nearby count: {nb}"
        .format(
            name=data.get("locality_name"),
            city=data.get("city_name"),
            rank=data.get("locality_rank_in_city"),
            psf=data.get("avg_sale_price_psf"),
            rent=data.get("avg_rent_price"),
            sale=data.get("sale_property_count"),
            rl=data.get("rent_property_count"),
            rating=data.get("overall_rating"),
            rc=data.get("total_review_count"),
            nb=len(data.get("nearby_localities") or []),
        )
    )

    # Show a few nearby localities with any price/rent numbers we found
    nbs = data.get("nearby_localities") or []
    if nbs:
        print("\n=== Nearby sample ===")
        for nb in nbs[:8]:
            print(
                "- {name:25} | rank: {rank!s:>4} | ₹/sq ft: {psf!s:>8} | rent ₹/sq ft: {rpsf!s:>6} | sale: {sc!s:>3} | rent: {rc!s:>3}"
                .format(
                    name=nb.get("name", ""),
                    rank=nb.get("rank_in_city"),
                    psf=nb.get("typical_price_psf"),
                    rpsf=nb.get("avg_rent_psf"),
                    sc=nb.get("sale_count"),
                    rc=nb.get("rent_count"),
                )
            )


if __name__ == "__main__":
    main()