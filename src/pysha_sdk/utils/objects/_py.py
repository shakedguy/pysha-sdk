"""Pure Python fallback implementations for object utilities."""

from typing import (
    Any,
    Callable,
    Collection,
    Literal,
    Mapping,
    Optional,
    Type,
    TypeAlias,
    TypeVar,
    Union,
)

from pydantic import BaseModel

try:
    from ._objects_cy import change_keys_case as change_keys_case_cy
    HAS_OBJECTS_CY = True
except ImportError:
    HAS_OBJECTS_CY = False

if HAS_OBJECTS_CY:
    def change_keys_case(input_obj: object, method: Callable[[str], str], deep: bool = True) -> object:
        return change_keys_case_cy(input_obj, method, deep)
else:
    def change_keys_case(input_obj: object, method: Callable[[str], str], deep: bool = True) -> object:
        return ChangeKeysCase._change_case(input_obj, method, deep)

# Type definitions
ValidIterables = Union[dict[str, Any], Collection[Any]]

T = TypeVar("T")
IncEx: TypeAlias = Union[
    set[int],
    set[str],
    Mapping[int, Union["IncEx", bool]],
    Mapping[str, Union["IncEx", bool]],
]


def is_iterable_except_str_like(obj: object) -> bool:
    """
    Check if an object is iterable, excluding string-like objects.

    Args:
        obj: Object to check.

    Returns:
        True if object is iterable but not string-like, False otherwise.
    """
    if isinstance(obj, (str, bytes, bytearray, memoryview)):
        return False
    try:
        iter(obj)
        return True
    except TypeError:
        return False


def model_dump(
    model: Union[BaseModel, Mapping[str, Any]],
    mode: Literal["json", "python"] = "python",
    exclude: Optional[IncEx] = None,
    include: Optional[IncEx] = None,
    serialize_as_any: bool = True,
) -> dict[str, Any]:
    """
    Dump a Pydantic model or dictionary to a dictionary.

    Args:
        model (BaseModel | dict[str, Any]): The Pydantic model or dictionary to dump.
        mode (str): The mode of serialization. Defaults to "dict".
        exclude (IncEx, optional): Fields to exclude from the serialization. Defaults to None.
        include (IncEx, optional): Fields to include in the serialization. Defaults to None.
        serialize_as_any (bool): Whether to serialize as any. Defaults to True.

    Returns:
        dict[str, Any]: The resulting dictionary.
    """
    if not isinstance(model, (BaseModel, dict)):
        raise ValueError("Invalid data type, must be a dict or Pydantic model")

    return (
        model.model_dump(
            mode=mode,
            exclude=exclude,
            include=include,
            serialize_as_any=serialize_as_any,
        )
        if isinstance(model, BaseModel)
        else dict(model)
    )


def dict_or_pydantic_model_to_dict(
    data: Union[BaseModel, dict[str, Any]],
) -> dict[str, Any]:
    """
    Convert a Pydantic model or dictionary to a dictionary.

    Args:
        data (BaseModel | dict[str, Any]): The Pydantic model or dictionary to convert.

    Returns:
        dict[str, Any]: The resulting dictionary.
    """
    res = dict()
    if isinstance(data, BaseModel):
        for field_name, field in data.model_fields.items():
            key = field.alias or field_name
            value = getattr(data, key, None)
            res[key] = (
                dict_or_pydantic_model_to_dict(value)
                if isinstance(value, (BaseModel, dict))
                else value
            )
    else:
        for key, value in data.items():
            res[key] = (
                dict_or_pydantic_model_to_dict(value)
                if isinstance(value, (BaseModel, dict))
                else value
            )

    return res


def _return_same_iterable(
    origin: ValidIterables, result: ValidIterables
) -> ValidIterables:
    return (
        set(result)
        if isinstance(origin, set)
        else tuple(result)
        if isinstance(origin, tuple)
        else list(result)
        if isinstance(origin, list)
        else result
    )


def recursive_sort_keys(
    input_value: ValidIterables,
) -> ValidIterables:
    """
    Recursively sort the keys of a dictionary or list of dictionaries.

    Args:
        input_value (dict[str, Any] | Collection[Any]): The input dictionary or list of dictionaries to sort.

    Returns:
        dict[str, Any] | Collection[Any]: The sorted dictionary or list of dictionaries.
    """
    import pydash as _

    if not _.is_iterable(input_value):
        raise ValueError("Invalid input, must be an iterable")
    if _.is_dict(input_value):
        return dict(sorted(dict(input_value).items()))

    return _return_same_iterable(
        input_value, [recursive_sort_keys(item) for item in input_value]
    )


