import csv
import io
import math
from datetime import datetime
import textwrap
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import requests
import streamlit as st
import pydeck as pdk
import pandas as pd
import altair as alt

WB_BASE = "https://api.worldbank.org/v2"
ODS_BASE = "https://public.opendatasoft.com/api/records/1.0/search/"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"


I18N = {
    "es": {
        "app_title": "Radar de Inversion Global",
        "app_subtitle": "Datos reales (World Bank, ONU/OpenDataSoft, OpenStreetMap).",
        "language": "Idioma",
        "country": "Pais",
        "city": "Ciudad",
        "top_cities": "Top 3 ciudades para inversion",
        "investment_hint": "Selecciona una ciudad y un negocio para sugerencias y competencia.",
        "business_category": "Categoria de negocio (120 opciones)",
        "search_business": "Buscar negocio",
        "city_zones": "Zonas dentro de la ciudad",
        "malls_offices": "Centros comerciales y oficinas",
        "competition": "Analisis de competencia",
        "competition_count": "Competidores encontrados",
        "data_notes": "Notas de datos",
        "country_metrics": "Indicadores del pais",
        "gdp": "PIB (USD)",
        "gdp_pc": "PIB per capita (USD)",
        "population": "Poblacion",
        "density": "Densidad (hab/km2)",
        "inflation": "Inflacion (IPC, %)",
        "unemployment": "Desempleo (%)",
        "growth": "Crecimiento PIB (%)",
        "tax_revenue": "Impuestos (% PIB)",
        "current_account": "Balanza cuenta corriente (% PIB)",
        "median_age": "Edad media (anos)",
        "risk_score": "Riesgo pais (WGI promedio)",
        "risk_level": "Nivel de riesgo",
        "urbanization": "Urbanizacion (%)",
        "labor_force": "Participacion laboral (%)",
        "cost_m2": "Costo por m2 (USD, ciudad)",
        "rent_month": "Alquiler mensual (USD, ciudad)",
        "potential_clients": "Clientes potenciales (estimado)",
        "updated": "Ultimo dato disponible",
        "no_data": "No hay datos disponibles.",
        "zones_empty": "No se encontraron zonas (intenta otra ciudad).",
        "pois_empty": "No se encontraron centros comerciales u oficinas.",
        "category_empty": "No se encontraron competidores con esa categoria.",
        "sources": "Fuentes: World Bank API, OpenDataSoft, OpenStreetMap (Overpass).",
        "cost_note": "El costo por m2 depende de datasets publicos por ciudad y puede no estar disponible.",
        "rent_note": "El alquiler mensual no tiene fuente global abierta; se muestra solo si hay datos.",
        "clients_note": "Clientes potenciales: estimado con poblacion de la ciudad y participacion laboral.",
        "econ_block": "Indicadores economicos",
        "risk_block": "Riesgo y demografia",
        "housing_block": "Vivienda y demanda",
        "ranking_block": "Ranking de ciudades",
        "ranking_note": "El ranking usa datos de pais + poblacion ciudad.",
        "compare_block": "Comparar paises",
        "alerts_block": "Alertas",
        "exports_block": "Exportar reportes",
        "map_block": "Mapa de competencia y zonas",
        "best_categories": "Mejores categorias (baja competencia)",
        "zone_types": "Tipos de zonas",
        "max_points": "Maximo de puntos en mapa",
        "weight_population": "Peso poblacion",
        "weight_gdp_pc": "Peso PIB per capita",
        "weight_inflation": "Peso inflacion (negativo)",
        "weight_unemployment": "Peso desempleo (negativo)",
        "weight_growth": "Peso crecimiento PIB",
        "weight_risk": "Peso riesgo pais",
        "alert_inflation": "Alerta inflacion si >",
        "alert_unemployment": "Alerta desempleo si >",
        "alert_risk": "Alerta riesgo si <",
        "download_country": "Descargar indicadores pais (CSV)",
        "download_cities": "Descargar top ciudades (CSV)",
        "download_report": "Descargar reporte (TXT)",
        "map_empty": "No hay puntos para mostrar en el mapa.",
        "best_hint": "Esto puede tardar por consultas a OpenStreetMap.",
        "top_n": "Top N",
        "categories_to_eval": "Categorias a evaluar",
        "table_category": "Categoria",
        "table_competitors": "Competidores",
        "summary_block": "Resumen ejecutivo",
        "composite_score": "Score compuesto",
        "demand_index": "Indice de demanda",
        "data_quality": "Calidad de datos",
        "compare_cities": "Comparar ciudades",
        "radius_km": "Radio de competencia (km)",
        "heatmap": "Mapa de calor",
        "watchlist": "Lista de seguimiento",
        "add_watchlist": "Agregar a seguimiento",
        "remove_watchlist": "Quitar de seguimiento",
        "watchlist_empty": "Tu lista esta vacia.",
        "export_watchlist": "Descargar seguimiento (CSV)",
        "series_block": "Series historicas",
        "series_hint": "Ultimos anos disponibles (World Bank).",
        "recommendations": "Recomendaciones",
        "recommendation_note": "Categorias con baja competencia y alta demanda.",
        "city_compare_chart": "Comparativo de ciudades",
        "assistant_block": "Asistente IA",
        "assistant_intro": "Pregunta sobre funciones o como usar la app.",
        "assistant_placeholder": "Escribe tu pregunta...",
        "assistant_unknown": "No estoy seguro. Prueba con: ranking, mapa, competencia, exportar, series, alertas.",
        "visual_block": "Visual corporativo",
        "visual_note": "Imagenes ilustrativas: bandera y centro financiero.",
        "risk_low": "Bajo",
        "risk_medium": "Medio",
        "risk_high": "Alto",
        "latest_year_label": "Ultimo ano",
        "cities_indexed_label": "Ciudades indexadas",
        "top_city_pop_label": "Poblacion ciudad top",
    },
    "en": {
        "app_title": "Global Investment Radar",
        "app_subtitle": "Live data (World Bank, UN/OpenDataSoft, OpenStreetMap).",
        "language": "Language",
        "country": "Country",
        "city": "City",
        "top_cities": "Top 3 cities for investment",
        "investment_hint": "Pick a city and a business to see suggestions and competition.",
        "business_category": "Business category (120 options)",
        "search_business": "Search business",
        "city_zones": "Zones within the city",
        "malls_offices": "Malls and offices",
        "competition": "Competition analysis",
        "competition_count": "Competitors found",
        "data_notes": "Data notes",
        "country_metrics": "Country indicators",
        "gdp": "GDP (USD)",
        "gdp_pc": "GDP per capita (USD)",
        "population": "Population",
        "density": "Density (people/km2)",
        "inflation": "Inflation (CPI, %)",
        "unemployment": "Unemployment (%)",
        "growth": "GDP growth (%)",
        "tax_revenue": "Tax revenue (% GDP)",
        "current_account": "Current account (% GDP)",
        "median_age": "Median age (years)",
        "risk_score": "Country risk (WGI avg)",
        "risk_level": "Risk level",
        "urbanization": "Urbanization (%)",
        "labor_force": "Labor force participation (%)",
        "cost_m2": "Cost per m2 (USD, city)",
        "rent_month": "Monthly rent (USD, city)",
        "potential_clients": "Potential clients (estimate)",
        "updated": "Latest available data",
        "no_data": "No data available.",
        "zones_empty": "No zones found (try another city).",
        "pois_empty": "No malls or offices found.",
        "category_empty": "No competitors found for this category.",
        "sources": "Sources: World Bank API, OpenDataSoft, OpenStreetMap (Overpass).",
        "cost_note": "Cost per m2 depends on public city datasets and may be unavailable.",
        "rent_note": "Monthly rent lacks a global open dataset; shown only when available.",
        "clients_note": "Potential clients: estimate using city population and labor participation.",
        "econ_block": "Economic indicators",
        "risk_block": "Risk and demographics",
        "housing_block": "Housing and demand",
        "ranking_block": "City ranking",
        "ranking_note": "Ranking uses country data + city population.",
        "compare_block": "Compare countries",
        "alerts_block": "Alerts",
        "exports_block": "Export reports",
        "map_block": "Competition and zones map",
        "best_categories": "Best categories (low competition)",
        "zone_types": "Zone types",
        "max_points": "Max points on map",
        "weight_population": "Population weight",
        "weight_gdp_pc": "GDP per capita weight",
        "weight_inflation": "Inflation weight (negative)",
        "weight_unemployment": "Unemployment weight (negative)",
        "weight_growth": "GDP growth weight",
        "weight_risk": "Country risk weight",
        "alert_inflation": "Inflation alert if >",
        "alert_unemployment": "Unemployment alert if >",
        "alert_risk": "Risk alert if <",
        "download_country": "Download country indicators (CSV)",
        "download_cities": "Download top cities (CSV)",
        "download_report": "Download report (TXT)",
        "map_empty": "No points to show on map.",
        "best_hint": "This can take time due to OpenStreetMap queries.",
        "top_n": "Top N",
        "categories_to_eval": "Categories to evaluate",
        "table_category": "Category",
        "table_competitors": "Competitors",
        "summary_block": "Executive summary",
        "composite_score": "Composite score",
        "demand_index": "Demand index",
        "data_quality": "Data quality",
        "compare_cities": "Compare cities",
        "radius_km": "Competition radius (km)",
        "heatmap": "Heatmap",
        "watchlist": "Watchlist",
        "add_watchlist": "Add to watchlist",
        "remove_watchlist": "Remove from watchlist",
        "watchlist_empty": "Your watchlist is empty.",
        "export_watchlist": "Download watchlist (CSV)",
        "series_block": "Historical series",
        "series_hint": "Latest available years (World Bank).",
        "recommendations": "Recommendations",
        "recommendation_note": "Low competition and high demand categories.",
        "city_compare_chart": "City comparison",
        "assistant_block": "AI assistant",
        "assistant_intro": "Ask about features or how to use the app.",
        "assistant_placeholder": "Type your question...",
        "assistant_unknown": "Not sure. Try: ranking, map, competition, export, series, alerts.",
        "visual_block": "Corporate visuals",
        "visual_note": "Illustrative images: flag and financial center.",
        "risk_low": "Low",
        "risk_medium": "Medium",
        "risk_high": "High",
        "latest_year_label": "Latest year",
        "cities_indexed_label": "Cities indexed",
        "top_city_pop_label": "Top city population",
    },
}


