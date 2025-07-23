"""
Type Enforcer - A utility for enforcing strongly typed responses.

This module provides a clean, efficient way to enforce type constraints on data
with detailed error reporting, runtime validation, and support for complex types
including nested structures, unions, and optional values.

Compatible with Python 3.13+ only.
"""

import types
from dataclasses import is_dataclass
from enum import Enum
from functools import cache
from typing import (
    Any,
    Literal,
    Union,
    get_args,
    get_origin,
    get_type_hints,
    is_typeddict,
)


# Cache type introspection functions at the module level for performance
@cache
def _cached_get_origin(tp: type) -> Any:
    """Cached version of get_origin."""
    return get_origin(tp)


@cache
def _cached_get_args(tp: type) -> tuple:
    """Cached version of get_args."""
    return get_args(tp)


@cache
def _cached_is_optional(type_hint: type) -> bool:
    """Check if a type hint is Optional (Union with NoneType). Use cache."""
    origin = get_origin(type_hint)
    args = get_args(type_hint)
    return (
        (origin is Union or origin is types.UnionType)  # Check both Union and | syntax
        and type(None) in args
    )


@cache
def _cached_get_type_hints(tp: type) -> dict:
    """Cached version of get_type_hints."""
    try:
        return get_type_hints(tp)
    except (TypeError, ValueError, NameError, AttributeError):
        # Handle cases where get_type_hints fails (e.g., unresolvable forward refs)
        return {}


@cache
def _cached_is_typeddict(tp: type) -> bool:
    """Cached version of is_typeddict."""
    try:
        return is_typeddict(tp)
    except (TypeError, ValueError, NameError, AttributeError):
        # Handle cases where get_type_hints fails (e.g., unresolvable forward refs)
        return False


@cache
def _type_name(type_: type) -> str:
    """Gets a readable name for a type."""
    # Special handling for generic types like List[int], Dict[str, int], etc.
    origin = get_origin(type_)
    if origin is not None:
        args = get_args(type_)
        origin_name = getattr(origin, "__name__", str(origin))

        # For types without arguments, just return the origin name
        if not args:
            return origin_name

        # Otherwise, format with arguments: Name[Arg1, Arg2, ...]
        args_str = ", ".join(_type_name(arg) for arg in args)
        return f"{origin_name}[{args_str}]"

    # For non-generic types, use __name__ if available
    if hasattr(type_, "__name__"):
        return type_.__name__

    # Fallback to string representation
    return str(type_)


class ValidationError(Exception):
    """Exception raised when type validation fails."""

    def __init__(self, message: str, path: str = ""):
        self.path = path
        self.message = message
        super().__init__(f"{path}: {message}" if path else message)


