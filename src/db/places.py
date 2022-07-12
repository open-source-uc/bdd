from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

# NOTE(benjavicente): para las ubicaciones se podria usar postgis,
#                     pero no hay un buen ORM para añadirlo a este esquema

# from geoalchemy2 import Geometry


class Campus(SQLModel, table=True):  # type: ignore  # noqa # type: ignore  # noqa
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    places: List["Place"] = Relationship()


class CategoryOfPlace(SQLModel, table=True):  # type: ignore  # noqa # type: ignore  # noqa
    category_id: Optional[int] = Field(
        default=None, foreign_key="placecategory.id", primary_key=True
    )
    place_id: Optional[int] = Field(default=None, foreign_key="place.id", primary_key=True)


class Place(SQLModel, table=True):  # type: ignore  # noqa # type: ignore  # noqa
    id: Optional[int] = Field(default=None, primary_key=True)
    lat: float
    lng: float
    # latLng: list = Field(sa_column=Column(Geometry("POINT")))
    # polygon: Optional[list] = Field(default=None, sa_column=Column(Geometry("POLYGON")))
    campus_id: Optional[int] = Field(default=None, foreign_key="campus.id")
    campus: Campus = Relationship(back_populates="places")
    name: str
    floor: Optional[int] = None
    notes: Optional[str] = None
    description: Optional[str] = None
    categories: List["PlaceCategory"] = Relationship(
        back_populates="places",
        link_model=CategoryOfPlace,
    )
    parent_id: Optional[int] = Field(default=None, foreign_key="place.id")
    parent: "Place" = Relationship(back_populates="child")
    child: "Place" = Relationship()


class PlaceCategory(SQLModel, table=True):  # type: ignore  # noqa # type: ignore  # noqa
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    places: list[Place] = Relationship(back_populates="categories", link_model=CategoryOfPlace)
