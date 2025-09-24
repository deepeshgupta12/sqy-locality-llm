from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# --- Small helper models ------------------------------------------------------

class RangePSF(BaseModel):
    min: Optional[float] = None
    max: Optional[float] = None


class RentalRange(BaseModel):
    min: Optional[float] = None
    max: Optional[float] = None


class NearbyHub(BaseModel):
    name: str
    distance_km: Optional[float] = None


class POI(BaseModel):
    name: str
    distance_km: Optional[float] = None
    category: Optional[str] = None


class TransportPoint(BaseModel):
    name: str
    distance_km: Optional[float] = None
    line: Optional[str] = None


class DeveloperStats(BaseModel):
    name: str
    total: Optional[int] = None
    new_launch: Optional[int] = None
    under_construction: Optional[int] = None
    ready_to_move: Optional[int] = None


class SourceRef(BaseModel):
    name: str
    url: str


class CultureDemoGeo(BaseModel):
    culture_points: List[str] = Field(default_factory=list)
    demographic_notes: List[str] = Field(default_factory=list)
    geo_notes: List[str] = Field(default_factory=list)
    sources: List[SourceRef] = Field(default_factory=list)


class LocalNewsItem(BaseModel):
    title: str
    date: Optional[str] = None   # "YYYY-MM-DD"
    summary: Optional[str] = None
    source_name: Optional[str] = None
    source_url: Optional[str] = None


class NearbyLocality(BaseModel):
    name: str
    rating: Optional[float] = None
    sale_count: Optional[int] = None
    rent_count: Optional[int] = None
    new_project_count: Optional[int] = None
    rank_in_city: Optional[int] = None
    typical_price_psf: Optional[float] = None
    avg_rent_month: Optional[float] = None
    best_for: Optional[str] = None
    url: Optional[str] = None


class Link(BaseModel):
    label: str
    href: str


class Interlinking(BaseModel):
    primary: List[Link] = Field(default_factory=list)
    secondary: List[Link] = Field(default_factory=list)
    developer: List[Link] = Field(default_factory=list)


class PriceBands(BaseModel):
    affordable_psf: Optional[float] = None
    typical_psf: Optional[float] = None
    premium_psf: Optional[float] = None


# --- Main input model ---------------------------------------------------------

class LocalityInput(BaseModel):
    # Identity
    locality_name: str
    city_name: str
    micromarket_name: Optional[str] = None
    pincode: Optional[str] = None
    slug: Optional[str] = None

    # Coordinates (if available)
    lat: Optional[float] = None
    lng: Optional[float] = None

    # Ranking & rating
    locality_rank_in_city: Optional[int] = None
    overall_city_locality_count: Optional[int] = None
    overall_rating: Optional[float] = None
    total_review_count: Optional[int] = None

    # Indices (0–5 or 0–10 as per your data)
    lifestyle_index: Optional[float] = None
    livability_index: Optional[float] = None
    connectivity_index: Optional[float] = None
    edu_health_index: Optional[float] = None

    # Stock counts
    new_launch_project_count: Optional[int] = None
    under_construction_project_count: Optional[int] = None
    partially_ready_to_move_society_count: Optional[int] = None
    ready_to_move_society_count: Optional[int] = None
    developed_project_count: Optional[int] = None
    resale_property_count: Optional[int] = None
    sale_property_count: Optional[int] = None
    rent_property_count: Optional[int] = None

    # Mix
    property_types: List[str] = Field(default_factory=list)
    property_type_counts: Dict[str, int] = Field(default_factory=dict)
    bhk_types: List[str] = Field(default_factory=list)
    bhk_type_property_count: Dict[str, int] = Field(default_factory=dict)

    # Demand/Supply (fractions, 0–1)
    major_property_type_demand_buy: Dict[str, float] = Field(default_factory=dict)
    major_bhk_type_demand_rent: Dict[str, float] = Field(default_factory=dict)
    major_property_type_supply_buy: Dict[str, float] = Field(default_factory=dict)
    major_bhk_type_supply_rent: Dict[str, float] = Field(default_factory=dict)

    # Pricing
    avg_sale_price_psf: Optional[float] = None
    sale_price_range_psf: Optional[RangePSF] = None
    price_bands_psf: PriceBands = Field(default_factory=PriceBands)
    asking_price_change_pct_3m: Optional[float] = None

    # Rental
    avg_rent_price: Optional[float] = None
    rental_price_range: Optional[RentalRange] = None
    rent_price_change_pct_3m: Optional[float] = None
    blended_gross_yield_pct: Optional[float] = None

    # Registrations / Govt
    gov_txn_count: Optional[int] = None
    gov_txn_value_inr: Optional[float] = None
    avg_registered_rate_psf: Optional[float] = None
    gov_txn_period_start: Optional[str] = None
    gov_txn_period_end: Optional[str] = None

    # Absorption
    absorption_90d: Optional[int] = None
    months_of_inventory: Optional[float] = None

    # Infra & commute
    major_interlinking_roads: List[str] = Field(default_factory=list)
    nearby_employment_hubs: List[NearbyHub] = Field(default_factory=list)
    nearest_metro: Optional[TransportPoint] = None
    nearest_bus_stand: Optional[TransportPoint] = None
    nearest_airport: Optional[TransportPoint] = None

    # Amenities
    schools_colleges: List[POI] = Field(default_factory=list)
    hospitals: List[POI] = Field(default_factory=list)
    malls: List[POI] = Field(default_factory=list)
    restaurants: List[POI] = Field(default_factory=list)
    spiritual_places: List[POI] = Field(default_factory=list)
    parks_open_spaces: List[POI] = Field(default_factory=list)
    hotels: List[POI] = Field(default_factory=list)

    # Developers & pipeline
    popular_developers: List[DeveloperStats] = Field(default_factory=list)
    project_pipeline_catalysts: List[Dict[str, Any]] = Field(default_factory=list)
    rera_coverage_pct: Optional[int] = None

    # Nearby localities
    nearby_localities: List[NearbyLocality] = Field(default_factory=list)

    # SEO
    primary_keywords: List[str] = Field(default_factory=list)
    secondary_keywords: List[str] = Field(default_factory=list)
    meta_title_max60: Optional[str] = None
    meta_description_max160: Optional[str] = None
    breadcrumb_trail: List[str] = Field(default_factory=list)
    schema_place: Dict[str, Any] = Field(default_factory=dict)
    data_window_months: Optional[int] = None
    last_updated_at: Optional[str] = None
    currency: Optional[str] = None
    area_unit: Optional[str] = None
    psf_unit: Optional[str] = None
    interlinking: Optional[Interlinking] = None

    # Data hygiene
    data_completeness_score: Optional[float] = None
    disclaimer_required: bool = True

    # Web enrichment (optional)
    culture_demo_geo: Optional[CultureDemoGeo] = None
    local_news: Optional[List[LocalNewsItem]] = None