class TypeEnforcer[T]:
    """
    Validates and enforces types on data.

    This class provides a way to check that a given value matches
    a specified target type at runtime, with detailed error reporting.
    """

    def __init__(self, target_type: type[T]):
        """
        Initialize a new TypeEnforcer.

        Args:
            target_type: The type to enforce
        """
        self.target_type = target_type

    # Compatibility methods for existing tests
    # These will be deprecated in the future
    def _type_name(self, type_: type) -> str:
        """Compatibility method for existing tests. Will be deprecated."""
        return _type_name(type_)

    def _is_optional(self, type_: type) -> bool:
        """Compatibility method for existing tests. Will be deprecated."""
        return _cached_is_optional(type_)

    def validate(self, data: Any) -> T:
        """
        Validates and enforces that the given data matches the target type.

        Args:
            data: Data to validate against the target type

        Returns:
            The validated data cast to the target type

        Raises:
            ValidationError: If the data doesn't match the target type
        """
        return self._validate_value(data, self.target_type, "")

    def _validate_value(self, value: Any, expected_type: type, path: str) -> Any:
        """Recursive validation function that handles complex types."""
        # Handle Any type - accepts anything
        if expected_type is Any:
            return value

        # Special case for NoneType
        if expected_type is type(None):
            if value is None:
                return None
            raise ValidationError(f"Expected NoneType, got {type(value).__name__}", path)

        # Get the origin type (like list, dict, etc.) using cached function
        origin = _cached_get_origin(expected_type)

        # Handle Literal types early to properly handle None
        if origin is Literal:
            return self._validate_literal(value, expected_type, path)

        # Handle None for Optional types using cached function
        if value is None:
            if _cached_is_optional(expected_type):
                return None
            raise ValidationError(f"Expected {_type_name(expected_type)}, got None", path)

        # Handle TypedDict (must happen before primitive check)
        if _cached_is_typeddict(expected_type):
            return self._validate_typed_dict(value, expected_type, path)

        # Handle primitive types
        if origin is None:
            return self._validate_primitive(value, expected_type, path)

        # Handle Union types (both Union[...] and X | Y)
        if origin is Union or origin is types.UnionType:
            return self._validate_union(value, expected_type, path)

        # Handle list types
        if origin is list:
            return self._validate_sequence(value, expected_type, path, list)

        # Handle tuple types
        if origin is tuple:
            return self._validate_tuple(value, expected_type, path)

        # Handle dict types
        if origin is dict:
            return self._validate_dict(value, expected_type, path)

        # Default case - try basic isinstance check
        if not isinstance(value, origin):
            raise ValidationError(
                f"Expected {_type_name(expected_type)}, got {type(value).__name__}",
                path,
            )

        return value

    def _validate_primitive(self, value: Any, expected_type: type, path: str) -> Any:
        """Validates a primitive type."""
        # Handle dataclasses
        if is_dataclass(expected_type):
            return self._validate_dataclass(value, expected_type, path)

        # Handle Enum types
        if isinstance(expected_type, type) and issubclass(expected_type, Enum):
            return self._validate_enum(value, expected_type, path)

        # Handle bool specially - because bool is a subclass of int
        if expected_type is int and isinstance(value, bool):
            raise ValidationError("Expected int, got bool", path)

        # Special case: Allow int to be converted to float
        if expected_type is float and isinstance(value, int):
            return float(value)

        # Basic isinstance check for primitive types
        if not isinstance(value, expected_type):
            raise ValidationError(f"Expected {expected_type.__name__}, got {type(value).__name__}", path)

        return value

    def _validate_union(self, value: Any, expected_type: type, path: str) -> Any:
        """Validates against Union types."""
        args = _cached_get_args(expected_type)
        errors = []

        # Check for bool specifically *before* iterating through union types if bool is not allowed
        is_bool = isinstance(value, bool)
        bool_in_union = bool in args

        if is_bool and not bool_in_union:
            # Explicitly reject bool if it's not part of the Union
            types_str = " | ".join(str(t) for t in args)
            raise ValidationError(
                f"Value doesn't match any type in Union. Got bool, expected one of: {types_str}", path
            )

        for arg_type in args:
            try:
                return self._validate_value(value, arg_type, path)
            except ValidationError as e:
                errors.append(str(e))

        # If we get here, nothing matched
        # The specific bool case is handled above, so this is for other mismatches
        types_str = " | ".join(str(t) for t in args)
        errors_str = "; ".join(errors)
        error_msg = f"Value doesn't match any type in Union: {types_str}\nValidation errors: {errors_str}"
        raise ValidationError(error_msg, path)

    def _validate_sequence(self, value: Any, expected_type: type, path: str, container_type: type = list) -> Any:
        """Validates sequence types (list/tuple)."""
        if not isinstance(value, container_type):
            raise ValidationError(f"Expected {container_type.__name__}, got {type(value).__name__}", path)

        args = _cached_get_args(expected_type)

        # If no type args specified, any sequence is valid
        if not args:
            return value

        # Get the expected item type
        item_type = args[0]
        result = []

        for i, item in enumerate(value):  # type: ignore[var-annotated,arg-type]
            item_path = f"{path}[{i}]"
            validated_item = self._validate_value(item, item_type, item_path)
            result.append(validated_item)

        return container_type(result)

    def _validate_tuple(self, value: Any, expected_type: type, path: str) -> Any:
        """Validates tuple types including fixed-length tuples."""
        if not isinstance(value, tuple):
            raise ValidationError(f"Expected tuple, got {type(value).__name__}", path)

        args = _cached_get_args(expected_type)

        # If no type args or empty args, any tuple is valid
        if not args:
            return value

        # Handle Tuple[X, ...] - homogeneous tuple
        if args[-1] is ... and len(args) == 2:
            item_type = args[0]
            result = []

            # Ensure value is a tuple before iterating
            if isinstance(value, tuple):
                # Explicitly cast for mypy - removed, use ignore instead
                # value_tuple: tuple = value
                for i, item in enumerate(value):  # type: ignore[arg-type, var-annotated]
                    item_path = f"{path}[{i}]"
                    validated_item_homog = self._validate_value(item, item_type, item_path)
                    result.append(validated_item_homog)

                return tuple(result)

        # Handle fixed-length tuples like Tuple[int, str]
        if len(value) != len(args):
            raise ValidationError(f"Expected tuple of length {len(args)}, got length {len(value)}", path)

        result = []
        # Ensure value is a tuple before iterating
        if isinstance(value, tuple):
            # Explicitly cast for mypy
            value_tuple_fixed: tuple = value  # Renamed variable
            for i, (item, arg_type) in enumerate(zip(value_tuple_fixed, args, strict=False)):
                item_path = f"{path}[{i}]"
                validated_item: Any = self._validate_value(item, arg_type, item_path)
                result.append(validated_item)
        return tuple(result)

    def _validate_dict(self, value: Any, expected_type: type, path: str) -> Any:
        """Validates dictionary types."""
        if not isinstance(value, dict):
            raise ValidationError(f"Expected dict, got {type(value).__name__}", path)

        args = _cached_get_args(expected_type)

        # If no type args specified, any dict is valid
        if not args or len(args) != 2:
            return value

        key_type, val_type = args
        result = {}

        for k, v in value.items():
            # Validate key
            key_path = f"{path}[{k}].key"
            validated_key = self._validate_value(k, key_type, key_path)

            # Validate value
            val_path = f"{path}[{k}]"
            validated_val = self._validate_value(v, val_type, val_path)

            result[validated_key] = validated_val

        return result

    def _validate_typed_dict(self, value: Any, expected_type: type, path: str) -> Any:
        """Validates TypedDict instances."""
        if not isinstance(value, dict):
            raise ValidationError(f"Expected dict (TypedDict), got {type(value).__name__}", path)

        # Get type hints for the TypedDict using cached function
        hints = _cached_get_type_hints(expected_type)
        result = {}

        # Get info about total/required/optional
        total = getattr(expected_type, "__total__", True)  # Default to total=True

        if total:
            # All fields are required unless explicitly marked as optional
            required_keys = set()
            optional_keys = set()

            for key, field_type in hints.items():
                if _cached_is_optional(field_type):
                    optional_keys.add(key)
                else:
                    required_keys.add(key)
        else:
            # total=False means all fields are optional
            required_keys = set()
            optional_keys = set(hints.keys())

        # Check for missing required keys
        missing_keys = required_keys - value.keys()
        if missing_keys:
            raise ValidationError(f"Missing required keys: {', '.join(sorted(missing_keys))}", path)

        # Validate each field
        for key, field_type in hints.items():
            if key in value:
                field_path = f"{path}.{key}" if path else key
                try:
                    validated_val = self._validate_value(value[key], field_type, field_path)
                    result[key] = validated_val
                except ValidationError:
                    # This condition seems unreachable: if value[key] is None and the field
                    # is optional, _validate_value should handle it successfully without raising
                    # the ValidationError needed to reach this except block.
                    # if key in optional_keys and value[key] is None:
                    #     continue
                    if key in optional_keys and value[key] is None:
                        continue
                    raise  # Re-raise the exception for required fields or invalid types

        # Check for unknown keys - always raise error for unknown keys (strict mode)
        unknown_keys = value.keys() - hints.keys()
        if unknown_keys:
            raise ValidationError(f"Unknown keys found: {', '.join(sorted(unknown_keys))}", path)

        return result

    def _validate_dataclass(self, value: Any, expected_type: type, path: str) -> Any:
        """Validates dataclass instances."""
        # Convert dict to dataclass if needed
        if isinstance(value, dict):
            # Get field types using cached function
            field_types = _cached_get_type_hints(expected_type)
            validated_data = {}

            for field_name, field_type in field_types.items():
                if field_name in value:
                    field_path = f"{path}.{field_name}" if path else field_name
                    validated_data[field_name] = self._validate_value(value[field_name], field_type, field_path)

            # Create instance using validated data
            try:
                return expected_type(**validated_data)
            except TypeError as e:
                raise ValidationError(f"Failed to create dataclass: {e!s}", path) from e

        # If it's already an instance, validate fields
        if not isinstance(value, expected_type):
            raise ValidationError(f"Expected {expected_type.__name__}, got {type(value).__name__}", path)

        return value

    def _validate_enum(self, value: Any, expected_type: type[Enum], path: str) -> Any:
        """Validates Enum instances."""
        # If value is already the right enum type
        if isinstance(value, expected_type):
            return value

        # Special case for bool (it's a subclass of int, so the int validation below
        # would incorrectly accept booleans)
        if isinstance(value, bool):
            valid_values = [e.name for e in expected_type]
            error_msg = f"Expected {expected_type.__name__}, got bool. Valid values: {', '.join(valid_values)}"
            raise ValidationError(error_msg, path)

        # Try to convert a string/int to enum value
        try:
            if isinstance(value, str):
                return expected_type[value]
            if isinstance(value, int):
                enum_values = list(expected_type)
                if 0 <= value < len(enum_values):
                    return enum_values[value]
                raise IndexError(f"Enum index {value} out of range")
        except (KeyError, IndexError):
            valid_values = [e.name for e in expected_type]
            raise ValidationError(f"Invalid enum value. Valid values: {', '.join(valid_values)}", path) from None

        # If it's not a string or int, it's definitely invalid
        raise ValidationError(f"Expected {expected_type.__name__}, got {type(value).__name__}", path)

    def _validate_literal(self, value: Any, expected_type: type, path: str) -> Any:
        """Validates Literal types."""
        allowed_values = _cached_get_args(expected_type)

        # Special case: if None is one of the allowed values and value is None
        if value is None and None in allowed_values:
            return None

        if value not in allowed_values:
            formatted_values = [repr(v) for v in allowed_values]
            raise ValidationError(
                f"Expected one of: {', '.join(formatted_values)}, got: {value!r}",
                path,
            )

        return value


def enforce[T](data: Any, expected_type: type[T]) -> T:
    """
    Enforce a type constraint on data.

    This is a convenience function that creates a TypeEnforcer and validates
    data against the expected type.

    Args:
        data: The data to validate
        expected_type: The expected type of the data

    Returns:
        The validated data, possibly with some conversions applied

    Raises:
        ValidationError: If the data does not match the expected type
    """
    return TypeEnforcer(expected_type).validate(data)
