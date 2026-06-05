# PakWheels Business Analytics

PakWheels Business Analytics is a Flask and MySQL project for managing and analyzing vehicle listings from a cleaned PakWheels dataset. It includes a normalized database schema, REST API routes, dashboard pages, listing management, search, comparison, and admin views.

## Project Highlights

- Flask backend with modular route files
- MySQL 8 database using a normalized relational schema
- SQL scripts for database creation, table creation, seed data, sample activity, and queries
- Frontend pages built with HTML templates, CSS, and JavaScript
- Dashboard analytics for vehicles, sellers, makes, cities, fuel types, prices, and trends
- Listing search, filters, detail pages, comparison page, and admin management endpoints
- Cleaned PakWheels dataset included in CSV format

## Technology Stack

| Layer | Tools |
| --- | --- |
| Backend | Python, Flask, Flask-CORS |
| Database | MySQL 8, mysqlclient |
| Frontend | HTML, CSS, JavaScript, Jinja templates |
| Configuration | python-dotenv |
| Dataset | CSV, pandas |
| Version Control | Git and GitHub |

## Repository Structure

```text
pakwheels_project/
|-- backend/
|   |-- app.py
|   |-- config.py
|   |-- requirements.txt
|   `-- routes/
|       |-- admin.py
|       |-- analytics.py
|       |-- filters.py
|       |-- listings.py
|       `-- search.py
|-- database/
|   `-- sql_files/
|       |-- 01_create_database.sql
|       |-- 02_create_tables.sql
|       |-- 03_insert_locations.sql
|       |-- 04_insert_categories.sql
|       |-- 05_insert_users.sql
|       |-- 06_insert_admins.sql
|       |-- 07_insert_sellers.sql
|       |-- 08_insert_vehicles.sql
|       |-- 09_insert_vehicle_images.sql
|       |-- 10_insert_sample_activity.sql
|       `-- 11_sample_queries.sql
|-- dataset/
|   `-- pakwheels_cleaned.csv
|-- frontend/
|   |-- static/
|   |   |-- main.js
|   |   `-- site.css
|   `-- templates/
|       |-- admin.html
|       |-- base.html
|       |-- compare.html
|       |-- dashboard.html
|       |-- listing_detail.html
|       `-- listings.html
`-- README.md
```

## Database Setup

1. Open MySQL Workbench or another MySQL client.
2. Run the SQL files in this exact order:

```text
database/sql_files/01_create_database.sql
database/sql_files/02_create_tables.sql
database/sql_files/03_insert_locations.sql
database/sql_files/04_insert_categories.sql
database/sql_files/05_insert_users.sql
database/sql_files/06_insert_admins.sql
database/sql_files/07_insert_sellers.sql
database/sql_files/08_insert_vehicles.sql
database/sql_files/09_insert_vehicle_images.sql
database/sql_files/10_insert_sample_activity.sql
```

3. Use `database/sql_files/11_sample_queries.sql` for testing and reporting queries.

The application expects the database name to be `pakwheels_db`.

## Backend Setup

Create a virtual environment and install dependencies:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env` from `.env.example` and update the values for your local MySQL server:

```env
DB_HOST=localhost
DB_USER=root
DB_PASS=your_mysql_password
DB_NAME=pakwheels_db
FLASK_DEBUG=true
```

Run the Flask application:

```bash
python app.py
```

The application runs at:

```text
http://localhost:5000
```

## Frontend Pages

| Page | URL | Purpose |
| --- | --- | --- |
| Dashboard | `/` | Vehicle market analytics overview |
| Listings | `/listings` | Browse and filter vehicle listings |
| Listing Detail | `/listing/<id>` | View one vehicle with details and images |
| Compare | `/compare` | Compare selected vehicles side by side |
| Admin | `/admin` | Manage users, sellers, inquiries, reviews, comparisons, and favorites |

## API Endpoints

### Core

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/health` | API health check |

### Listings

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/listings` | Get vehicle listings with filters and pagination |
| GET | `/api/listings/<id>` | Get one vehicle listing |
| POST | `/api/listings` | Create a vehicle listing |
| PUT | `/api/listings/<id>` | Update a vehicle listing |
| DELETE | `/api/listings/<id>` | Delete a vehicle listing |

### Analytics

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/analytics/overview` | Summary dashboard statistics |
| GET | `/api/analytics/trends` | Business trends and insights |
| GET | `/api/analytics/makes` | Listings by make |
| GET | `/api/analytics/cities` | Listings by city |
| GET | `/api/analytics/fuel-types` | Listings by fuel type |
| GET | `/api/analytics/body-types` | Listings by body type |
| GET | `/api/analytics/transmissions` | Listings by transmission |
| GET | `/api/analytics/price-distribution` | Price bucket distribution |
| GET | `/api/analytics/vehicle-age` | Vehicle age analysis |
| GET | `/api/analytics/models` | Listings by model |
| GET | `/api/analytics/top-makes` | Top vehicle makes |
| GET | `/api/analytics/sellers` | Seller performance summary |

### Filters and Search

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/filters/makes` | Make filter values |
| GET | `/api/filters/models` | Model filter values |
| GET | `/api/filters/cities` | City filter values |
| GET | `/api/filters/fuel-types` | Fuel type filter values |
| GET | `/api/filters/transmissions` | Transmission filter values |
| GET | `/api/filters/body-types` | Body type filter values |
| GET | `/api/filters/categories` | Category filter values |
| GET | `/api/filters/locations` | Location filter values |
| GET | `/api/search?q=toyota` | Search vehicle listings |
| GET | `/api/search/logs` | View recent search logs |

### Admin

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/api/admin/login` | Admin login |
| GET | `/api/admin/stats` | Table and system statistics |
| GET | `/api/admin/users` | View users |
| GET | `/api/admin/sellers` | View sellers |
| GET | `/api/admin/inquiries` | View inquiries |
| PATCH | `/api/admin/inquiries/<id>/status` | Update inquiry status |
| GET | `/api/admin/reviews` | View reviews |
| DELETE | `/api/admin/reviews/<id>` | Delete a review |
| GET | `/api/admin/comparisons` | View comparisons |
| GET | `/api/admin/favorites` | View favorites |
| PATCH | `/api/admin/users/<id>/toggle` | Activate or deactivate a user |

## Dataset

The dataset is stored at:

```text
dataset/pakwheels_cleaned.csv
```

It contains cleaned vehicle listing records used to populate and analyze the PakWheels-style marketplace database.

## Version Control

This project is maintained with Git and hosted on GitHub:

```text
https://github.com/mkhan1572/PakWheels-Business_02
```

The main branch contains the project source code, SQL files, dataset, frontend assets, and documentation. Local development artifacts such as virtual environments, cache files, editor settings, and private `.env` files are excluded through `.gitignore`.

## Author

Developed as a database and business analytics project for a PakWheels-style vehicle marketplace system.
