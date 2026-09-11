# Property Management API

REST API for a property management system. Staff users register and log in with JWT, create properties
containing units, register members (tenants), and assign a member to a unit under a contract. The system
calculates the total contract value, blocks double-booking a unit for overlapping dates, and keeps unit
status in sync with the contracts running against it.

Python 3.11, Django 5.2, Django REST Framework, PostgreSQL, Celery with Redis.

## Running it

Docker is the quickest way. Nothing else needs to be installed.

```bash
./start.sh
```

That copies `.env.example` to `.env` if you do not have one, builds the image, starts postgres, redis, the
API, a celery worker and celery beat, applies migrations and seeds demo data. The API is then on
http://localhost:8000 and you can log in with:

```
staff@example.com / Staff@123
```

Useful afterwards:

```bash
docker compose ps
docker compose logs -f web
docker compose logs -f celery_worker
docker compose down          # stop
docker compose down -v       # stop and drop the database
```

### Running without Docker

You need PostgreSQL and Redis on the host.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# set DB_HOST=localhost and REDIS_URL=redis://localhost:6379/0
createdb property_management

python manage.py migrate
python manage.py seed_demo_data
python manage.py runserver
```

Celery, in two more terminals:

```bash
celery -A config worker -l info
celery -A config beat -l info
```

## Configuration

Every value comes from `.env`. `.env.example` is the template.

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

Every endpoint except register and login needs `Authorization: Bearer <access token>`.

| Method | Path | Notes |
|---|---|---|
| POST | `/api/auth/register` | creates a staff user, returns the user |
| POST | `/api/auth/login` | takes `email` and `password`, returns `access` and `refresh` |
| POST | `/api/auth/refresh` | exchanges a refresh token for a new access token |
| POST | `/api/properties` | create a property |
| GET | `/api/properties` | list properties with `unit_count` |
| GET | `/api/properties/<property_id>` | property with its units nested |
| POST | `/api/properties/<property_id>/units` | add a unit to a property |
| GET | `/api/units` | list units, `?status=available` or `?status=occupied` |
| POST | `/api/members` | create a member |
| GET | `/api/members` | list members |
| POST | `/api/contracts` | create a contract |
| GET | `/api/contracts` | list contracts, `?active=true` or `?active=false` |

Paths have no trailing slash, matching the specification. List endpoints are paginated 20 per page with
`?page=`.

`postman_collection.json` covers all of them. Import it, run **Login** first and the access token is stored
in a collection variable that every other request uses.

### Response format

Successful responses:

```json
{
  "success": true,
  "message": "Contract created successfully",
  "data": { "id": 1, "total_value": "74516.13" }
}
```

Failures:

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": { "end_date": ["End date must be after start date."] }
}
```

List responses keep the DRF paginator inside `data`:

```json
{
  "success": true,
  "message": "Contracts fetched successfully",
  "data": {
    "count": 12,
    "next": "http://localhost:8000/api/contracts?page=2",
    "previous": null,
    "results": []
  }
}
```

### Example

```bash
TOKEN=$(curl -s -X POST localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"staff@example.com","password":"Staff@123"}' \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["data"]["access"])')

curl -s -X POST localhost:8000/api/contracts \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"unit":1,"member":1,"start_date":"2026-01-01","end_date":"2026-03-15","monthly_rent":"30000.00"}'
```

## Layout

```
config/           settings, root urls, api urls, celery app
apps/common/      abstract timestamp model, response renderer, exception handler, seed command
apps/users/       custom user model, registration, login
apps/properties/  properties and units
apps/members/     tenants
apps/contracts/   contracts, contract rules, celery task
```

Each app keeps models, serializers, services, views and urls separate. Serializers validate the shape of a
request, services hold the business rules and own the transaction, and views stay thin. A serializer's
`create()` is a single call into a service.

## How the main rules work

**Total contract value** is calculated in `apps/contracts/services.py` and stored on the contract, so the
figure agreed at signing does not move if the unit's rent changes later. Whole months are counted with
`relativedelta(end_date + 1 day, start_date)` and any leftover days are prorated over the real number of
days in that month. The extra day matters: a lease from 15 Jan 2026 to 14 Jan 2027 is twelve months, and
without it the calculation returns eleven months and thirty days. At 30,000 a month:

| Period | Total |
|---|---|
| 01 Jan to 31 Dec | 360000.00 |
| 15 Jan 2026 to 14 Jan 2027 | 360000.00 |
| 01 Jan to 15 Mar | 74516.13 |

**Double-booking** is blocked by `has_overlapping_contract`, which treats both ends as inclusive
(`start_date <= new end` and `end_date >= new start`), so a contract ending 30 June conflicts with one
starting 30 June. The check runs inside `transaction.atomic()` after `select_for_update()` on the unit row,
so two requests arriving at the same time for the same unit cannot both pass it.

**Unit status** is a projection of contract state, not the source of truth. Creating a contract calls
`refresh_unit_status`, which marks the unit occupied only if a contract is active *today*, so a lease signed
now for next quarter does not make the unit disappear from `?status=available` for three months. A daily
celery beat job runs `sync_unit_statuses` at 00:30 in `TIME_ZONE` to release units whose contracts have
ended and occupy units whose contracts have just started. The same logic is available on demand:

```bash
docker compose exec web python manage.py sync_unit_statuses
```

**Active contracts** are derived from dates through `Contract.objects.active()` rather than a stored status
column, which cannot drift. `?active=false` returns contracts that are not currently running, past or future.

## Notes

- Contracts reference units, members and users with `PROTECT`. A contract is a financial record and should
  not disappear because something it points at was deleted.
- `monthly_rent` may be omitted when creating a contract and falls back to the unit's rent.
- Money is `Decimal` everywhere and DRF serializes it as a string, so `"32000.00"` rather than `32000.0`.
- List endpoints run a constant number of queries regardless of page size, using `select_related` on
  contracts and units and an annotated count on properties.
- Registration is open because the specification describes staff registering themselves. In a real
  deployment it would sit behind an invite or an admin-only endpoint.
