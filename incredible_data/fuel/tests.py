from geopy import geocoders
from geopy.location import Location

from incredible_data.fuel.geolocate import GeoLocate

geocoders.options.default_user_agent = "incredible-data-fuel"


def test_trivial():
    assert True


# Create your tests here.
def test_geolocate_lat_long(mocker):
    mock_reverse = mocker.patch("geopy.geocoders.Nominatim.reverse")
    mock_location = Location(
        "221B Baker Street, London", (51.5237, -0.1585), {"place_id": 12345}
    )
    mock_reverse.return_value = mock_location

    address = GeoLocate.from_lat_long(38.8977, -77.0365)

    mock_reverse.assert_called_once_with("38.8977, -77.0365")

    assert address == "221B Baker Street, London"
