from sqlalchemy.dialects.postgresql import ENUM

person_type_enum = ENUM(
    "actor", "producer", "director", name="person_type_enum", create_type=True
)
