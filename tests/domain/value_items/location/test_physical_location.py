import pytest

from domain.value_items.location.physical_location import PhysicalLocation


def test_distance_calculation():
    """Test successful distance calculation between two locations with coordinates."""
    # Create two locations with coordinates
    location1 = PhysicalLocation(
        latitude=40.7128,
        longitude=-74.0060,
        street_address="123 Broadway",
        city="New York",
        state="NY",
        zip_code="10001",
        country="USA",
    )

    location2 = PhysicalLocation(
        latitude=34.0522,
        longitude=-118.2437,
        street_address="456 Hollywood Blvd",
        city="Los Angeles",
        state="CA",
        zip_code="90001",
        country="USA",
    )

    # Calculate distance
    distance = location1.distance(location2)

    # The distance between New York and Los Angeles is approximately 3935 km
    assert distance.kilometers == pytest.approx(3935.75, abs=1e-2)
    assert distance.miles == pytest.approx(2445.57, abs=1e-2)


def test_distance_with_other_location_missing_coordinates():
    """Test that ValueError is raised when the other location doesn't have coordinates."""
    # Create a location with coordinates
    location1 = PhysicalLocation(
        latitude=40.7128,
        longitude=-74.0060,
        street_address="123 Broadway",
        city="New York",
        state="NY",
        zip_code="10001",
        country="USA",
    )

    # Create a location without coordinates
    location_without_coordinates = PhysicalLocation(
        street_address="789 Main St",
        city="Chicago",
        state="IL",
        zip_code="60601",
        country="USA",
    )

    # Test that ValueError is raised when the other location doesn't have coordinates
    with pytest.raises(
        ValueError, match="The other location does not have latitude and longitude set"
    ):
        location1.distance(location_without_coordinates)


def test_distance_with_this_location_missing_coordinates():
    """Test that ValueError is raised when this location doesn't have coordinates."""
    # Create a location with coordinates
    location_with_coordinates = PhysicalLocation(
        latitude=40.7128,
        longitude=-74.0060,
        street_address="123 Broadway",
        city="New York",
        state="NY",
        zip_code="10001",
        country="USA",
    )

    # Create a location without coordinates
    location_without_coordinates = PhysicalLocation(
        street_address="789 Main St",
        city="Chicago",
        state="IL",
        zip_code="60601",
        country="USA",
    )

    # Test that ValueError is raised when this location doesn't have coordinates
    with pytest.raises(
        ValueError, match="This location does not have latitude and longitude set"
    ):
        location_without_coordinates.distance(location_with_coordinates)