BUSINESS_CATEGORIES = [
    "Restaurant",
    "Cafe",
    "Bakery",
    "Supermarket",
    "Convenience Store",
    "Pharmacy",
    "Hospital",
    "Clinic",
    "Dentist",
    "Veterinary",
    "Gym",
    "Yoga Studio",
    "Spa",
    "Salon",
    "Bar",
    "Nightclub",
    "Cinema",
    "Theater",
    "Museum",
    "Art Gallery",
    "Bookstore",
    "Electronics Store",
    "Hardware Store",
    "Furniture Store",
    "Clothing Store",
    "Shoe Store",
    "Jewelry Store",
    "Florist",
    "Pet Store",
    "Toy Store",
    "Stationery",
    "Bank",
    "ATM",
    "Insurance Office",
    "Real Estate Office",
    "Law Firm",
    "Accounting Office",
    "Coworking Space",
    "Office Building",
    "Mall",
    "Market",
    "Warehouse",
    "Logistics",
    "Gas Station",
    "Car Wash",
    "Car Repair",
    "Car Dealership",
    "Bike Shop",
    "Sports Store",
    "Outdoor Store",
    "Hotel",
    "Hostel",
    "Apartment Rental",
    "Travel Agency",
    "School",
    "University",
    "Language School",
    "Daycare",
    "Music School",
    "Tech Startup",
    "IT Services",
    "Telecom Store",
    "Printing Shop",
    "Marketing Agency",
    "Photography Studio",
    "Event Venue",
    "Convention Center",
    "Wedding Services",
    "Security Services",
    "Cleaning Services",
    "Construction Company",
    "Architect",
    "Engineering Firm",
    "Manufacturing",
    "Food Processing",
    "Beverage Producer",
    "Farm",
    "Agri Supplies",
    "Greenhouse",
    "Wholesale",
    "Import/Export",
    "E-commerce Warehouse",
    "Parcel Locker",
    "Delivery Services",
    "Mobile Repair",
    "Data Center",
    "Internet Cafe",
    "Gaming Lounge",
    "Arcade",
    "Library",
    "Religious Center",
    "Government Office",
    "Post Office",
    "Recycling Center",
    "Renewable Energy",
    "Solar Installer",
    "EV Charging",
    "Parking Garage",
    "Taxi Stand",
    "Bus Station",
    "Train Station",
    "Airport Services",
    "Port Logistics",
    "Water Utility",
    "Waste Management",
    "Telemedicine",
    "Elder Care",
    "Rehabilitation Center",
    "Sports Club",
    "Stadium",
    "Swimming Pool",
    "Dance Studio",
    "Film Studio",
    "Podcast Studio",
    "Influencer Agency",
    "Coaching Center",
    "Test Prep Center",
    "Translation Services",
    "Call Center",
    "Customer Support",
    "HR Agency",
    "Staffing Agency",
    "Research Lab",
    "Biotech",
    "Fintech",
    "Insurtech",
    "Legal Tech",
    "EdTech",
    "HealthTech",
    "Retail Analytics",
    "Supply Chain Tech",
    "Property Management",
    "Home Services",
    "Handyman",
    "Laundry",
    "Dry Cleaner",
    "Tailor",
    "Security Systems",
    "Fire Safety",
    "Auto Parts",
    "Marine Services",
    "Mining Services",
    "Oil & Gas Services",
    "Industrial Park",
    "Business Park",
    "R&D Center",
    "Exhibition Center",
    "Local Market",
    "Crafts Store",
    "Organic Store",
    "Health Food",
    "Butcher",
    "Fish Market",
    "Beauty Supply",
    "Cosmetics Store",
    "Home Decor",
    "Kitchenware",
    "Mobile Accessories",
    "Kids Store",
    "Outlet Store",
    "Duty Free",
    "Warehouse Club",
    "Office Supplies",
    "Copy Center",
    "Courier Office",
    "Notary",
    "Immigration Services",
    "Tax Services",
    "Investment Office",
    "Venture Capital",
    "Private Equity",
    "Microfinance",
    "Credit Union",
    "Community Bank",
    "Payments Provider",
    "Blockchain Services",
    "AI Services",
]


