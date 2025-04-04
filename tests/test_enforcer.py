"""
Tests for the type_enforcer module.

This test suite verifies the functionality of the TypeEnforcer utility,
which provides runtime type validation with detailed error reporting.
"""

from dataclasses import dataclass
from enum import Enum
from typing import (
    Any,
    Literal,
    TypedDict,
)

import pytest

from type_enforcer import TypeEnforcer, ValidationError, enforce


# Define test types
class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class UserInfo(TypedDict):
    name: str
    age: int
    role: UserRole | None


class PartialUserInfo(TypedDict, total=False):
    name: str
    age: int
    role: UserRole | None


@dataclass
class Point:
    x: int
    y: int

    def distance_from_origin(self) -> float:
        return (self.x**2 + self.y**2) ** 0.5


@dataclass
class Shape:
    points: list[Point]
    name: str
    properties: dict[str, Any]


class TestBasicValidation:
    """Test basic validation for primitive types."""

    def test_valid_primitives(self):
        """Test validation of valid primitive values."""
        assert enforce(42, int) == 42
        assert enforce("hello", str) == "hello"
        assert enforce(3.14, float) == 3.14
        assert enforce(True, bool) is True
        assert enforce(None, type(None)) is None

    def test_invalid_primitives(self):
        """Test validation of invalid primitive values."""
        with pytest.raises(ValidationError) as exc_info:
            enforce("not an int", int)
        assert "Expected int, got str" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            enforce(42, str)
        assert "Expected str, got int" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            enforce("not none", type(None))
        assert "Expected NoneType, got str" in str(exc_info.value)


class TestListAndTupleValidation:
    """Test validation for list and tuple types."""

    def test_valid_lists(self):
        """Test validation of valid lists."""
        assert enforce([], list[int]) == []
        assert enforce([1, 2, 3], list[int]) == [1, 2, 3]
        assert enforce(["a", "b", "c"], list[str]) == ["a", "b", "c"]

        # Nested lists
        assert enforce([[1, 2], [3, 4]], list[list[int]]) == [[1, 2], [3, 4]]

    def test_invalid_lists(self):
        """Test validation of invalid lists."""
        with pytest.raises(ValidationError) as exc_info:
            enforce("not a list", list[int])
        assert "Expected list, got str" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            enforce([1, "not an int", 3], list[int])
        assert "[1]: Expected int, got str" in str(exc_info.value)

        # Nested list errors
        with pytest.raises(ValidationError) as exc_info:
            enforce([[1, 2], [3, "not an int"]], list[list[int]])
        assert "[1][1]: Expected int, got str" in str(exc_info.value)

    def test_valid_tuples(self):
        """Test validation of valid tuples."""
        assert enforce((), tuple[int, ...]) == ()
        assert enforce((1, 2, 3), tuple[int, ...]) == (1, 2, 3)

        # Fixed-length tuples
        assert enforce((1, "hello"), tuple[int, str]) == (1, "hello")

    def test_invalid_tuples(self):
        """Test validation of invalid tuples."""
        with pytest.raises(ValidationError) as exc_info:
            enforce([1, 2, 3], tuple[int, ...])
        assert "Expected tuple, got list" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            enforce((1, 2, "not an int"), tuple[int, ...])
        assert "[2]: Expected int, got str" in str(exc_info.value)

        # Fixed-length tuple errors
        with pytest.raises(ValidationError) as exc_info:
            enforce((1, 2), tuple[int, str])
        assert "[1]: Expected str, got int" in str(exc_info.value)


class TestDictionaryValidation:
    """Test validation for dictionary types."""

    def test_valid_dicts(self):
        """Test validation of valid dictionaries."""
        assert enforce({}, dict[str, int]) == {}
        assert enforce({"a": 1, "b": 2}, dict[str, int]) == {"a": 1, "b": 2}
        assert enforce({1: "a", 2: "b"}, dict[int, str]) == {1: "a", 2: "b"}

        # Nested dictionaries
        assert enforce({"x": {"a": 1}, "y": {"b": 2}}, dict[str, dict[str, int]]) == {
            "x": {"a": 1},
            "y": {"b": 2},
        }

    def test_invalid_dicts(self):
        """Test validation of invalid dictionaries."""
        with pytest.raises(ValidationError) as exc_info:
            enforce("not a dict", dict[str, int])
        assert "Expected dict, got str" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            enforce({"a": 1, "b": "not an int"}, dict[str, int])
        assert "[b]: Expected int, got str" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            enforce({1: "a", "not an int": "b"}, dict[int, str])
        assert "[not an int].key: Expected int, got str" in str(exc_info.value)

        # Nested dictionary errors
        with pytest.raises(ValidationError) as exc_info:
            enforce(
                {"x": {"a": 1}, "y": {"b": "not an int"}}, dict[str, dict[str, int]]
            )
        assert "[y][b]: Expected int, got str" in str(exc_info.value)


