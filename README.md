# Wingz Ride API

A RESTful API for managing ride information built with Django REST Framework.

## Setup

1. Create virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

4. Create admin user:
   ```bash
   python manage.py createsuperuser
   ```

5. Seed sample data:
   ```bash
   python manage.py seed_data
   python manage.py seed_24h_data  # Creates trips > 1 hour for report testing
   ```

6. Run server:
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Rides
- `GET /api/rides/` - List all rides (paginated)
- `POST /api/rides/` - Create a new ride
- `GET /api/rides/{id}/` - Get ride details
- `PUT /api/rides/{id}/` - Update a ride
- `DELETE /api/rides/{id}/` - Delete a ride

### Users
- `GET /api/users/` - List all users
- `POST /api/users/` - Create a new user
- `GET /api/users/{id}/` - Get user details

### Ride Events
- `GET /api/ride-events/` - List all ride events
- `POST /api/ride-events/` - Create a new event

### Reports
- `GET /api/reports/trip-duration/` - Trips > 1 hour by month/driver

### Filtering
- `?status=pickup` - Filter by status
- `?rider_email=test@example.com` - Filter by rider email

### Sorting
- `?ordering=pickup_time` - Sort by pickup time
- `?ordering=-pickup_time` - Sort by pickup time descending
- `?lat=37.77&lng=-122.41&sort_by=distance` - Sort by distance

## Raw SQL Report

```sql
SELECT 
    strftime('%Y-%m', pickup_event.created_at) as month,
    u.first_name || ' ' || u.last_name as driver,
    COUNT(*) as trip_count
FROM ride r
JOIN user u ON r.id_driver = u.id
JOIN ride_event pickup_event ON pickup_event.id_ride = r.id 
    AND pickup_event.description = 'Status changes to pickup'
JOIN ride_event dropoff_event ON dropoff_event.id_ride = r.id 
    AND dropoff_event.description = 'Status change to dropoff'
WHERE (
    strftime('%s', substr(replace(dropoff_event.created_at, 'T', ' '), 1, 19)) - 
    strftime('%s', substr(replace(pickup_event.created_at, 'T', ' '), 1, 19))
) > 3600
GROUP BY month, driver
ORDER BY month, driver;
```

Access via API: `GET /api/reports/trip-duration/`

## Running Tests

```bash
python manage.py test
```

Tests cover:
- Authentication requirements
- Admin role permissions
- Ride listing
- Trip duration report with controlled data