class ChangeKeysCase:
    """
    A utility class for changing the case of keys in dictionaries.
    """

    @staticmethod
    def to_camel_case(input_obj: ValidIterables, deep: bool = True) -> ValidIterables:
        """
        Convert the keys of the input object to camel case.

        Args:
            input_obj (dict[str, Any] | Collection[Any]): The input object (str, dict, or list) to convert.
            deep (bool): Whether to apply the conversion deeply. Defaults to True.

        Returns:
            dict[str, Any] | Collection[Any]: The object with keys converted to camel case.
        """
        from ..strings import to_camel_case

        return change_keys_case(input_obj, to_camel_case, deep)

    @staticmethod
    def to_snake_case(input_obj: ValidIterables, deep: bool = True) -> ValidIterables:
        """
        Convert the keys of the input object to snake case.

        Args:
            input_obj (dict[str, Any] | Collection[Any]): The input object (str, dict, or list) to convert.
            deep (bool): Whether to apply the conversion deeply. Defaults to True.

        Returns:
            dict[str, Any] | Collection[Any]: The object with keys converted to snake case.
        """
        from ..strings import to_snake_case

        return change_keys_case(input_obj, to_snake_case, deep)

    @staticmethod
    def to_kebab_case(input_obj: ValidIterables, deep: bool = True) -> ValidIterables:
        """
        Convert the keys of the input object to kebab case.

        Args:
            input_obj (dict[str, Any] | Collection[Any]): The input object (str, dict, or list) to convert.
            deep (bool): Whether to apply the conversion deeply. Defaults to True.

        Returns:
            dict[str, Any] | Collection[Any]: The object with keys converted to kebab case.
        """
        from ..strings import to_kebab_case

        return change_keys_case(input_obj, to_kebab_case, deep)

    @staticmethod
    def to_pascal_case(input_obj: ValidIterables, deep: bool = True) -> ValidIterables:
        """
        Convert the keys of the input object to pascal case.

        Args:
            input_obj (dict[str, Any] | Collection[Any]): The input object (str, dict, or list) to convert.
            deep (bool): Whether to apply the conversion deeply. Defaults to True.

        Returns:
            dict[str, Any] | Collection[Any]: The object with keys converted to pascal case.
        """
        from ..strings import to_pascale_case

        return change_keys_case(input_obj, to_pascale_case, deep)

    @staticmethod
    def to_constant_case(
        input_obj: ValidIterables, deep: bool = True
    ) -> ValidIterables:
        """
        Convert the keys of the input object to constant case.

        Args:
            input_obj (dict[str, Any] | Collection[Any]): The input object (str, dict, or list) to convert.
            deep (bool): Whether to apply the conversion deeply. Defaults to True.

        Returns:
            dict[str, Any] | Collection[Any]: The object with keys converted to constant case.
        """
        from ..strings import to_constant_case

        return change_keys_case(input_obj, to_constant_case, deep)

    @staticmethod
    def to_dot_case(input_obj: ValidIterables) -> ValidIterables:
        """
        Convert the keys of the input dictionary to dot case and sort them.

        Args:
            input_obj (dict[str, Any] | Collection[Any]): The input dictionary to convert.

        Returns:
            dict[str, Any] | Collection[Any]: The dictionary with keys converted to dot case and sorted.
        """
        return recursive_sort_keys(
            ChangeKeysCase._change_to_dot_case(ChangeKeysCase.to_snake_case(input_obj))
        )

    @staticmethod
    def _change_case(
        input_obj: ValidIterables, method: Callable[[str], str], deep: bool = True
    ) -> ValidIterables:
        """
        Helper method to change the case of keys in the input object using the specified method.

        Args:
            input_obj (dict[str, Any] | Collection[Any]): The input object (str, dict, or list) to convert.
            method (Callable[[str], str]): The method to use for changing the case.
            deep (bool): Whether to apply the conversion deeply. Defaults to True.

        Returns:
            ValidIterables: The object with keys converted using the specified method.
        """
        import pydash as _

        if isinstance(input_obj, (bytes, str, bytearray, memoryview)):
            return method(input_obj)

        if _.is_dict(input_obj):
            for key in filter(lambda k: k.startswith("_"), input_obj.keys()):
                new_key = str(key).lstrip("_")
                if new_key in input_obj:
                    input_obj[new_key] = input_obj[new_key] or input_obj[key]

            return {
                method(key): ChangeKeysCase._change_case(value, method)
                if deep and is_iterable_except_str_like(value)
                else value
                for key, value in dict(input_obj).items()
            }

        return _return_same_iterable(
            input_obj,
            [
                ChangeKeysCase._change_case(item, method)
                if is_iterable_except_str_like(item)
                else item
                for item in input_obj
            ],
        )

    @staticmethod
    def _change_to_dot_case(
        input_obj: ValidIterables, prefix: str = ""
    ) -> ValidIterables:
        """
        Helper method to convert the keys of the input dictionary to dot case.

        Args:
            input_obj (dict[str, Any] | Collection[Any]): The input dictionary to convert.
            prefix (str, optional): The prefix to add to the keys. Defaults to "".

        Returns:
            dict[str, Any] | Collection[Any]: The dictionary with keys converted to dot case.
        """
        import pydash as _

        if not _.is_iterable(input_obj):
            raise ValueError("Invalid input, must be an iterable")

        if not _.is_dict(input_obj):
            return _return_same_iterable(
                input_obj,
                [
                    ChangeKeysCase._change_to_dot_case(item, prefix)
                    for item in input_obj
                ],
            )

        result = {}
        for key, value in dict(input_obj).items():
            new_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                result.update(ChangeKeysCase._change_to_dot_case(value, new_key))
            elif isinstance(value, list):
                for index, item in enumerate(value):
                    if isinstance(item, dict):
                        result.update(
                            ChangeKeysCase._change_to_dot_case(
                                item, f"{new_key}.[{index}]"
                            )
                        )
                    else:
                        result[f"{new_key}[{index}]"] = item
            else:
                result[new_key] = value
        return result



def find_subclasses(base_class: Type[T]) -> list[Type[T]]:
    """
    Find all classes that inherit from the given base class.

    Args:
        base_class: The class to find subclasses for

    Returns:
        list: A list of all subclasses (direct and indirect)
    """
    # Note: orm import removed as it's not available in pysha-sdk
    direct_subclasses = base_class.__subclasses__()
    all_subclasses = list(direct_subclasses)

    for subclass in direct_subclasses:
        all_subclasses.extend(find_subclasses(subclass))

    res = list(dict.fromkeys(all_subclasses))

    # Note: orm module inspection removed as it's not available in pysha-sdk
    return res
