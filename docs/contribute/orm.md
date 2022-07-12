# Modelos

En ese proyecto se utiliza [SQLModel][SQLModel] para la definición de
modelos (tablas) y las consultas de la base de datos. Es un wrapper de
[SQLAlchemy][SQLAlchemy], un ORM popular de python.

SQLModel combina la simplicidad de `@dataclass` con el poder de
SQLAlchemy:


=== "SQLModel"
    ```python
    from datetime import datetime
    from typing import Optional

    from sqlmodel import SQLModel, Field, Relationship


    class Wizard(SQLModel, table=True): # type: ignore  # noqa
        id: Optional[int] = Field(default=None, primary_key=True)
        name: str
        level: int = 0
        created_at: datetime = Field(default_factory=datetime.now)

    wizard = Wizard(name="🧙‍")
    ```

=== "Data Classes"
    ```python
    from datetime import datetime
    from typing import Optional

    from dataclasses import dataclass, field

    @dataclass
    class Wizard:
        name: str # Fields without a default value must appear fist
        id: Optional[int] = None
        level: int = 0
        created_at: datetime = field(default_factory=datetime.now)

    wizard = Wizard(name="🧙‍♂️")
    ```

!!! danger "Importante"
    SQLModel fue lanzada el 24 de Agosto del 2021, y todavia no alcanza
    una versión estable, por lo que la API puede cambiar drasticamente
    y hay métodos que no tienen anotación de tipos.

En varios casos, uno puede interactuar con SQLAlchemy directamente,
como por ejemplo, en `Relations` se puede usar `sa_relationship_kwargs`:

```python hl_lines="4"
class Wand(SQLModel, table=True): # type: ignore  # noqa
    id: Optional[int] = Field(primary_key=True, default=None)
    wizard_id: int = Field(foreign_key="wizard.id", default=None)
    wizard: Wizard = Relationship(sa_relationship_kwargs=dict(lazy="joined"))

wand = Wand()
wand.wizard = wizard
```

*[ORM]: Object-Relational mapping

[SQLModel]: https://sqlmodel.tiangolo.com/
[SQLAlchemy]: https://www.sqlalchemy.org/
