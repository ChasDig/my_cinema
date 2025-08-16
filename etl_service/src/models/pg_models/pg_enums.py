import enum

from sqlalchemy.dialects.postgresql import ENUM


class PersonsAssociationEnum(enum.Enum):
    actor = "actor"
    producer = "producer"
    director = "director"

    @classmethod
    def names(cls) -> list[str]:
        return [en.name for en in cls]


person_type_enum = ENUM(
    *PersonsAssociationEnum.names(),
    name="person_type_enum",
    create_type=True,
)
