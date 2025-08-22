from datetime import date
from enum import Enum
from uuid import uuid4

from django.core import exceptions, validators
from django.db import models


class PersonsTypesEmployment(Enum):
    ACTOR = "actor"
    PRODUCER = "producer"
    DIRECTOR = "director"

    @classmethod
    def choices(cls) -> list[tuple[str, str]]:
        return [(item.value, item.name.capitalize()) for item in cls]


class UUIDMixin(models.Model):
    """Postgres Mixin: ID(UUID)."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True


class DatetimeStampedMixin(models.Model):
    """Postgres Mixin: DatetimeStamped."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ActiveMixin(models.Model):
    """Postgres Mixin: являются ли данные активными."""

    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Persons(UUIDMixin, DatetimeStampedMixin, ActiveMixin):
    """Postgres модель - Персоны."""

    first_name = models.CharField(max_length=64, null=False)
    second_name = models.CharField(max_length=64, null=True)
    last_name = models.CharField(max_length=64, null=False)
    birthday = models.DateField(null=False)
    place_of_birth = models.CharField(max_length=64, null=True)
    type_employment = models.CharField(
        max_length=32,
        choices=PersonsTypesEmployment.choices(),
        null=False,
        help_text="Тип деятельности персоны",
    )

    class Meta:
        db_table = 'movies"."persons'
        verbose_name = "Персона"
        verbose_name_plural = "Персоны"

    def clean(self) -> None:
        errors = dict()

        nax_date_birthday = date(year=1795, month=1, day=1)
        if self.birthday < nax_date_birthday:
            errors["birthday"] = exceptions.ValidationError(
                f"Максимальная дата рождения: {nax_date_birthday.isoformat()}",
            )

        if errors:
            raise exceptions.ValidationError(errors)

    def __str__(self) -> str:
        return (
            f"{self.first_name} {self.second_name} {self.last_name}"
            if self.second_name
            else f"{self.first_name} {self.last_name}"
        )


class MoviesPersonsAssociation(UUIDMixin):
    """Postgres модель-связка Фильма и Персоны."""

    movie_id = models.ForeignKey("Movies", on_delete=models.CASCADE)
    person_id = models.ForeignKey("Persons", on_delete=models.CASCADE)

    class Meta:
        db_table = 'movies"."movies_persons_association'

    def __str__(self) -> str:
        return f"MovieID={self.movie_id}, PersonID={self.person_id}"


class Genres(UUIDMixin, DatetimeStampedMixin, ActiveMixin):
    """Postgres модель - Жанры."""

    title = models.CharField(max_length=128, null=False)
    description = models.TextField(null=False)
    age_rating = models.SmallIntegerField(
        null=False,
        validators=[
            validators.MinValueValidator(0),
            validators.MaxValueValidator(18),
        ],
        db_index=True,
        help_text="Возрастной рейтинг жанра",
    )

    class Meta:
        db_table = 'movies"."genres'
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    def __str__(self) -> str:
        return self.title


class MoviesGenresAssociation(UUIDMixin):
    """Postgres модель-связка - Фильма и Жанра."""

    movie_id = models.ForeignKey("Movies", on_delete=models.CASCADE)
    genre_id = models.ForeignKey("Genres", on_delete=models.CASCADE)

    class Meta:
        db_table = 'movies"."movies_genres_association'

    def __str__(self) -> str:
        return f"MovieID={self.movie_id}, GenreID={self.genre_id}"


class Movies(UUIDMixin, DatetimeStampedMixin, ActiveMixin):
    """Postgres модель - Фильм."""

    name_ru = models.CharField(
        max_length=256,
        null=False,
        unique=True,
        db_index=True,
    )
    name_eng = models.CharField(max_length=256, blank=True, unique=True)
    release_date = models.DateField(
        null=False,
        db_index=True,
        help_text="Дата релиза фильма",
    )
    rating = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        default=0.0,
        validators=[
            validators.MinValueValidator(0.0),
            validators.MaxValueValidator(10.0),
        ],
        db_index=True,
        help_text="Рейтинг фильма",
    )
    age_rating = models.SmallIntegerField(
        null=False,
        validators=[
            validators.MinValueValidator(0),
            validators.MaxValueValidator(18),
        ],
        db_index=True,
        help_text="Возрастной рейтинг фильма",
    )
    description = models.TextField(default="")

    persons = models.ManyToManyField(
        Persons,
        through="MoviesPersonsAssociation",
    )
    genres = models.ManyToManyField(
        Genres,
        through="MoviesGenresAssociation",
    )

    class Meta:
        db_table = 'movies"."movies'
        verbose_name = "Фильм"
        verbose_name_plural = "Фильмы"

    def clean(self) -> None:
        errors = dict()

        min_release_date = 1895
        if self.release_date and self.release_date.year < min_release_date:
            errors["release_date"] = exceptions.ValidationError(
                f"Дата создания первого фильма: {min_release_date}",
            )

        if self.rating > 0 and self.release_date is None:
            errors["rating"] = exceptions.ValidationError(
                "Фильм без даты релиза не может иметь рейтинг",
            )

        if errors:
            raise exceptions.ValidationError(errors)

    def __str__(self) -> str:
        return f"{self.name_ru}({self.name_eng if self.name_eng else "-"})"
