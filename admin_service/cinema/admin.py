from django import forms
from django.contrib import admin

from .models import (
    Genres,
    Movies,
    MoviesGenresAssociation,
    MoviesPersonsAssociation,
    Persons,
)


class MoviesPersonsAssociationForm(forms.ModelForm):
    class Meta:
        model = MoviesPersonsAssociation
        fields = "__all__"
        widgets = {"person_id": forms.Select(attrs={"class": "select2"})}


class MoviesPersonsAssociationInline(admin.TabularInline):
    model = MoviesPersonsAssociation
    form = MoviesPersonsAssociationForm
    extra = 1
    autocomplete_fields = ["person_id"]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "person_id":
            kwargs["queryset"] = Persons.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class MoviesGenresAssociationForm(forms.ModelForm):
    class Meta:
        model = MoviesGenresAssociation
        fields = "__all__"
        widgets = {"genre_id": forms.Select(attrs={"class": "select2"})}


class MoviesGenresAssociationInline(admin.TabularInline):
    model = MoviesGenresAssociation
    form = MoviesGenresAssociationForm
    extra = 1
    autocomplete_fields = ["genre_id"]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "genre_id":
            kwargs["queryset"] = Genres.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Movies)
class MoviesAdmin(admin.ModelAdmin):
    inlines = [MoviesPersonsAssociationInline, MoviesGenresAssociationInline]


@admin.register(Persons)
class PersonsAdmin(admin.ModelAdmin):
    search_fields = ["first_name", "second_name", "last_name"]


@admin.register(Genres)
class GenresAdmin(admin.ModelAdmin):
    search_fields = ["title"]
