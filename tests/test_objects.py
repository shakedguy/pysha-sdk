"""Unit tests for object utilities module."""

import pytest
from pydantic import BaseModel

from pysha_sdk.utils.objects import (
    ChangeKeysCase,
    dict_or_pydantic_model_to_dict,
    find_subclasses,
    is_iterable_except_str_like,
    model_dump,
    recursive_sort_keys,
)


class TestModelDump:
    """Tests for model_dump function."""

    def test_model_dump_with_dict(self):
        """Test model_dump with dictionary."""
        data = {"name": "John", "age": 30}
        result = model_dump(data)
        assert result == data

    def test_model_dump_with_pydantic_model(self):
        """Test model_dump with Pydantic model."""

        class Person(BaseModel):
            name: str
            age: int

        person = Person(name="John", age=30)
        result = model_dump(person)
        assert result == {"name": "John", "age": 30}

    def test_model_dump_invalid_type(self):
        """Test model_dump with invalid type raises error."""
        with pytest.raises(ValueError):
            model_dump("not a dict or model")


class TestDictOrPydanticModelToDict:
    """Tests for dict_or_pydantic_model_to_dict function."""

    def test_dict_or_pydantic_model_to_dict_with_dict(self):
        """Test conversion with dictionary."""
        data = {"name": "John", "age": 30}
        result = dict_or_pydantic_model_to_dict(data)
        assert result == data

    def test_dict_or_pydantic_model_to_dict_with_pydantic_model(self):
        """Test conversion with Pydantic model."""

        class Person(BaseModel):
            name: str
            age: int

        person = Person(name="John", age=30)
        result = dict_or_pydantic_model_to_dict(person)
        assert result == {"name": "John", "age": 30}

    def test_dict_or_pydantic_model_to_dict_nested(self):
        """Test conversion with nested structures."""
        data = {"user": {"name": "John", "age": 30}}
        result = dict_or_pydantic_model_to_dict(data)
        assert result == data


class TestRecursiveSortKeys:
    """Tests for recursive_sort_keys function."""

    def test_recursive_sort_keys_basic(self):
        """Test basic recursive key sorting."""
        data = {"z": 3, "a": 1, "m": 2}
        result = recursive_sort_keys(data)
        assert list(result.keys()) == ["a", "m", "z"]

    def test_recursive_sort_keys_nested(self):
        """Test recursive sorting with nested dicts."""
        data = {"z": 3, "a": 1, "m": {"c": 2, "a": 1}}
        result = recursive_sort_keys(data)
        assert list(result.keys()) == ["a", "m", "z"]
        assert list(result["m"].keys()) == ["a", "c"]

    def test_recursive_sort_keys_list(self):
        """Test recursive sorting with list of dicts."""
        data = [{"z": 3, "a": 1}, {"c": 2, "b": 1}]
        result = recursive_sort_keys(data)
        assert isinstance(result, list)
        assert list(result[0].keys()) == ["a", "z"]
        assert list(result[1].keys()) == ["b", "c"]

    def test_recursive_sort_keys_invalid(self):
        """Test recursive sorting with invalid input."""
        # Note: recursive_sort_keys may handle strings differently
        # Test with a truly invalid input
        with pytest.raises((ValueError, TypeError)):
            recursive_sort_keys(123)  # Integer is not iterable


class TestIsIterableExceptStrLike:
    """Tests for is_iterable_except_str_like function."""

    def test_is_iterable_except_str_like_dict(self):
        """Test with dictionary."""
        assert is_iterable_except_str_like({"a": 1}) is True

    def test_is_iterable_except_str_like_list(self):
        """Test with list."""
        assert is_iterable_except_str_like([1, 2, 3]) is True

    def test_is_iterable_except_str_like_string(self):
        """Test with string (should return False)."""
        assert is_iterable_except_str_like("hello") is False

    def test_is_iterable_except_str_like_bytes(self):
        """Test with bytes (should return False)."""
        assert is_iterable_except_str_like(b"hello") is False

    def test_is_iterable_except_str_like_tuple(self):
        """Test with tuple."""
        assert is_iterable_except_str_like((1, 2, 3)) is True


class TestChangeKeysCase:
    """Tests for ChangeKeysCase class."""

    def test_to_camel_case_dict(self):
        """Test converting dict keys to camel case."""
        data = {"first_name": "John", "last_name": "Doe"}
        result = ChangeKeysCase.to_camel_case(data)
        assert "firstName" in result
        assert "lastName" in result

    def test_to_snake_case_dict(self):
        """Test converting dict keys to snake case."""
        data = {"firstName": "John", "lastName": "Doe"}
        result = ChangeKeysCase.to_snake_case(data)
        assert "first_name" in result
        assert "last_name" in result

    def test_to_kebab_case_dict(self):
        """Test converting dict keys to kebab case."""
        data = {"first_name": "John", "last_name": "Doe"}
        result = ChangeKeysCase.to_kebab_case(data)
        assert "first-name" in result
        assert "last-name" in result

    def test_to_pascal_case_dict(self):
        """Test converting dict keys to Pascal case."""
        data = {"first_name": "John", "last_name": "Doe"}
        result = ChangeKeysCase.to_pascal_case(data)
        assert "FirstName" in result
        assert "LastName" in result

    def test_to_constant_case_dict(self):
        """Test converting dict keys to constant case."""
        data = {"first_name": "John", "last_name": "Doe"}
        result = ChangeKeysCase.to_constant_case(data)
        assert "FIRST_NAME" in result
        assert "LAST_NAME" in result

    def test_to_camel_case_nested(self):
        """Test converting nested dict keys to camel case."""
        data = {"user_data": {"first_name": "John"}}
        result = ChangeKeysCase.to_camel_case(data, deep=True)
        assert "userData" in result
        assert "firstName" in result["userData"]

    def test_to_camel_case_list(self):
        """Test converting list of dicts."""
        data = [{"first_name": "John"}, {"last_name": "Doe"}]
        result = ChangeKeysCase.to_camel_case(data)
        assert isinstance(result, list)
        assert "firstName" in result[0]

    def test_to_dot_case(self):
        """Test converting to dot case."""
        data = {"user": {"name": "John"}}
        result = ChangeKeysCase.to_dot_case(data)
        assert isinstance(result, dict)


class TestFindSubclasses:
    """Tests for find_subclasses function."""

    def test_find_subclasses_basic(self):
        """Test finding subclasses of a base class."""

        class Base:
            pass

        class Child1(Base):
            pass

        class Child2(Base):
            pass

        class GrandChild(Child1):
            pass

        result = find_subclasses(Base)
        assert Child1 in result
        assert Child2 in result
        assert GrandChild in result

    def test_find_subclasses_no_subclasses(self):
        """Test finding subclasses when none exist."""

        class Base:
            pass

        result = find_subclasses(Base)
        assert isinstance(result, list)
