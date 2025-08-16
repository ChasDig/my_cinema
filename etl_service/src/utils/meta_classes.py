from typing import Any, ClassVar, Type, TypeVar, cast

T = TypeVar("T")


class SingletonMeta(type):
    """Metaclass - Singleton."""

    _instances: ClassVar[dict[Type[Any], Any]] = {}

    def __call__(cls: Type[T], *args: Any, **kwargs: Any) -> T:
        if cls not in cls._instances:  # type: ignore[attr-defined]
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance  # type: ignore[attr-defined]

        return cast(T, cls._instances[cls])  # type: ignore[attr-defined]