BUSINESS_OSM_MAP = {
    "Restaurant": ("amenity", "restaurant"),
    "Cafe": ("amenity", "cafe"),
    "Bakery": ("shop", "bakery"),
    "Supermarket": ("shop", "supermarket"),
    "Convenience Store": ("shop", "convenience"),
    "Pharmacy": ("amenity", "pharmacy"),
    "Hospital": ("amenity", "hospital"),
    "Clinic": ("amenity", "clinic"),
    "Dentist": ("amenity", "dentist"),
    "Veterinary": ("amenity", "veterinary"),
    "Gym": ("leisure", "fitness_centre"),
    "Bar": ("amenity", "bar"),
    "Nightclub": ("amenity", "nightclub"),
    "Cinema": ("amenity", "cinema"),
    "Theater": ("amenity", "theatre"),
    "Bookstore": ("shop", "books"),
    "Electronics Store": ("shop", "electronics"),
    "Hardware Store": ("shop", "hardware"),
    "Furniture Store": ("shop", "furniture"),
    "Clothing Store": ("shop", "clothes"),
    "Shoe Store": ("shop", "shoes"),
    "Jewelry Store": ("shop", "jewelry"),
    "Florist": ("shop", "florist"),
    "Pet Store": ("shop", "pet"),
    "Toy Store": ("shop", "toys"),
    "Bank": ("amenity", "bank"),
    "ATM": ("amenity", "atm"),
    "Real Estate Office": ("office", "real_estate_agent"),
    "Coworking Space": ("office", "coworking"),
    "Office Building": ("building", "office"),
    "Mall": ("shop", "mall"),
    "Market": ("amenity", "marketplace"),
    "Gas Station": ("amenity", "fuel"),
    "Car Wash": ("amenity", "car_wash"),
    "Car Repair": ("shop", "car_repair"),
    "Hotel": ("tourism", "hotel"),
    "Hostel": ("tourism", "hostel"),
    "School": ("amenity", "school"),
    "University": ("amenity", "university"),
    "Post Office": ("amenity", "post_office"),
}


@dataclass
class CityRecord:
    name: str
    country: str
    population: Optional[int]
    lat: Optional[float]
    lon: Optional[float]


def t(lang: str, key: str) -> str:
    return I18N.get(lang, I18N["en"]).get(key, key)


@st.cache_data(show_spinner=False, ttl=86400)
def fetch_json(url: str, params: Optional[Dict[str, str]] = None) -> Optional[dict]:
    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code != 200:
            return None
        return response.json()
    except requests.RequestException:
        return None


@st.cache_data(show_spinner=False, ttl=86400)
def fetch_countries() -> List[Tuple[str, str, str]]:
    data = fetch_json(f"{WB_BASE}/country", params={"format": "json", "per_page": "400"})
    if not data or len(data) < 2:
        return []
    countries = []
    for item in data[1]:
        if item.get("region", {}).get("id") == "NA":
            continue
        iso2 = item.get("iso2Code")
        iso3 = item.get("id")
        name = item.get("name")
        if iso2 and iso3 and name:
            countries.append((iso2, iso3, name))
    return sorted(countries, key=lambda x: x[2])


@st.cache_data(show_spinner=False, ttl=86400)
def fetch_indicator(country_code: str, indicator: str) -> Tuple[Optional[float], Optional[int]]:
    url = f"{WB_BASE}/country/{country_code}/indicator/{indicator}"
    data = fetch_json(url, params={"format": "json", "per_page": "10"})
    if not data or len(data) < 2:
        return None, None
    for row in data[1]:
        if row.get("value") is not None:
            return row.get("value"), row.get("date")
    return None, None


@st.cache_data(show_spinner=False, ttl=86400)
def fetch_wgi_risk(country_code: str) -> Tuple[Optional[float], Optional[int]]:
    indicators = ["CC.EST", "GE.EST", "PV.EST", "RL.EST", "RQ.EST", "VA.EST"]
    values = []
    years = []
    for indicator in indicators:
        value, year = fetch_indicator(country_code, indicator)
        if value is not None:
            values.append(value)
        if year is not None:
            years.append(year)
    if not values:
        return None, None
    avg = sum(values) / len(values)
    year = max(years) if years else None
    return avg, year


@st.cache_data(show_spinner=False, ttl=86400)
def fetch_worldcities(country_code: str) -> List[CityRecord]:
    params = {
        "dataset": "geonames-all-cities-with-a-population-1000",
        "rows": "500",
        "sort": "population",
        "refine.country_code": country_code.upper(),
    }
    data = fetch_json(ODS_BASE, params=params)
    if not data or "records" not in data:
        return []
    cities = []
    for record in data["records"]:
        fields = record.get("fields", {})
        pop = fields.get("population")
        try:
            pop = int(pop) if pop else None
        except (TypeError, ValueError):
            pop = None
        coords = fields.get("coordinates") or []
        lat = coords[0] if len(coords) >= 2 else None
        lon = coords[1] if len(coords) >= 2 else None
        cities.append(
            CityRecord(
                name=fields.get("name") or fields.get("ascii_name") or "",
                country=fields.get("cou_name_en") or "",
                population=pop,
                lat=lat,
                lon=lon,
            )
        )
    return cities


@st.cache_data(show_spinner=False, ttl=86400)
def fetch_city_cost_m2(city: str, country: str) -> Optional[float]:
    params = {
        "dataset": "numbeo",
        "q": f"{city} {country}",
        "rows": "1",
    }
    data = fetch_json(ODS_BASE, params=params)
    if not data or "records" not in data or not data["records"]:
        return None
    fields = data["records"][0].get("fields", {})
    for key in (
        "price_to_buy_apartment_city_centre_usd",
        "price_to_buy_apartment_city_centre",
    ):
        value = fields.get(key)
        if value:
            try:
                return float(value)
            except (TypeError, ValueError):
                continue
    return None


@st.cache_data(show_spinner=False, ttl=86400)
def fetch_city_rent(city: str, country: str) -> Optional[float]:
    # No global public dataset for city-level rent in OpenDataSoft at the moment.
    # Keep placeholder for future data sources.
    return None


def overpass_query(query: str) -> Optional[dict]:
    try:
        response = requests.post(OVERPASS_URL, data={"data": query}, timeout=60)
        if response.status_code != 200:
            return None
        return response.json()
    except requests.RequestException:
        return None


@st.cache_data(show_spinner=False, ttl=3600)
def fetch_city_zones(city: str, country_code: str, lat: Optional[float], lon: Optional[float]) -> List[str]:
    if lat is not None and lon is not None:
        area_filter = f"(around:15000,{lat},{lon})"
    else:
        area_filter = f'(area["name"="{city}"]["boundary"="administrative"]["ISO3166-1"="{country_code}"])'
    query = textwrap.dedent(
        f"""
        [out:json][timeout:25];
        (
          node["place"~"neighbourhood|suburb"]{area_filter};
          way["place"~"neighbourhood|suburb"]{area_filter};
          relation["place"~"neighbourhood|suburb"]{area_filter};
        );
        out tags;
        """
    ).strip()
    data = overpass_query(query)
    if not data or "elements" not in data:
        return []
    zones = []
    for element in data["elements"]:
        tags = element.get("tags", {})
        name = tags.get("name")
        if name:
            zones.append(name)
    return sorted(set(zones))


