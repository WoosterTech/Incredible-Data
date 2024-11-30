from geopy import geocoders
from geopy.geocoders import Nominatim
from geopy.location import Location

geocoders.options.default_user_agent = "incredible-data-fuel"


class GeoLocate:
    @staticmethod
    def from_lat_long(latitude: float, longitude: float) -> Location:
        geolocator = Nominatim()
        return geolocator.reverse(f"{latitude}, {longitude}")

    @staticmethod
    def from_address(address: str) -> Location:
        geolocator = Nominatim()
        return geolocator.geocode(address)


if __name__ == "__main__":
    from rich import print  # noqa: A004
    from rich.pretty import pprint

    latitude = 38.8977
    longitude = -77.0365

    print(f"(Latitude: {latitude}, Longitude: {longitude})")

    lat_lon_location = GeoLocate.from_lat_long(latitude, longitude)

    pprint(f"Address: {lat_lon_location.address}")

    address = "7711 Thetis Dr, Pasco, WA 99301"

    address_location = GeoLocate.from_address(address)

    pprint(
        f"Latitude: {address_location.latitude}, "
        f"Longitude: {address_location.longitude}"
    )
