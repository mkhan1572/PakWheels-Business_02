# PakWheels_Inventory_Intelligence
**pakwheels_db · MySQL 8 · Flask REST API · HTML/JS Frontend**
Milestone 1–5 | Institute of Management Sciences, Peshawar

---

## Project Structure

```
pakwheels_project/
├── database/
│   ├── setup_pakwheels_db.sql   ← RUN THIS FIRST in MySQL Workbench
│   └── sql_files/               ← Individual milestone SQL files (reference)
├── backend/
│   ├── .env                     ← DB credentials (edit DB_PASS)
│   ├── app.py                   ← Flask entry point
│   ├── config.py                ← MySQL connection
│   ├── requirements.txt
│   └── routes/
│       ├── listings.py          ← CRUD for vehicles
│       ├── analytics.py         ← Dashboard analytics
│       ├── filters.py           ← Dropdown filter values
│       ├── search.py            ← Full-text search + search_logs
│       └── admin.py             ← Admin panel (all 12 tables)
├── frontend/
│   ├── static/
│   │   ├── main.js
│   │   └── site.css
│   └── templates/
│       ├── base.html
│       ├── dashboard.html
│       ├── listings.html
│       ├── listing_detail.html
│       ├── compare.html
│       └── admin.html
└── dataset/
    └── pakwheels_cleaned.csv    ← 497 real PakWheels records
```

---

## Database Setup (MySQL Workbench)

1. Open **MySQL Workbench** and connect to your local server.
2. Go to **File → Open SQL Script** and select:
   `database/setup_pakwheels_db.sql`
3. Click **Execute** (⚡ lightning bolt, or `Ctrl+Shift+Enter`).
4. Refresh the **Schemas** panel — you should see `pakwheels_db` with 12 tables.

### Tables created (Milestone 1 & 4 — 3NF schema)
| # | Table | Purpose |
|---|-------|---------|
| 1 | `locations` | 45 Pakistani cities |
| 2 | `categories` | Cars / Vans / Trucks / Bikes |
| 3 | `users` | Admin, seller, buyer accounts |
| 4 | `admins` | Permission flags for admin users |
| 5 | `sellers` | Seller profiles (1:1 with users) |
| 6 | `vehicles` | Core listing table (497 records) |
| 7 | `vehicle_images` | Image URLs per listing |
| 8 | `favorites` | Buyer wishlists |
| 9 | `comparisons` | Side-by-side vehicle comparisons |
| 10 | `inquiries` | Buyer → seller messages |
| 11 | `reviews` | Star ratings for sellers |
| 12 | `search_logs` | Analytics: every search query |

---

## Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Edit .env if your MySQL password differs:
# DB_PASS=your_password_here

python app.py
# → Running on http://localhost:5000
```

---

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/listings` | All listings (filters + pagination) |
| GET | `/api/listings/<id>` | Single listing with images |
| POST | `/api/listings` | Create listing |
| PUT | `/api/listings/<id>` | Update listing |
| DELETE | `/api/listings/<id>` | Delete listing |
| GET | `/api/analytics/overview` | Summary stats |
| GET | `/api/analytics/makes` | By brand |
| GET | `/api/analytics/cities` | By city (via locations FK) |
| GET | `/api/analytics/fuel-types` | By fuel type |
| GET | `/api/analytics/body-types` | By body type |
| GET | `/api/analytics/transmissions` | By transmission |
| GET | `/api/analytics/price-distribution` | Price buckets |
| GET | `/api/analytics/vehicle-age` | By model year |
| GET | `/api/analytics/top-makes` | Top N brands |
| GET | `/api/analytics/sellers` | Seller leaderboard |
| GET | `/api/analytics/trends` | Business insights |
| GET | `/api/filters/makes` | Dropdown options |
| GET | `/api/filters/cities` | Dropdown options |
| GET | `/api/filters/fuel-types` | Dropdown options |
| GET | `/api/filters/body-types` | Dropdown options |
| GET | `/api/filters/categories` | Dropdown options |
| GET | `/api/filters/locations` | All 45 locations |
| GET | `/api/search?q=toyota` | Full-text search |
| GET | `/api/search/logs` | Recent searches |
| GET | `/api/admin/stats` | Table counts |
| GET | `/api/admin/users` | All users |
| GET | `/api/admin/sellers` | All sellers |
| GET | `/api/admin/inquiries` | All inquiries |
| PATCH | `/api/admin/inquiries/<id>/status` | Update status |
| GET | `/api/admin/reviews` | All reviews |
| DELETE | `/api/admin/reviews/<id>` | Delete review |
| GET | `/api/admin/comparisons` | All comparisons |
| GET | `/api/admin/favorites` | All favorites |
| PATCH | `/api/admin/users/<id>/toggle` | Activate/deactivate user |

---

## Milestones Reference

| Milestone | Document | Content |
|-----------|----------|---------|
| 1 | `Milestone1_ERD_v302.pdf` | ERD + Relational Schema (12 tables) |
| 2 | `Milestone2_Final.pdf` | Normalization (1NF → 3NF) |
| 3 | `Milestone3_Report_01.pdf` | Dataset preprocessing & dataflow |
| 4 | `Milestone4_DDL.pdf` | CREATE TABLE DDL statements |
| 5 | `Milestone5_DML.pdf` | INSERT / UPDATE / DELETE + validation |
# PakWheels_Inventory_Intelligence