@st.cache_data(show_spinner=False, ttl=3600)
def fetch_malls_offices(city: str, country_code: str, lat: Optional[float], lon: Optional[float]) -> List[str]:
    if lat is not None and lon is not None:
        area_filter = f"(around:15000,{lat},{lon})"
    else:
        area_filter = f'(area["name"="{city}"]["boundary"="administrative"]["ISO3166-1"="{country_code}"])'
    query = textwrap.dedent(
        f"""
        [out:json][timeout:25];
        (
          node["shop"="mall"]{area_filter};
          way["shop"="mall"]{area_filter};
          relation["shop"="mall"]{area_filter};
          node["building"="office"]{area_filter};
          way["building"="office"]{area_filter};
          relation["building"="office"]{area_filter};
          node["office"]{area_filter};
        );
        out tags;
        """
    ).strip()
    data = overpass_query(query)
    if not data or "elements" not in data:
        return []
    pois = []
    for element in data["elements"]:
        tags = element.get("tags", {})
        name = tags.get("name")
        if name:
            pois.append(name)
    return sorted(set(pois))


@st.cache_data(show_spinner=False, ttl=3600)
def fetch_competitors(
    city: str,
    country_code: str,
    category: str,
    lat: Optional[float],
    lon: Optional[float],
    radius_m: int,
) -> int:
    osm_tag = BUSINESS_OSM_MAP.get(category)
    if osm_tag:
        key, value = osm_tag
        filter_part = f'["{key}"="{value}"]'
    else:
        keyword = category.split()[0]
        filter_part = f'["name"~"{keyword}",i]'
    if lat is not None and lon is not None:
        area_filter = f"(around:{radius_m},{lat},{lon})"
    else:
        area_filter = f'(area["name"="{city}"]["boundary"="administrative"]["ISO3166-1"="{country_code}"])'
    query = textwrap.dedent(
        f"""
        [out:json][timeout:25];
        (
          node{filter_part}{area_filter};
          way{filter_part}{area_filter};
          relation{filter_part}{area_filter};
        );
        out count;
        """
    ).strip()
    data = overpass_query(query)
    if not data or "elements" not in data:
        return 0
    for element in data["elements"]:
        if element.get("type") == "count":
            return int(element.get("tags", {}).get("total", 0))
    return 0


def build_area_filter(
    city: str, country_code: str, lat: Optional[float], lon: Optional[float], radius_m: int
) -> str:
    if lat is not None and lon is not None:
        return f"(around:{radius_m},{lat},{lon})"
    return f'(area["name"="{city}"]["boundary"="administrative"]["ISO3166-1"="{country_code}"])'


def extract_points(elements: List[dict], limit: int) -> List[dict]:
    points = []
    for element in elements:
        tags = element.get("tags", {})
        name = tags.get("name")
        if "lat" in element and "lon" in element:
            points.append({"lat": element["lat"], "lon": element["lon"], "name": name})
        elif "center" in element:
            center = element.get("center", {})
            if "lat" in center and "lon" in center:
                points.append({"lat": center["lat"], "lon": center["lon"], "name": name})
        if len(points) >= limit:
            break
    return points


@st.cache_data(show_spinner=False, ttl=3600)
def fetch_zone_points(
    city: str,
    country_code: str,
    lat: Optional[float],
    lon: Optional[float],
    zone_types: List[str],
    limit: int,
    radius_m: int,
) -> List[dict]:
    zone_filter = "|".join(zone_types) if zone_types else "neighbourhood|suburb|quarter|district"
    area_filter = build_area_filter(city, country_code, lat, lon, radius_m)
    query = textwrap.dedent(
        f"""
        [out:json][timeout:25];
        (
          node["place"~"{zone_filter}"]{area_filter};
          way["place"~"{zone_filter}"]{area_filter};
          relation["place"~"{zone_filter}"]{area_filter};
        );
        out center;
        """
    ).strip()
    data = overpass_query(query)
    if not data or "elements" not in data:
        return []
    return extract_points(data["elements"], limit)


@st.cache_data(show_spinner=False, ttl=3600)
def fetch_competitor_points(
    city: str,
    country_code: str,
    category: str,
    lat: Optional[float],
    lon: Optional[float],
    limit: int,
    radius_m: int,
) -> List[dict]:
    osm_tag = BUSINESS_OSM_MAP.get(category)
    if osm_tag:
        key, value = osm_tag
        filter_part = f'["{key}"="{value}"]'
    else:
        keyword = category.split()[0]
        filter_part = f'["name"~"{keyword}",i]'
    area_filter = build_area_filter(city, country_code, lat, lon, radius_m)
    query = textwrap.dedent(
        f"""
        [out:json][timeout:25];
        (
          node{filter_part}{area_filter};
          way{filter_part}{area_filter};
          relation{filter_part}{area_filter};
        );
        out center;
        """
    ).strip()
    data = overpass_query(query)
    if not data or "elements" not in data:
        return []
    return extract_points(data["elements"], limit)


@st.cache_data(show_spinner=False, ttl=86400)
def fetch_country_snapshot(country_code: str) -> Dict[str, Optional[float]]:
    snapshot = {}
    indicators = {
        "gdp": "NY.GDP.MKTP.CD",
        "gdp_pc": "NY.GDP.PCAP.CD",
        "population": "SP.POP.TOTL",
        "density": "EN.POP.DNST",
        "inflation": "FP.CPI.TOTL.ZG",
        "unemployment": "SL.UEM.TOTL.ZS",
        "growth": "NY.GDP.MKTP.KD.ZG",
        "tax_revenue": "GC.TAX.TOTL.GD.ZS",
        "current_account": "BN.CAB.XOKA.GD.ZS",
        "median_age": "SP.POP.MEDN",
        "urbanization": "SP.URB.TOTL.IN.ZS",
        "labor_force": "SL.TLF.CACT.ZS",
    }
    for key, code in indicators.items():
        value, _ = fetch_indicator(country_code, code)
        snapshot[key] = value
    risk_score, _ = fetch_wgi_risk(country_code)
    snapshot["risk_score"] = risk_score
    return snapshot


@st.cache_data(show_spinner=False, ttl=86400)
def fetch_indicator_series(country_code: str, indicator: str, limit: int = 10) -> List[Tuple[int, float]]:
    url = f"{WB_BASE}/country/{country_code}/indicator/{indicator}"
    data = fetch_json(url, params={"format": "json", "per_page": str(limit)})
    if not data or len(data) < 2:
        return []
    series = []
    for row in data[1]:
        value = row.get("value")
        date = row.get("date")
        if value is None or date is None:
            continue
        try:
            series.append((int(date), float(value)))
        except (TypeError, ValueError):
            continue
    return sorted(series, key=lambda x: x[0])


def compute_city_score(
    city_population: Optional[int],
    gdp_pc: Optional[float],
    inflation: Optional[float],
    unemployment: Optional[float],
    growth: Optional[float],
    risk_score: Optional[float],
    weights: Dict[str, float],
) -> float:
    pop_score = math.log(max(city_population or 1, 1))
    gdp_score = math.log(max(gdp_pc or 1, 1))
    inflation_score = inflation or 0
    unemployment_score = unemployment or 0
    growth_score = growth or 0
    risk = risk_score or 0
    return (
        weights["population"] * pop_score
        + weights["gdp_pc"] * gdp_score
        - weights["inflation"] * inflation_score
        - weights["unemployment"] * unemployment_score
        + weights["growth"] * growth_score
        + weights["risk"] * risk
    )


def compute_demand_index(
    city_population: Optional[int],
    density: Optional[float],
    gdp_pc: Optional[float],
) -> float:
    pop_score = math.log(max(city_population or 1, 1))
    density_score = math.log(max(density or 1, 1))
    income_score = math.log(max(gdp_pc or 1, 1))
    return pop_score * 0.5 + density_score * 0.3 + income_score * 0.2


