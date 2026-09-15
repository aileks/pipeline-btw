import pytest
from pydantic import ValidationError

from pipeline_btw.load.postgres import Brewery


def brewery_row(**overrides):
    row = {
        "id": "b54b7e3d-6d1a-4f65-9c8d-0f5a6b7c8d9e",
        "brewery_type": "micro",
        "name": "Allagash Brewing Company",
        "address_1": "50 Industrial Way",
        "address_2": "",
        "address_3": "",
        "city": "Portland",
        "state_province": "Maine",
        "postal_code": "04101",
        "country": "United States",
        "longitude": "-70.2589",
        "latitude": "43.6591",
        "phone": "(207) 878-5300",
        "website_url": "https://www.allagash.com/beers",
    }
    row.update(overrides)
    return row


def test_valid_row_parses_with_normalized_values():
    """A valid row parses with coordinates as floats, phone as bare digits, and url as str."""
    dumped = Brewery(**brewery_row()).model_dump()

    assert dumped["longitude"] == -70.2589
    assert dumped["latitude"] == 43.6591
    assert dumped["phone"] == "2078785300"
    assert dumped["website_url"] == "https://www.allagash.com/beers"
    assert isinstance(dumped["website_url"], str)


def test_empty_strings_become_none():
    """Empty string values are converted to None before field validation."""
    brewery = Brewery(**brewery_row())

    assert brewery.address_2 is None
    assert brewery.address_3 is None


def test_string_null_becomes_none():
    """The literal string 'null' is converted to None."""
    brewery = Brewery(**brewery_row(longitude="null", website_url="null"))

    assert brewery.longitude is None
    assert brewery.website_url is None


def test_phone_without_digits_becomes_none():
    """A phone value that strips down to no digits becomes None."""
    brewery = Brewery(**brewery_row(phone="not available"))

    assert brewery.phone is None


def test_invalid_brewery_type_is_rejected():
    """An unknown brewery_type raises ValidationError."""
    with pytest.raises(ValidationError):
        Brewery(**brewery_row(brewery_type="brewery"))


def test_invalid_id_is_rejected():
    """A non-UUID id raises ValidationError."""
    with pytest.raises(ValidationError):
        Brewery(**brewery_row(id="not-a-uuid"))
