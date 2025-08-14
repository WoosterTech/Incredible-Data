# pyright: reportMissingTypeStubs=false

import pytest
from geopy import geocoders
from geopy.location import Location

from incredible_data.fuel.geolocate import GeoLocate

geocoders.options.default_user_agent = "incredible-data-fuel"


def test_trivial():
    assert True


# Create your tests here.
@pytest.mark.skip("not being used")
def test_geolocate_lat_long(mocker):  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType]
    mock_reverse = mocker.patch("geopy.geocoders.Nominatim.reverse")  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    mock_location = Location(
        "221B Baker Street, London", (51.5237, -0.1585), {"place_id": 12345}
    )
    mock_reverse.return_value = mock_location

    address = GeoLocate.from_lat_long(38.8977, -77.0365)

    mock_reverse.assert_called_once_with("38.8977, -77.0365")  # pyright: ignore[reportUnknownMemberType]

    assert address == "221B Baker Street, London"