class TestTypedDictValidation:
    """Test validation for TypedDict types."""

    def test_valid_typed_dict(self):
        """Test validation of valid TypedDict values."""
        # Full UserInfo
        user = {"name": "Alice", "age": 30, "role": UserRole.ADMIN}
        validated = enforce(user, UserInfo)
        assert validated["name"] == "Alice"
        assert validated["age"] == 30
        assert validated["role"] == UserRole.ADMIN

        # With optional field
        user = {"name": "Bob", "age": 25}
        validated = enforce(user, UserInfo)
        assert validated["name"] == "Bob"
        assert validated["age"] == 25
        assert "role" not in validated

        # Partial UserInfo
        user = {"name": "Charlie"}
        validated = enforce(user, PartialUserInfo)
        assert validated["name"] == "Charlie"

    def test_invalid_typed_dict(self):
        """Test validation of invalid TypedDict values."""
        # Missing required field
        with pytest.raises(ValidationError) as exc_info:
            enforce({"age": 30}, UserInfo)
        assert "Missing required keys: name" in str(exc_info.value)

        # Invalid field type
        with pytest.raises(ValidationError) as exc_info:
            enforce({"name": "Dave", "age": "not an int"}, UserInfo)
        assert "age: Expected int, got str" in str(exc_info.value)

        # Invalid enum value
        with pytest.raises(ValidationError) as exc_info:
            enforce({"name": "Eve", "age": 28, "role": "superuser"}, UserInfo)
        assert "role: Invalid enum value. Valid values: ADMIN, USER, GUEST" in str(
            exc_info.value
        )


class TestOptionalValidation:
    """Test validation for Optional types."""

    def test_valid_optional(self):
        """Test validation of valid Optional values."""
        assert enforce(None, int | None) is None
        assert enforce(42, int | None) == 42
        assert enforce(None, list[str] | None) is None
        assert enforce(["a", "b"], list[str] | None) == ["a", "b"]

    def test_invalid_optional(self):
        """Test validation of invalid Optional values."""
        with pytest.raises(ValidationError) as exc_info:
            enforce("not an int", int | None)
        assert "Value doesn't match any type in Union" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            enforce([1, 2, 3], list[str] | None)
        assert "[0]: Expected str, got int" in str(exc_info.value)


class TestUnionValidation:
    """Test validation for Union types."""

    def test_valid_union(self):
        """Test validation of valid Union values."""
        assert enforce(42, int | str) == 42
        assert enforce("hello", int | str) == "hello"
        assert enforce([1, 2, 3], list[int] | str) == [1, 2, 3]

    def test_invalid_union(self):
        """Test validation of invalid Union values."""
        with pytest.raises(ValidationError) as exc_info:
            enforce(True, int | str)
        assert "Value doesn't match any type in Union" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            enforce([1, "a"], list[int] | list[str])
        assert "Value doesn't match any type in Union" in str(exc_info.value)
        assert "[0]: Expected str, got int" in str(exc_info.value)
        assert "[1]: Expected int, got str" in str(exc_info.value)


class TestLiteralValidation:
    """Test validation for Literal types."""

    def test_valid_literal(self):
        """Test validation of valid Literal values."""
        assert enforce("small", Literal["small", "medium", "large"]) == "small"
        assert enforce(1, Literal[1, 2, 3]) == 1
        assert enforce(None, Literal[None, 1, "a"]) is None

    def test_invalid_literal(self):
        """Test validation of invalid Literal values."""
        with pytest.raises(ValidationError) as exc_info:
            enforce("extra-large", Literal["small", "medium", "large"])
        assert "Expected one of: 'small', 'medium', 'large', got: 'extra-large'" in str(
            exc_info.value
        )

        with pytest.raises(ValidationError) as exc_info:
            enforce(4, Literal[1, 2, 3])
        assert "Expected one of: 1, 2, 3, got: 4" in str(exc_info.value)


class TestEnumValidation:
    """Test validation for Enum types."""

    def test_valid_enum(self):
        """Test validation of valid Enum values."""
        assert enforce(UserRole.ADMIN, UserRole) == UserRole.ADMIN
        assert enforce("ADMIN", UserRole) == UserRole.ADMIN
        assert enforce(0, UserRole) == UserRole.ADMIN  # First enum value

    def test_invalid_enum(self):
        """Test validation of invalid Enum values."""
        with pytest.raises(ValidationError) as exc_info:
            enforce("SUPERUSER", UserRole)
        assert "Invalid enum value. Valid values: ADMIN, USER, GUEST" in str(
            exc_info.value
        )

        with pytest.raises(ValidationError) as exc_info:
            enforce(10, UserRole)  # Out of range
        assert "Invalid enum value" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            enforce(True, UserRole)
        assert "Expected UserRole, got bool" in str(exc_info.value)


