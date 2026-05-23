import requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
_cache: dict[str, tuple[float, float] | None] = {}


def geocode(address: str) -> tuple[float, float] | None:
    """주소 → (lat, lng). 실패 시 None."""
    if address in _cache:
        return _cache[address]

    try:
        resp = requests.get(
            NOMINATIM_URL,
            params={"q": address, "format": "json", "limit": 1, "countrycodes": "kr"},
            headers={"User-Agent": "100-0-lab/1.0"},
            timeout=5,
        )
        results = resp.json()
        if results:
            lat = float(results[0]["lat"])
            lng = float(results[0]["lon"])
            _cache[address] = (lat, lng)
            return (lat, lng)
    except Exception as e:
        print(f"[geocoding] error for '{address}': {e}")

    _cache[address] = None
    return None
