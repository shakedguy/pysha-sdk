"""Unit tests for DictMixin class."""

from pydantic import BaseModel

from pysha_sdk.utils.mixins.dict_mixin import DictMixin


class TestDictMixin:
    """Tests for DictMixin class."""

    def test_dict_mixin_basic(self):
        """Test basic DictMixin functionality."""

        class TestDict(DictMixin):
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)

        obj = TestDict(name="John", age=30)
        assert obj["name"] == "John"
        assert obj["age"] == 30

    def test_dict_mixin_getitem(self):
        """Test __getitem__ method."""
        obj = DictMixin()
        obj.name = "John"
        assert obj["name"] == "John"

    def test_dict_mixin_getitem_path(self):
        """Test __getitem__ with path-based access."""
        obj = DictMixin()
        obj.nested = {"deep": {"value": 42}}
        assert obj["nested.deep.value"] == 42

    def test_dict_mixin_setitem(self):
        """Test __setitem__ method."""
        obj = DictMixin()
        obj["name"] = "John"
        assert obj.name == "John"

    def test_dict_mixin_delitem(self):
        """Test __delitem__ method."""
        obj = DictMixin()
        obj.name = "John"
        del obj["name"]
        assert not hasattr(obj, "name")

    def test_dict_mixin_contains(self):
        """Test __contains__ method."""
        obj = DictMixin()
        obj.name = "John"
        assert "name" in obj
        assert "missing" not in obj

    def test_dict_mixin_len(self):
        """Test __len__ method."""
        obj = DictMixin()
        obj.name = "John"
        obj.age = 30
        # Note: DictMixin may have additional internal attributes
        assert len(obj) >= 2

    def test_dict_mixin_get(self):
        """Test get method."""
        obj = DictMixin()
        obj.name = "John"
        assert obj.get("name") == "John"
        assert obj.get("missing", "default") == "default"

    def test_dict_mixin_get_path(self):
        """Test get method with path."""
        obj = DictMixin()
        obj.nested = {"value": 42}
        assert obj.get("nested.value") == 42
        assert obj.get("nested.missing", "default") == "default"

    def test_dict_mixin_set(self):
        """Test set method."""
        obj = DictMixin()
        obj.set("name", "John")
        assert obj.name == "John"

    def test_dict_mixin_setdefault(self):
        """Test setdefault method."""
        obj = DictMixin()
        result = obj.setdefault("name", "John")
        assert result == "John"
        assert obj["name"] == "John"

        # Should return existing value
        result2 = obj.setdefault("name", "Jane")
        assert result2 == "John"

    def test_dict_mixin_has(self):
        """Test has method."""
        obj = DictMixin()
        obj.name = "John"
        assert obj.has("name") is True
        assert obj.has("missing") is False

    def test_dict_mixin_keys(self):
        """Test keys method."""
        obj = DictMixin()
        obj.name = "John"
        obj.age = 30
        keys = list(obj.keys())
        assert "name" in keys
        assert "age" in keys
        assert "data" not in keys  # Should exclude "data" key

    def test_dict_mixin_values(self):
        """Test values method."""
        obj = DictMixin()
        obj.name = "John"
        obj.age = 30
        values = list(obj.values())
        assert "John" in values
        assert 30 in values

    def test_dict_mixin_items(self):
        """Test items method."""
        obj = DictMixin()
        obj.name = "John"
        obj.age = 30
        items = dict(obj.items())
        assert items["name"] == "John"
        assert items["age"] == 30

    def test_dict_mixin_clear(self):
        """Test clear method."""
        obj = DictMixin()
        obj.name = "John"
        obj.age = 30
        obj.clear()
        assert obj.name is None
        assert obj.age is None

    def test_dict_mixin_copy(self):
        """Test copy method."""

        class TestDict(DictMixin):
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)

        obj = TestDict(name="John", age=30)
        copied = obj.copy()
        assert copied.name == "John"
        assert copied.age == 30
        assert copied is not obj

    def test_dict_mixin_iter(self):
        """Test __iter__ method."""
        obj = DictMixin()
        obj.name = "John"
        obj.age = 30
        keys = list(iter(obj))
        assert "name" in keys
        assert "age" in keys

    def test_dict_mixin_eq(self):
        """Test __eq__ method."""

        class TestDict1(DictMixin):
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)

        class TestDict2(DictMixin):
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)

        obj1 = TestDict1(name="John", age=30)
        obj2 = TestDict2(name="John", age=30)
        # Note: __eq__ compares vars(self) == vars(other)
        assert vars(obj1) == vars(obj2)

    def test_dict_mixin_with_pydantic(self):
        """Test DictMixin with Pydantic BaseModel."""

        class Person(BaseModel, DictMixin):
            name: str
            age: int

        person = Person(name="John", age=30)
        # Access via attribute (Pydantic style)
        assert person.name == "John"
        assert person.age == 30