class TestDataclassValidation:
    """Test validation for dataclass types."""

    def test_valid_dataclass(self):
        """Test validation of valid dataclass instances."""
        # Direct instance
        point = Point(x=1, y=2)
        assert enforce(point, Point) == point
        assert enforce(point, Point).distance_from_origin() == pytest.approx(
            2.236, 0.001
        )

        # Dict conversion
        point_dict = {"x": 3, "y": 4}
        point = enforce(point_dict, Point)
        assert isinstance(point, Point)
        assert point.x == 3
        assert point.y == 4
        assert point.distance_from_origin() == 5.0

        # Nested dataclass
        shape_dict = {
            "points": [{"x": 1, "y": 2}, {"x": 3, "y": 4}],
            "name": "rectangle",
            "properties": {"color": "blue", "filled": True},
        }
        shape = enforce(shape_dict, Shape)
        assert isinstance(shape, Shape)
        assert isinstance(shape.points[0], Point)
        assert shape.points[0].x == 1
        assert shape.points[1].distance_from_origin() == 5.0
        assert shape.name == "rectangle"
        assert shape.properties["color"] == "blue"

    def test_invalid_dataclass(self):
        """Test validation of invalid dataclass instances."""
        # Missing field
        with pytest.raises(ValidationError) as exc_info:
            enforce({"x": 1}, Point)
        assert "Failed to create dataclass" in str(exc_info.value)

        # Invalid field type
        with pytest.raises(ValidationError) as exc_info:
            enforce({"x": "not an int", "y": 2}, Point)
        assert "x: Expected int, got str" in str(exc_info.value)

        # Invalid value for nested dataclass
        with pytest.raises(ValidationError) as exc_info:
            enforce(
                {
                    "points": [{"x": 1, "y": "not an int"}],
                    "name": "rectangle",
                    "properties": {},
                },
                Shape,
            )
        assert "points[0].y: Expected int, got str" in str(exc_info.value)


class TestErrorPathReporting:
    """Test detailed error path reporting in validation errors."""

    def test_nested_error_paths(self):
        """Test that error paths accurately show where errors occurred."""
        # Deeply nested structure
        complex_type = dict[str, list[dict[str, int | list[Point]]]]
        complex_data = {
            "items": [
                {"id": 1, "points": [{"x": 1, "y": 2}]},
                {"id": 2, "points": [{"x": 3, "y": "not an int"}]},
            ]
        }

        with pytest.raises(ValidationError) as exc_info:
            enforce(complex_data, complex_type)

        error_msg = str(exc_info.value)
        # Accept either format for path: [items][1][points] or items[1][points]
        assert (
            "[items][1][points][0].y: Expected int, got str" in error_msg
            or "items[1][points][0].y: Expected int, got str" in error_msg
        )


class TestTypeEnforcerClass:
    """Test direct usage of the TypeEnforcer class."""

    def test_reuse_enforcer(self):
        """Test reusing the same enforcer for multiple validations."""
        enforcer = TypeEnforcer(list[int])

        assert enforcer.validate([1, 2, 3]) == [1, 2, 3]

        with pytest.raises(ValidationError):
            enforcer.validate([1, "not an int", 3])

        # Enforcer is still usable after errors
        assert enforcer.validate([4, 5, 6]) == [4, 5, 6]


