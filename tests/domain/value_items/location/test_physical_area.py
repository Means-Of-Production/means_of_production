import pytest
from domain.value_items.location.physical_area import PhysicalArea
from domain.value_items.location.physical_location import PhysicalLocation
from domain.value_items.location.distance import Distance
from domain.value_items.location.virtual_location import VirtualLocation
from domain.value_items.url import URL


class TestPhysicalAreaContains:
    """Test suite for the PhysicalArea.contains method."""

    def test_contains_physical_location_inside(self):
        """Test that a PhysicalArea contains a PhysicalLocation that is inside its radius."""
        # Create a center point for our area
        center = PhysicalLocation(
            latitude=40.7128,
            longitude=-74.0060,
            street_address="123 Broadway",
            city="New York",
            state="NY",
            zip_code="10001",
            country="USA",
        )

        # Create an area with a 10km radius
        area = PhysicalArea(center_point=center, radius=Distance(kilometers=10.0))

        # Create a location 5km away from the center (should be inside)
        # This is approximately 0.045 degrees latitude north of the center
        inside_location = PhysicalLocation(
            latitude=40.7533,  # ~5km north of center
            longitude=-74.0060,
            street_address="456 W 57th St",
            city="New York",
            state="NY",
            zip_code="10019",
            country="USA",
        )

        # Assert that the location is inside the area
        assert area.contains(inside_location) is True

    def test_contains_physical_location_on_boundary(self):
        """Test that a PhysicalArea contains a PhysicalLocation that is exactly on its boundary."""
        # Create a center point for our area
        center = PhysicalLocation(
            latitude=40.7128,
            longitude=-74.0060,
            street_address="123 Broadway",
            city="New York",
            state="NY",
            zip_code="10001",
            country="USA",
        )

        # Create an area with a 10km radius
        area = PhysicalArea(center_point=center, radius=Distance(kilometers=10.0))

        # Create a location exactly 10km away from the center (should be on boundary)
        # This is approximately 0.09 degrees latitude north of the center
        boundary_location = PhysicalLocation(
            latitude=40.8028,  # ~10km north of center
            longitude=-74.0060,
            street_address="789 W 181st St",
            city="New York",
            state="NY",
            zip_code="10033",
            country="USA",
        )

        # The contains method uses < operator, so a point exactly on the boundary
        # should return False
        assert area.contains(boundary_location) is False

    def test_contains_physical_location_outside(self):
        """Test that a PhysicalArea does not contain a PhysicalLocation that is outside its radius."""
        # Create a center point for our area
        center = PhysicalLocation(
            latitude=40.7128,
            longitude=-74.0060,
            street_address="123 Broadway",
            city="New York",
            state="NY",
            zip_code="10001",
            country="USA",
        )

        # Create an area with a 10km radius
        area = PhysicalArea(center_point=center, radius=Distance(kilometers=10.0))

        # Create a location 15km away from the center (should be outside)
        # This is approximately 0.135 degrees latitude north of the center
        outside_location = PhysicalLocation(
            latitude=40.8478,  # ~15km north of center
            longitude=-74.0060,
            street_address="123 Main St",
            city="Fort Lee",
            state="NJ",
            zip_code="07024",
            country="USA",
        )

        # Assert that the location is outside the area
        assert area.contains(outside_location) is False

    def test_contains_physical_area_inside(self):
        """Test that a PhysicalArea contains another PhysicalArea that is completely inside it."""
        # Create a center point for our area
        center = PhysicalLocation(
            latitude=40.7128,
            longitude=-74.0060,
            street_address="123 Broadway",
            city="New York",
            state="NY",
            zip_code="10001",
            country="USA",
        )

        # Create an area with a 20km radius
        large_area = PhysicalArea(center_point=center, radius=Distance(kilometers=20.0))

        # Create another center point 5km away
        other_center = PhysicalLocation(
            latitude=40.7533,  # ~5km north of center
            longitude=-74.0060,
            street_address="456 W 57th St",
            city="New York",
            state="NY",
            zip_code="10019",
            country="USA",
        )

        # Create a smaller area with a 5km radius
        small_area = PhysicalArea(
            center_point=other_center, radius=Distance(kilometers=5.0)
        )

        # Assert that the small area is inside the large area
        assert large_area.contains(small_area) is True

    def test_contains_physical_area_outside(self):
        """Test that a PhysicalArea does not contain another PhysicalArea that is outside it."""
        # Create a center point for our area
        center = PhysicalLocation(
            latitude=40.7128,
            longitude=-74.0060,
            street_address="123 Broadway",
            city="New York",
            state="NY",
            zip_code="10001",
            country="USA",
        )

        # Create an area with a 10km radius
        area = PhysicalArea(center_point=center, radius=Distance(kilometers=10.0))

        # Create another center point 25km away
        other_center = PhysicalLocation(
            latitude=40.9378,  # ~25km north of center
            longitude=-74.0060,
            street_address="123 Main St",
            city="Englewood Cliffs",
            state="NJ",
            zip_code="07632",
            country="USA",
        )

        # Create another area with a 10km radius
        other_area = PhysicalArea(
            center_point=other_center, radius=Distance(kilometers=10.0)
        )

        # Assert that the other area is outside the area
        assert area.contains(other_area) is False

    def test_contains_physical_area_touching_boundary(self):
        """Test that a PhysicalArea does not contain another PhysicalArea that touches its boundary."""
        # Create a center point for our area
        center = PhysicalLocation(
            latitude=40.7128,
            longitude=-74.0060,
            street_address="123 Broadway",
            city="New York",
            state="NY",
            zip_code="10001",
            country="USA",
        )

        # Create an area with a 15km radius
        area = PhysicalArea(center_point=center, radius=Distance(kilometers=15.0))

        # Create another center point 10km away
        other_center = PhysicalLocation(
            latitude=40.8028,  # ~10km north of center
            longitude=-74.0060,
            street_address="789 W 181st St",
            city="New York",
            state="NY",
            zip_code="10033",
            country="USA",
        )

        # Create another area with a 5km radius
        # This should touch the boundary of the first area (10km + 5km = 15km)
        other_area = PhysicalArea(
            center_point=other_center, radius=Distance(kilometers=5.0)
        )

        # The contains method uses < operator, so an area touching the boundary
        # should return False
        assert area.contains(other_area) is False

    def test_contains_invalid_type(self):
        """Test that the contains method raises a ValueError for invalid types."""
        # Create a center point for our area
        center = PhysicalLocation(
            latitude=40.7128,
            longitude=-74.0060,
            street_address="123 Broadway",
            city="New York",
            state="NY",
            zip_code="10001",
            country="USA",
        )

        # Create an area with a 10km radius
        area = PhysicalArea(center_point=center, radius=Distance(kilometers=10.0))

        # Create a virtual location (not supported by contains)
        virtual_location = VirtualLocation(url=URL.parse("https://example.com"))

        # Assert that the method raises a ValueError
        with pytest.raises(ValueError):
            area.contains(virtual_location)
