# Rest API

Para la API se utiliza [FastAPI][FastAPI], un framework web que
permite crear una APIs auto documentadas[^1] y documentadas
automaticamente[^2]. La estructura es similar a otros frameworks web
como Express:


=== "FastAPI"
    ```py
    from fastapi import FastAPI

    app = FastAPI()

    @app.get("/")
    def say_hello(name: str = "World") -> str:
        return f"Hello {name}"

    # uvicorn module:app --port 8080
    ```

=== "Express"
    ```js
    const express = require('express');

    const app = express();

    app.get('/', function(req, res){
        res.send(`Hello ${req.params.name || 'World'}!`)
    });

    // app.listen(8080);
    ```

[FastAPI]: https://fastapi.tiangolo.com/

[^1]: Que el código se entiende por si solo
[^2]: Que el código genera documentación automaticamente


## Referencia Rápida

### Auto documentación

Cada endpoint es **documentado automaticamente** en el formato
[OpenAPI][OpenAPI]. Se puede ver la documentación y probar cada
endpoint tanto en la interfaz de [Swagger UI][swagger-ui] en `/docs`
y en la interfaz de ReDoc en `/redoc`, en el servidor.

El nombre del endpoint es obtenido del nombre del nombre de la función,
su descripción de su docstring, los parámetros de los atributos con
las anotaciones de tipos, la categoria con el parámetro, el formato
de respuesta y su status code con los parámetro `tags`,
`response_model` y `status_code` respectivamente.

[OpenAPI]: https://spec.openapis.org/oas/latest.html
[swagger-ui]: https://swagger.io/tools/swagger-ui/
[ReDoc]: https://github.com/Redocly/redoc



### Dependencias

Las [dependencias] en FastAPI son procesos que ocurren ocurren
generalmente antes del proceso principal de la ruta. Estos pueden ser
usados para evitar repetir codigo en cada ruta. Un caso común es con
sesiones en la base de datos:

```py
def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.commit()
        db.close()


@app.get("/users/:user_id")
def user_by_id(user_id: int, db: Session = Depends(get_db)):
    return db.exec(select(User).where(User.id == user_id)).one()
```

[dependencias]: https://fastapi.tiangolo.com/tutorial/dependencies/