def get_help_answer(lang: str, question: str) -> str:
    q = question.lower()
    help_map = [
        (["ranking", "score", "top"], "Usa el bloque de ranking para ajustar pesos y ver ciudades con mayor potencial."),
        (["mapa", "map", "heatmap"], "Activa Mapa en la barra lateral; puedes activar Heatmap para densidad."),
        (["competencia", "competition", "rival"], "Selecciona categoria y ajusta el radio para medir competencia."),
        (["export", "descargar", "csv"], "En Exportar reportes puedes bajar CSV y reporte TXT."),
        (["serie", "history", "historico"], "Series historicas muestra PIB, inflacion y desempleo por ano."),
        (["alerta", "alerts"], "Alertas se activan cuando superan los umbrales del sidebar."),
        (["watchlist", "seguimiento"], "Usa Agregar/Quitar para guardar pais y ciudad."),
        (["recomend", "recommend"], "Recomendaciones sugiere categorias con baja competencia."),
        (["zona", "zone", "suburb"], "Zonas se filtran por tipo en la multiseleccion."),
        (["comparar", "compare"], "Comparar paises y ciudades esta en los bloques de comparacion."),
    ]
    for keywords, answer_es in help_map:
        if any(key in q for key in keywords):
            if lang == "en":
                return {
                    "Usa el bloque de ranking para ajustar pesos y ver ciudades con mayor potencial.": (
                        "Use the ranking block to adjust weights and see top potential cities."
                    ),
                    "Activa Mapa en la barra lateral; puedes activar Heatmap para densidad.": (
                        "Enable Map in the sidebar; toggle Heatmap for density."
                    ),
                    "Selecciona categoria y ajusta el radio para medir competencia.": (
                        "Select a category and adjust the radius to measure competition."
                    ),
                    "En Exportar reportes puedes bajar CSV y reporte TXT.": (
                        "In Export reports you can download CSV and a TXT report."
                    ),
                    "Series historicas muestra PIB, inflacion y desempleo por ano.": (
                        "Historical series shows GDP, inflation, and unemployment by year."
                    ),
                    "Alertas se activan cuando superan los umbrales del sidebar.": (
                        "Alerts trigger when thresholds in the sidebar are exceeded."
                    ),
                    "Usa Agregar/Quitar para guardar pais y ciudad.": (
                        "Use Add/Remove to save country and city."
                    ),
                    "Recomendaciones sugiere categorias con baja competencia.": (
                        "Recommendations suggest low-competition categories."
                    ),
                    "Zonas se filtran por tipo en la multiseleccion.": (
                        "Zones are filtered by type in the multiselect."
                    ),
                    "Comparar paises y ciudades esta en los bloques de comparacion.": (
                        "Country and city comparison live in the comparison blocks."
                    ),
                }.get(answer_es, t(lang, "assistant_unknown"))
            return answer_es
    return t(lang, "assistant_unknown")