class TestEdgeCasesAndCoverage:
    """Test edge cases and areas previously missed by coverage."""

    def test_any_type(self):
        """Test that Any accepts any value."""
        assert enforce(1, Any) == 1
        assert enforce("hello", Any) == "hello"
        assert enforce(None, Any) is None
        assert enforce([1, 2], Any) == [1, 2]

    def test_invalid_none(self):
        """Test enforcing None type with non-None value."""
        with pytest.raises(ValidationError) as exc_info:
            enforce(0, type(None))
        assert "Expected NoneType, got int" in str(exc_info.value)

    def test_invalid_optional_none(self):
        """Test giving None when not Optional."""
        with pytest.raises(ValidationError) as exc_info:
            enforce(None, int)
        assert "Expected int, got None" in str(exc_info.value)

    def test_bool_as_int_disallowed(self):
        """Test that bool is not accepted as int (outside Union)."""
        with pytest.raises(ValidationError) as exc_info:
            enforce(True, int)
        assert "Expected int, got bool" in str(exc_info.value)
        with pytest.raises(ValidationError) as exc_info:
            enforce(False, int)
        assert "Expected int, got bool" in str(exc_info.value)

    def test_int_to_float_conversion(self):
        """Test that int is automatically converted to float."""
        assert enforce(42, float) == 42.0

    def test_union_bool_mismatch(self):
        """Test bool mismatch in Union (specific error message)."""
        with pytest.raises(ValidationError) as exc_info:
            enforce(True, str | float)
        assert "Value doesn\'t match any type in Union. Got bool" in str(exc_info.value)

    def test_sequence_no_args(self):
        """Test list/tuple validation with no type args."""
        assert enforce([1, "a", None], list) == [1, "a", None]
        assert enforce((1, "a", None), tuple) == (1, "a", None)

    def test_dict_no_args(self):
        """Test dict validation with no type args."""
        assert enforce({1: "a", "b": None}, dict) == {1: "a", "b": None}

    def test_invalid_tuple_length(self):
        """Test fixed-length tuple with incorrect length."""
        with pytest.raises(ValidationError) as exc_info:
            enforce((1, 2, 3), tuple[int, int])
        assert "Expected tuple of length 2, got length 3" in str(exc_info.value)

    def test_invalid_tuple_type_during_iteration(self):
        """Test validation error within fixed-length tuple validation."""
        with pytest.raises(ValidationError) as exc_info:
            enforce((1, "not an int"), tuple[int, int])
        assert "[1]: Expected int, got str" in str(exc_info.value)

    def test_invalid_dict_key_type(self):
        """Test validation error for dict key."""
        with pytest.raises(ValidationError) as exc_info:
            enforce({1: "a", "b": "c"}, dict[str, str])
        assert "[1].key: Expected str, got int" in str(exc_info.value)

    def test_typeddict_total_false_unknown_keys(self):
        """Test TypedDict(total=False) with unknown keys."""
        with pytest.raises(ValidationError) as exc_info:
            enforce({"name": "X", "extra": True}, PartialUserInfo)
        assert "Unknown keys found: extra" in str(exc_info.value)

    def test_typeddict_optional_field_validation_failure(self):
        """Test when an optional field exists but has the wrong type."""
        with pytest.raises(ValidationError) as exc_info:
            enforce({"name": "X", "age": 30, "role": "invalid"}, UserInfo)
        assert "role: Invalid enum value" in str(exc_info.value)

    def test_dataclass_dict_creation_type_error(self):
        """Test when dict-to-dataclass conversion fails type check during init."""
        @dataclass
        class StrictPoint:
            x: int
            y: Any # Allow Any during field validation
            def __post_init__(self):
                # Fail if y is not an int during actual object creation
                if not isinstance(self.y, int):
                    raise TypeError("y must be int during init")

        with pytest.raises(ValidationError) as exc_info:
            # Pass a dict that passes field validation but fails __post_init__
            enforce({"x": 1, "y": "2"}, StrictPoint)
        # Now the failure should come from the try/except block in _validate_dataclass
        assert "Failed to create dataclass: y must be int during init" in str(exc_info.value)

    def test_dataclass_not_instance_or_dict(self):
        """Test passing wrong type entirely to dataclass validation."""
        with pytest.raises(ValidationError) as exc_info:
            enforce("not a dict or Point", Point)
        assert "Expected Point, got str" in str(exc_info.value)

    def test_enum_invalid_index(self):
        """Test enum validation with out-of-range index."""
        with pytest.raises(ValidationError) as exc_info:
            enforce(5, UserRole)
        assert "Invalid enum value" in str(exc_info.value)

    def test_enum_invalid_type(self):
        """Test enum validation with completely wrong type."""
        with pytest.raises(ValidationError) as exc_info:
            enforce(object(), UserRole)
        assert "Expected UserRole, got object" in str(exc_info.value)

    def test_literal_none_allowed(self):
        """Test Literal where None is explicitly allowed."""
        assert enforce(None, Literal["a", None, 1]) is None

    def test_final_isinstance_fallback_failure(self):
        """Test the final isinstance check in _validate_value failing."""
        # Create a dummy generic type that isn't handled explicitly
        class DummyGeneric(list):
            pass
        with pytest.raises(ValidationError) as exc_info:
            enforce("hello", DummyGeneric[int])
        assert "Expected DummyGeneric[int], got str" in str(exc_info.value)

    def test_compatibility_methods(self):
        """Test the instance compatibility methods (for coverage)."""
        enforcer = TypeEnforcer(int)
        assert enforcer._type_name(list[int]) == "list[int]"
        assert enforcer._is_optional(int | None) is True
        assert enforcer._is_optional(int) is False
