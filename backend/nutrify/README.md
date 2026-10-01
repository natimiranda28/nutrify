# Nutrify — backend

API REST para el MVP de la plataforma de alimentación inclusiva. Está hecha con
Django REST Framework y funciona con SQLite para desarrollo rápido o PostgreSQL
mediante Docker. La información alimentaria representa **declaraciones del
establecimiento**: no certifica que un producto sea médicamente seguro.

## Requisitos

- Python 3.12 o superior, para ejecutar el backend directamente.
- Docker Desktop, para levantar el backend y PostgreSQL juntos.

## Opción recomendada: Visual Studio Code + Docker

1. Abre la raíz del repositorio `nutrify` en VS Code.
2. En la terminal integrada, ejecuta `cd backend/nutrify` y luego
   `docker compose up --build`.
3. Cuando termine de iniciar, abre `http://localhost:8000/api/` o
   `http://localhost:8000/admin/`.
4. Para detener los servicios, usa `Ctrl+C` y luego `docker compose down`.

La configuración de Docker es solo para desarrollo local; reemplaza las claves
y contraseñas antes de cualquier despliegue.

## Opción local: SQLite

En una terminal de VS Code, desde la raíz del repositorio:

```bash
cd backend/nutrify
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

En Windows PowerShell, activa el entorno con
`.venv\Scripts\Activate.ps1`. El servidor queda disponible en
`http://127.0.0.1:8000/`. SQLite se crea automáticamente en `db.sqlite3`.

Desde `/admin/` puedes cargar restricciones, categorías, establecimientos,
productos y las compatibilidades **declaradas por cada comercio**. No se cargan
datos de ejemplo para no inventar información sobre productos o su seguridad.

## Endpoints

| Método | Ruta | Descripción |
| --- | --- | --- |
| `POST` | `/api/auth/register/` | Crear usuario y perfil |
| `POST` | `/api/auth/token/` | Obtener tokens JWT (`username`, `password`) |
| `POST` | `/api/auth/token/refresh/` | Renovar el token de acceso |
| `GET` | `/api/auth/me/` | Consultar el usuario autenticado |
| `GET`, `PUT`, `PATCH` | `/api/profile/` | Consultar o actualizar restricciones del perfil |
| `GET` | `/api/restrictions/` | Listar restricciones disponibles |
| `GET` | `/api/categories/` | Listar categorías |
| `GET` | `/api/establishments/` | Listar establecimientos |
| `GET` | `/api/establishments/{slug}/` | Ver un establecimiento y sus productos |
| `GET` | `/api/establishments/search/` | Buscar opciones compatibles |
| `GET`, `POST`, `DELETE` | `/api/favorites/` | Listar, crear o quitar favoritos (JWT) |

La búsqueda admite `q`, `category`, `restrictions`, `latitude`, `longitude` y
`radius_km`. Las restricciones pueden repetirse o enviarse separadas por coma.
Cuando se solicitan varias, cada producto devuelto debe tener declaradas todas.
Si se envían coordenadas, los resultados se ordenan por distancia; el radio
predeterminado es 10 km y el máximo es 100 km.

Ejemplo:

```text
GET /api/establishments/search/?q=helado&restrictions=diabetes&latitude=-34.6037&longitude=-58.3816&radius_km=5
```

Para endpoints autenticados, envía
`Authorization: Bearer <access_token>`. El perfil se actualiza con un arreglo
de IDs de restricciones, por ejemplo:

```json
{"restrictions": [1, 3]}
```

## Pruebas y chequeos

```bash
python manage.py test
python manage.py check
```