def build_csv(rows: List[Dict[str, object]], fieldnames: List[str]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue()


def format_number(value: Optional[float]) -> str:
    if value is None:
        return "-"
    if isinstance(value, (int, float)) and value > 1_000_000:
        return f"{value:,.0f}"
    if isinstance(value, (int, float)):
        return f"{value:,.2f}"
    return str(value)


def risk_level_label(score: Optional[float], lang: str) -> str:
    if score is None:
        return "-"
    if score >= 1:
        return t(lang, "risk_low")
    if score >= 0:
        return t(lang, "risk_medium")
    return t(lang, "risk_high")


def main() -> None:
    st.set_page_config(page_title="Investment Radar", layout="wide")

    lang = st.sidebar.selectbox(t("en", "language"), ["es", "en"], index=0)
    if "watchlist" not in st.session_state:
        st.session_state.watchlist = []
    st.markdown(
        """
        <style>
        :root {
            --ink: #0f1b2d;
            --muted: #5b6b7b;
            --accent: #ff7a59;
            --accent-2: #1da1f2;
            --bg: #f6f3ee;
            --card: #ffffff;
            --shadow: rgba(15, 27, 45, 0.08);
        }
        html, body, [class*="css"]  {
            font-family: "Space Grotesk", "Work Sans", sans-serif;
            color: var(--ink);
        }
        .stApp {
            background: radial-gradient(circle at 15% 10%, #ffe9d6 0, transparent 40%),
                        radial-gradient(circle at 85% 5%, #d9f0ff 0, transparent 35%),
                        linear-gradient(180deg, #f6f3ee 0%, #f7f7fb 100%);
        }
        .hero {
            background: linear-gradient(120deg, #ffffff 0%, #fff4eb 55%, #f1f7ff 100%);
            padding: 24px 28px;
            border-radius: 18px;
            box-shadow: 0 12px 30px var(--shadow);
            margin-bottom: 16px;
            border: 1px solid rgba(15, 27, 45, 0.06);
        }
        .hero h1 {
            font-size: 34px;
            margin: 0 0 4px 0;
        }
        .hero p {
            margin: 0;
            color: var(--muted);
        }
        .badge {
            display: inline-block;
            background: rgba(255, 122, 89, 0.15);
            color: #a7432d;
            padding: 6px 12px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 600;
            margin-right: 8px;
        }
        .panel {
            background: var(--card);
            padding: 16px 18px;
            border-radius: 14px;
            box-shadow: 0 10px 24px var(--shadow);
            border: 1px solid rgba(15, 27, 45, 0.05);
        }
        .kpi {
            background: #fff;
            padding: 14px 16px;
            border-radius: 12px;
            border: 1px solid rgba(15, 27, 45, 0.06);
            box-shadow: 0 6px 14px var(--shadow);
        }
        .section-title {
            letter-spacing: 0.5px;
            text-transform: uppercase;
            color: var(--muted);
            font-size: 12px;
            margin-bottom: 8px;
        }
        </style>
        <script>
        document.addEventListener("wheel", function(e) {
            const target = e.target;
            if (target && (target.tagName === "INPUT" || target.tagName === "TEXTAREA")) {
                if (target.type === "number" || target.type === "range") {
                    target.blur();
                }
            }
        }, { passive: true });
        document.addEventListener("wheel", function(e) {
            const chartRoot = e.target.closest(".stDeckGlJsonChart, .vega-embed, canvas, svg");
            if (chartRoot) {
                e.stopPropagation();
            }
        }, { passive: true, capture: true });
        </script>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="hero">
            <div>
                <span class="badge">World Bank</span>
                <span class="badge">OpenStreetMap</span>
                <span class="badge">GeoNames</span>
            </div>
            <h1>{t(lang, "app_title")}</h1>
            <p>{t(lang, "app_subtitle")}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.title(t(lang, "app_title"))
    st.caption(t(lang, "app_subtitle"))

    countries = fetch_countries()
    if not countries:
        st.warning(t(lang, "no_data"))
        return
    country_label = [name for _, _, name in countries]
    selected_name = st.sidebar.selectbox(t(lang, "country"), country_label)
    selected_iso2, selected_iso3, _ = next(
        (iso2, iso3, name) for iso2, iso3, name in countries if name == selected_name
    )
    with st.sidebar.expander(t(lang, "ranking_block"), expanded=False):
        weight_population = st.slider(t(lang, "weight_population"), 0.0, 3.0, 1.2, 0.1)
        weight_gdp_pc = st.slider(t(lang, "weight_gdp_pc"), 0.0, 3.0, 1.0, 0.1)
        weight_inflation = st.slider(t(lang, "weight_inflation"), 0.0, 3.0, 1.0, 0.1)
        weight_unemployment = st.slider(t(lang, "weight_unemployment"), 0.0, 3.0, 1.0, 0.1)
        weight_growth = st.slider(t(lang, "weight_growth"), 0.0, 3.0, 0.8, 0.1)
        weight_risk = st.slider(t(lang, "weight_risk"), 0.0, 3.0, 0.6, 0.1)
    with st.sidebar.expander(t(lang, "alerts_block"), expanded=False):
        alert_inflation = st.slider(t(lang, "alert_inflation"), 0.0, 50.0, 10.0, 0.5)
        alert_unemployment = st.slider(t(lang, "alert_unemployment"), 0.0, 50.0, 12.0, 0.5)
        alert_risk = st.slider(t(lang, "alert_risk"), -2.5, 2.5, -0.5, 0.1)
    max_points = st.sidebar.slider(t(lang, "max_points"), 50, 300, 150, 50)
    radius_km = st.sidebar.slider(t(lang, "radius_km"), 1, 30, 10, 1)
    show_map = st.sidebar.checkbox(t(lang, "map_block"), value=False)
    show_heatmap = st.sidebar.checkbox(t(lang, "heatmap"), value=False)
    show_best = st.sidebar.checkbox(t(lang, "best_categories"), value=False)

    gdp, gdp_year = fetch_indicator(selected_iso3, "NY.GDP.MKTP.CD")
    gdp_pc, gdp_pc_year = fetch_indicator(selected_iso3, "NY.GDP.PCAP.CD")
    pop, pop_year = fetch_indicator(selected_iso3, "SP.POP.TOTL")
    density, density_year = fetch_indicator(selected_iso3, "EN.POP.DNST")
    inflation, inflation_year = fetch_indicator(selected_iso3, "FP.CPI.TOTL.ZG")
    unemployment, unemployment_year = fetch_indicator(selected_iso3, "SL.UEM.TOTL.ZS")
    growth, growth_year = fetch_indicator(selected_iso3, "NY.GDP.MKTP.KD.ZG")
    tax_revenue, tax_year = fetch_indicator(selected_iso3, "GC.TAX.TOTL.GD.ZS")
    current_account, ca_year = fetch_indicator(selected_iso3, "BN.CAB.XOKA.GD.ZS")
    median_age, median_age_year = fetch_indicator(selected_iso3, "SP.POP.MEDN")
    urbanization, urban_year = fetch_indicator(selected_iso3, "SP.URB.TOTL.IN.ZS")
    labor_force, labor_year = fetch_indicator(selected_iso3, "SL.TLF.CACT.ZS")
    risk_score, risk_year = fetch_wgi_risk(selected_iso3)

    st.subheader(t(lang, "country_metrics"))
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(t(lang, "gdp"), format_number(gdp))
    col2.metric(t(lang, "gdp_pc"), format_number(gdp_pc))
    col3.metric(t(lang, "population"), format_number(pop))
    col4.metric(t(lang, "density"), format_number(density))
    st.caption(
        f"{t(lang, 'updated')}: "
        f"{gdp_year or '-'}, {gdp_pc_year or '-'}, {pop_year or '-'}, {density_year or '-'}"
    )

    st.subheader(t(lang, "econ_block"))
    econ1, econ2, econ3, econ4 = st.columns(4)
    econ1.metric(t(lang, "inflation"), format_number(inflation))
    econ2.metric(t(lang, "unemployment"), format_number(unemployment))
    econ3.metric(t(lang, "growth"), format_number(growth))
    econ4.metric(t(lang, "tax_revenue"), format_number(tax_revenue))
    econ5, econ6, econ7 = st.columns(3)
    econ5.metric(t(lang, "current_account"), format_number(current_account))
    econ6.metric(t(lang, "urbanization"), format_number(urbanization))
    econ7.metric(t(lang, "labor_force"), format_number(labor_force))
    st.caption(
        f"{t(lang, 'updated')}: "
        f"{inflation_year or '-'}, {unemployment_year or '-'}, {growth_year or '-'}, "
        f"{tax_year or '-'}, {ca_year or '-'}, {urban_year or '-'}, {labor_year or '-'}"
    )

    st.subheader(t(lang, "risk_block"))
    risk1, risk2, risk3 = st.columns(3)
    risk1.metric(t(lang, "risk_score"), format_number(risk_score))
    risk2.metric(t(lang, "risk_level"), risk_level_label(risk_score, lang))
    risk3.metric(t(lang, "median_age"), format_number(median_age))
    st.caption(f"{t(lang, 'updated')}: {risk_year or '-'}, {median_age_year or '-'}")

    st.subheader(t(lang, "alerts_block"))
    if inflation is not None and inflation > alert_inflation:
        st.warning(f"{t(lang, 'inflation')}: {format_number(inflation)}")
    if unemployment is not None and unemployment > alert_unemployment:
        st.warning(f"{t(lang, 'unemployment')}: {format_number(unemployment)}")
    if risk_score is not None and risk_score < alert_risk:
        st.warning(f"{t(lang, 'risk_score')}: {format_number(risk_score)}")

    st.subheader(t(lang, "summary_block"))
    indicator_values = [
        gdp,
        gdp_pc,
        pop,
        density,
        inflation,
        unemployment,
        growth,
        tax_revenue,
        current_account,
        median_age,
        urbanization,
        labor_force,
        risk_score,
    ]
    available = sum(1 for value in indicator_values if value is not None)
    data_quality = available / len(indicator_values) * 100
    summary1, summary2, summary3 = st.columns(3)
    demand_index = compute_demand_index(None, density, gdp_pc)
    composite_score = compute_city_score(
        None,
        gdp_pc,
        inflation,
        unemployment,
        growth,
        risk_score,
        {
            "population": weight_population,
            "gdp_pc": weight_gdp_pc,
            "inflation": weight_inflation,
            "unemployment": weight_unemployment,
            "growth": weight_growth,
            "risk": weight_risk,
        },
    )
    summary1.metric(t(lang, "composite_score"), format_number(composite_score))
    summary2.metric(t(lang, "demand_index"), format_number(demand_index))
    summary3.metric(t(lang, "data_quality"), f"{data_quality:.0f}%")

    cities = fetch_worldcities(selected_iso2)
    if not cities:
        st.warning(t(lang, "no_data"))
        return
    years = [
        gdp_year,
        gdp_pc_year,
        pop_year,
        density_year,
        inflation_year,
        unemployment_year,
        growth_year,
        tax_year,
        ca_year,
        median_age_year,
        urban_year,
        labor_year,
        risk_year,
    ]
    years = [int(y) for y in years if y]
    latest_year = max(years) if years else None

    st.markdown(f"<div class='section-title'>{t(lang, 'data_notes')}</div>", unsafe_allow_html=True)
    snap1, snap2, snap3 = st.columns(3)
    snap1.metric(t(lang, "latest_year_label"), latest_year or "-")
    snap2.metric(t(lang, "cities_indexed_label"), format_number(len(cities)))
    snap3.metric(t(lang, "top_city_pop_label"), format_number(max((c.population or 0) for c in cities)))
    top_cities = sorted(
        [c for c in cities if c.population],
        key=lambda x: x.population or 0,
        reverse=True,
    )[:10]

    st.subheader(t(lang, "top_cities"))
    top_cols = st.columns(3)
    for idx, city in enumerate(top_cities[:3]):
        score = (city.population or 0) * (gdp_pc or 0) / 1_000_000 if gdp_pc else 0
        top_cols[idx].markdown(
            f"**{city.name}**  \n"
            f"Pop: {format_number(city.population)}  \n"
            f"Score: {format_number(score)}"
        )

    st.subheader(t(lang, "ranking_block"))
    st.caption(t(lang, "ranking_note"))
    weights = {
        "population": weight_population,
        "gdp_pc": weight_gdp_pc,
        "inflation": weight_inflation,
        "unemployment": weight_unemployment,
        "growth": weight_growth,
        "risk": weight_risk,
    }
    ranked = []
    for city in top_cities:
        ranked.append(
            (
                city.name,
                compute_city_score(
                    city.population,
                    gdp_pc,
                    inflation,
                    unemployment,
                    growth,
                    risk_score,
                    weights,
                ),
            )
        )
    ranked = sorted(ranked, key=lambda x: x[1], reverse=True)[:10]
    st.table({"City": [c for c, _ in ranked], "Score": [format_number(s) for _, s in ranked]})

    st.subheader(t(lang, "compare_cities"))
    compare_city_names = st.multiselect(
        t(lang, "compare_cities"),
        [city.name for city in top_cities],
        default=[city.name for city in top_cities[:3]],
    )
    if compare_city_names:
        compare_rows = []
        for city in top_cities:
            if city.name not in compare_city_names:
                continue
            compare_rows.append(
                {
                    "city": city.name,
                    "population": city.population or 0,
                    "score": compute_city_score(
                        city.population,
                        gdp_pc,
                        inflation,
                        unemployment,
                        growth,
                        risk_score,
                        weights,
                    ),
                }
            )
        df_compare = pd.DataFrame(compare_rows)
        df_long = df_compare.melt(id_vars=["city"], value_vars=["population", "score"], var_name="metric", value_name="value")
        chart = (
            alt.Chart(df_long)
            .mark_bar()
            .encode(
                x=alt.X("city:N", sort=None),
                y=alt.Y("value:Q"),
                color=alt.Color("metric:N"),
                tooltip=["city", "metric", "value"],
            )
        )
        st.altair_chart(chart, use_container_width=True)

    city_names = []
    city_by_name = {}
    seen = set()
    for city in top_cities + cities:
        if city.name and city.name not in seen:
            seen.add(city.name)
            city_names.append(city.name)
            city_by_name[city.name] = city
    city_choice = st.selectbox(t(lang, "city"), city_names)
    st.caption(t(lang, "investment_hint"))

    watch_col1, watch_col2 = st.columns(2)
    if watch_col1.button(t(lang, "add_watchlist")):
        st.session_state.watchlist.append(
            {"country": selected_name, "city": city_choice, "added": datetime.utcnow().isoformat()}
        )
    if watch_col2.button(t(lang, "remove_watchlist")):
        st.session_state.watchlist = [
            item
            for item in st.session_state.watchlist
            if not (item["country"] == selected_name and item["city"] == city_choice)
        ]

    st.subheader(t(lang, "visual_block"))
    st.caption(t(lang, "visual_note"))
    flag_url = f"https://flagcdn.com/w160/{selected_iso2.lower()}.png"
    skyline_query = city_choice.replace(" ", "%20")
    skyline_url = f"https://source.unsplash.com/featured/900x600/?{skyline_query},skyline,finance"
    visual1, visual2 = st.columns(2)
    visual1.image(flag_url, caption=selected_name, use_container_width=True)
    visual2.image(skyline_url, caption=city_choice, use_container_width=True)

    selected_city = city_by_name.get(city_choice)
    city_cost = fetch_city_cost_m2(city_choice, selected_name)
    city_rent = fetch_city_rent(city_choice, selected_name)
    potential_clients = None
    if selected_city and selected_city.population:
        if labor_force is not None:
            participation = labor_force / 100
            employment_rate = 1 - (unemployment or 0) / 100
            potential_clients = selected_city.population * participation * employment_rate
        else:
            potential_clients = selected_city.population

    city_demand = compute_demand_index(
        selected_city.population if selected_city else None, density, gdp_pc
    )
    st.subheader(t(lang, "housing_block"))
    house1, house2, house3, house4 = st.columns(4)
    house1.metric(t(lang, "cost_m2"), format_number(city_cost))
    house2.metric(t(lang, "rent_month"), format_number(city_rent))
    house3.metric(t(lang, "potential_clients"), format_number(potential_clients))
    house4.metric(t(lang, "demand_index"), format_number(city_demand))

    st.subheader(t(lang, "business_category"))
    search_term = st.text_input(t(lang, "search_business"))
    categories = [c for c in BUSINESS_CATEGORIES if search_term.lower() in c.lower()] if search_term else BUSINESS_CATEGORIES
    category_choice = st.selectbox(t(lang, "business_category"), categories)

    zone_type_options = ["neighbourhood", "suburb", "quarter", "district"]
    zone_types = st.multiselect(t(lang, "zone_types"), zone_type_options, default=zone_type_options)

    zones = fetch_city_zones(
        city_choice,
        selected_iso2,
        selected_city.lat if selected_city else None,
        selected_city.lon if selected_city else None,
    )
    st.subheader(t(lang, "city_zones"))
    if zones:
        st.write(", ".join(zones[:50]))
    else:
        st.info(t(lang, "zones_empty"))

    malls_offices = fetch_malls_offices(
        city_choice,
        selected_iso2,
        selected_city.lat if selected_city else None,
        selected_city.lon if selected_city else None,
    )
    st.subheader(t(lang, "malls_offices"))
    if malls_offices:
        st.write(", ".join(malls_offices[:50]))
    else:
        st.info(t(lang, "pois_empty"))

    st.subheader(t(lang, "competition"))
    competitors = fetch_competitors(
        city_choice,
        selected_iso2,
        category_choice,
        selected_city.lat if selected_city else None,
        selected_city.lon if selected_city else None,
        radius_km * 1000,
    )
    if competitors:
        st.metric(t(lang, "competition_count"), competitors)
    else:
        st.info(t(lang, "category_empty"))

    st.subheader(t(lang, "recommendations"))
    st.caption(t(lang, "recommendation_note"))
    rec_candidates = list(BUSINESS_OSM_MAP.keys())[:6]
    rec_rows = []
    for category in rec_candidates:
        count = fetch_competitors(
            city_choice,
            selected_iso2,
            category,
            selected_city.lat if selected_city else None,
            selected_city.lon if selected_city else None,
            radius_km * 1000,
        )
        score = city_demand / max(count + 1, 1)
        rec_rows.append({"category": category, "score": score, "competitors": count})
    rec_rows = sorted(rec_rows, key=lambda x: x["score"], reverse=True)[:3]
    st.table(
        {
            t(lang, "table_category"): [row["category"] for row in rec_rows],
            t(lang, "table_competitors"): [row["competitors"] for row in rec_rows],
        }
    )

    if show_map:
        st.subheader(t(lang, "map_block"))
        if selected_city and selected_city.lat is not None and selected_city.lon is not None:
            zone_points = fetch_zone_points(
                city_choice,
                selected_iso2,
                selected_city.lat,
                selected_city.lon,
                zone_types,
                max_points,
                radius_km * 1000,
            )
            competitor_points = fetch_competitor_points(
                city_choice,
                selected_iso2,
                category_choice,
                selected_city.lat,
                selected_city.lon,
                max_points,
                radius_km * 1000,
            )
            if zone_points or competitor_points:
                layers = []
                if zone_points:
                    layers.append(
                        pdk.Layer(
                            "ScatterplotLayer",
                            data=zone_points,
                            get_position="[lon, lat]",
                            get_radius=200,
                            get_fill_color=[60, 120, 200, 160],
                            pickable=True,
                        )
                    )
                if competitor_points:
                    layers.append(
                        pdk.Layer(
                            "ScatterplotLayer",
                            data=competitor_points,
                            get_position="[lon, lat]",
                            get_radius=150,
                            get_fill_color=[220, 60, 60, 160],
                            pickable=True,
                        )
                    )
                    if show_heatmap:
                        layers.append(
                            pdk.Layer(
                                "HeatmapLayer",
                                data=competitor_points,
                                get_position="[lon, lat]",
                                radius_pixels=60,
                            )
                        )
                view = pdk.ViewState(
                    latitude=selected_city.lat,
                    longitude=selected_city.lon,
                    zoom=11,
                    pitch=0,
                )
                st.pydeck_chart(
                    pdk.Deck(
                        layers=layers,
                        initial_view_state=view,
                        tooltip={"text": "{name}"},
                        controller={"scrollZoom": False},
                    )
                )
            else:
                st.info(t(lang, "map_empty"))
        else:
            st.info(t(lang, "map_empty"))

    if show_best:
        st.subheader(t(lang, "best_categories"))
        st.caption(t(lang, "best_hint"))
        best_limit = st.slider(t(lang, "top_n"), 3, 8, 5, 1)
        eval_count = st.slider(t(lang, "categories_to_eval"), 5, min(20, len(BUSINESS_OSM_MAP)), 8, 1)
        best_candidates = list(BUSINESS_OSM_MAP.keys())[:eval_count]
        progress = st.progress(0)
        best_rows = []
        for idx, category in enumerate(best_candidates, start=1):
            count = fetch_competitors(
                city_choice,
                selected_iso2,
                category,
                selected_city.lat if selected_city else None,
                selected_city.lon if selected_city else None,
                radius_km * 1000,
            )
            best_rows.append({"category": category, "competitors": count})
            progress.progress(idx / len(best_candidates))
        progress.empty()
        best_rows = sorted(best_rows, key=lambda x: x["competitors"])[:best_limit]
        st.table(
            {
                t(lang, "table_category"): [row["category"] for row in best_rows],
                t(lang, "table_competitors"): [row["competitors"] for row in best_rows],
            }
        )

    st.subheader(t(lang, "compare_block"))
    compare_names = st.multiselect(t(lang, "country"), country_label, default=[selected_name])
    compare_rows = []
    for name in compare_names:
        iso2, iso3, _ = next((i2, i3, n) for i2, i3, n in countries if n == name)
        snapshot = fetch_country_snapshot(iso3)
        snapshot["country"] = name
        compare_rows.append(snapshot)
    if compare_rows:
        st.dataframe(compare_rows, use_container_width=True)

    st.subheader(t(lang, "series_block"))
    st.caption(t(lang, "series_hint"))
    series_gdp = fetch_indicator_series(selected_iso3, "NY.GDP.MKTP.CD", 12)
    series_inflation = fetch_indicator_series(selected_iso3, "FP.CPI.TOTL.ZG", 12)
    series_unemployment = fetch_indicator_series(selected_iso3, "SL.UEM.TOTL.ZS", 12)
    if series_gdp:
        df_series = pd.DataFrame(
            {
                "year": [y for y, _ in series_gdp],
                "gdp": [v for _, v in series_gdp],
            }
        )
        chart = alt.Chart(df_series).mark_line().encode(x="year:O", y="gdp:Q", tooltip=["year", "gdp"])
        st.altair_chart(chart, use_container_width=True)
    if series_inflation:
        df_inflation = pd.DataFrame(
            {
                "year": [y for y, _ in series_inflation],
                "inflation": [v for _, v in series_inflation],
            }
        )
        chart = alt.Chart(df_inflation).mark_line(color="#ff7a59").encode(
            x="year:O", y="inflation:Q", tooltip=["year", "inflation"]
        )
        st.altair_chart(chart, use_container_width=True)
    if series_unemployment:
        df_unemployment = pd.DataFrame(
            {
                "year": [y for y, _ in series_unemployment],
                "unemployment": [v for _, v in series_unemployment],
            }
        )
        chart = alt.Chart(df_unemployment).mark_line(color="#1da1f2").encode(
            x="year:O", y="unemployment:Q", tooltip=["year", "unemployment"]
        )
        st.altair_chart(chart, use_container_width=True)

    st.subheader(t(lang, "exports_block"))
    country_rows = [
        {
            "country": selected_name,
            "gdp": gdp,
            "gdp_pc": gdp_pc,
            "population": pop,
            "density": density,
            "inflation": inflation,
            "unemployment": unemployment,
            "growth": growth,
            "tax_revenue": tax_revenue,
            "current_account": current_account,
            "median_age": median_age,
            "urbanization": urbanization,
            "labor_force": labor_force,
            "risk_score": risk_score,
        }
    ]
    country_csv = build_csv(country_rows, list(country_rows[0].keys()))
    st.download_button(
        t(lang, "download_country"),
        data=country_csv,
        file_name=f"country_{selected_iso3}.csv",
        mime="text/csv",
    )

    city_rows = []
    for city_name, score in ranked:
        city_rows.append({"city": city_name, "score": score})
    cities_csv = build_csv(city_rows, ["city", "score"])
    st.download_button(
        t(lang, "download_cities"),
        data=cities_csv,
        file_name=f"cities_{selected_iso3}.csv",
        mime="text/csv",
    )

    report_text = "\n".join(
        [
            f"Report generated: {datetime.utcnow().isoformat()}Z",
            f"Country: {selected_name}",
            f"GDP: {gdp}",
            f"GDP per capita: {gdp_pc}",
            f"Population: {pop}",
            f"Inflation: {inflation}",
            f"Unemployment: {unemployment}",
            f"Growth: {growth}",
            f"Risk score: {risk_score}",
            f"City: {city_choice}",
            f"Cost per m2: {city_cost}",
            f"Potential clients: {potential_clients}",
        ]
    )
    st.download_button(
        t(lang, "download_report"),
        data=report_text,
        file_name=f"report_{selected_iso3}.txt",
        mime="text/plain",
    )

    st.subheader(t(lang, "watchlist"))
    if st.session_state.watchlist:
        st.dataframe(st.session_state.watchlist, use_container_width=True)
        watchlist_csv = build_csv(st.session_state.watchlist, ["country", "city", "added"])
        st.download_button(
            t(lang, "export_watchlist"),
            data=watchlist_csv,
            file_name="watchlist.csv",
            mime="text/csv",
        )
    else:
        st.info(t(lang, "watchlist_empty"))

    st.subheader(t(lang, "assistant_block"))
    st.caption(t(lang, "assistant_intro"))
    if "assistant_messages" not in st.session_state:
        st.session_state.assistant_messages = []
    for msg in st.session_state.assistant_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    user_question = st.chat_input(t(lang, "assistant_placeholder"))
    if user_question:
        st.session_state.assistant_messages.append({"role": "user", "content": user_question})
        answer = get_help_answer(lang, user_question)
        st.session_state.assistant_messages.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.write(answer)

    st.subheader(t(lang, "data_notes"))
    st.write(t(lang, "sources"))
    st.write(t(lang, "cost_note"))
    st.write(t(lang, "rent_note"))
    st.write(t(lang, "clients_note"))


if __name__ == "__main__":
    main()
