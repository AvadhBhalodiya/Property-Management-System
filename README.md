# Property Management API

REST API for a property management system. Staff log in with JWT, create properties containing units,
register members, and assign a member to a unit under a contract.

Python 3.11, Django 5.2, Django REST Framework, PostgreSQL, Celery with Redis.

## Running it

```bash
./start.sh
```

Builds the image, starts postgres, redis, the API, a celery worker and celery beat, applies migrations and
seeds demo data. The API is on http://localhost:8000, log in with `staff@example.com` / `Staff@123`.

```bash
docker compose ps
docker compose logs -f web
docker compose down -v       # stop and drop the database
```

### Without Docker

Needs PostgreSQL and Redis on the host. Set `DB_HOST=localhost` and `REDIS_URL=redis://localhost:6379/0`
in `.env`, then:

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
createdb property_management
python manage.py migrate && python manage.py seed_demo_data && python manage.py runserver
celery -A config worker -l info        # separate terminal
celery -A config beat -l info          # separate terminal
```

## Configuration

Every value comes from `.env`, and `.env.example` is the template.

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` for local development |
| `ALLOWED_HOSTS` | comma separated host list |
| `TIME_ZONE` | used by Django and by celery beat schedules |
| `DB_NAME` `DB_USER` `DB_PASSWORD` `DB_HOST` `DB_PORT` | postgres connection |
| `ACCESS_TOKEN_LIFETIME_MINUTES` | access token lifetime, default 60 |
| `REFRESH_TOKEN_LIFETIME_DAYS` | refresh token lifetime, default 7 |
| `REDIS_URL` | celery broker |
| `SEED_DEMO_DATA` | seed demo rows on container start |

## Endpoints

Everything except register and login needs `Authorization: Bearer <access token>`. Paths have no trailing
slash. List endpoints are paginated 20 per page with `?page=`.

| Method | Path | Notes |
|---|---|---|
| POST | `/api/auth/register` | creates a staff user |
| POST | `/api/auth/login` | takes `email` and `password`, returns `access` and `refresh` |
| POST | `/api/auth/refresh` | new access token from a refresh token |
| POST | `/api/properties` | create a property |
| GET | `/api/properties` | list with `unit_count` |
| GET | `/api/properties/<property_id>` | property with its units nested |
| POST | `/api/properties/<property_id>/units` | add a unit |
| GET | `/api/units` | `?status=available` or `?status=occupied` |
| POST | `/api/members` | create a member |
| GET | `/api/members` | list members |
| POST | `/api/contracts` | `monthly_rent` is optional, defaults to the unit's rent |
| GET | `/api/contracts` | `?active=true` or `?active=false` |

`postman_collection.json` covers all of them. Import it and run Login first; the token is stored in a
collection variable the other requests use.

## Response format

```json
{
  "success": true,
  "message": "Contract created successfully",
  "data": { "id": 1, "monthly_rent": "30000.00", "total_value": "74516.13" }
}
```

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": { "unit": "This unit is already booked for the selected dates." }
}
```

List responses keep the paginator (`count`, `next`, `previous`, `results`) inside `data`.

## Business rules

- **Total contract value** is calculated on create and stored, so the agreed figure does not move if the
  unit's rent changes later. Whole months plus leftover days prorated over that month's real length. A
  lease from 01 Jan to 15 Mar at 30,000 is 74516.13; a full year is exactly twelve times the rent, whether
  or not it starts on the first.
- **Double-booking** returns a 400. Both ends count as occupied, so a lease ending 30 June conflicts with
  one starting 30 June. The check runs in a transaction with the unit row locked, so two simultaneous
  requests cannot both succeed.
- **Unit status** follows the contracts, and is set only while one is actually running — a lease signed
  today for next quarter does not remove the unit from `?status=available` now. A celery beat job reconciles
  it daily at 00:30; `python manage.py sync_unit_statuses` does the same on demand.
- **Active contracts** are derived from the dates rather than a stored flag, so they cannot go stale.
