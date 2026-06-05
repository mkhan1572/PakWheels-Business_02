"""
routes/listings.py
GET/POST/PUT/DELETE for vehicle listings.
Uses the Milestone schema: vehicles table with FK to sellers, locations, categories.
"""
from flask import Blueprint, jsonify, request
from config import get_db

listings_bp = Blueprint('listings', __name__)


def rows_to_list(cur, rows):
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in rows]


def row_to_dict(cur, row):
    cols = [d[0] for d in cur.description]
    return dict(zip(cols, row))


# Full SELECT that joins vehicles → sellers → locations → vehicle_images
_BASE_SELECT = """
    SELECT
        v.vehicle_id,
        v.brand,
        v.model,
        v.year,
        v.price,
        v.mileage,
        v.fuel_type,
        v.transmission,
        v.body_type,
        v.engine_cc,
        v.color,
        v.status,
        c.category_name,
        s.seller_id,
        s.business_name  AS seller_name,
        s.seller_type,
        s.verified_status,
        s.rating         AS seller_rating,
        l.city,
        l.state,
        l.country,
        (SELECT image_url FROM vehicle_images vi
         WHERE vi.vehicle_id = v.vehicle_id AND vi.is_primary = 1
         LIMIT 1)        AS image_url
    FROM vehicles v
    LEFT JOIN sellers   s ON v.seller_id   = s.seller_id
    LEFT JOIN locations l ON v.location_id = l.location_id
    LEFT JOIN categories c ON v.category_id = c.category_id
"""


# ── GET /api/listings ─────────────────────────────────────────────
@listings_bp.route('', methods=['GET'])
def get_listings():
    p = request.args
    page  = max(1, int(p.get('page',  1)))
    limit = min(100, max(1, int(p.get('limit', 20))))
    offset = (page - 1) * limit

    where, params = [], []

    if p.get('brand'):
        where.append("v.brand = %s"); params.append(p['brand'])
    if p.get('make'):                          # alias
        where.append("v.brand = %s"); params.append(p['make'])
    if p.get('model'):
        where.append("v.model = %s"); params.append(p['model'])
    if p.get('city'):
        where.append("l.city = %s"); params.append(p['city'])
    if p.get('fuel_type') or p.get('fuel'):
        where.append("v.fuel_type = %s"); params.append(p.get('fuel_type') or p.get('fuel'))
    if p.get('transmission'):
        where.append("v.transmission = %s"); params.append(p['transmission'])
    if p.get('body_type'):
        where.append("v.body_type = %s"); params.append(p['body_type'])
    if p.get('status'):
        where.append("v.status = %s"); params.append(p['status'])
    if p.get('year_min'):
        where.append("v.year >= %s"); params.append(int(p['year_min']))
    if p.get('year_max'):
        where.append("v.year <= %s"); params.append(int(p['year_max']))
    if p.get('price_min'):
        where.append("v.price >= %s"); params.append(float(p['price_min']))
    if p.get('price_max'):
        where.append("v.price <= %s"); params.append(float(p['price_max']))
    if p.get('engine_min'):
        where.append("v.engine_cc >= %s"); params.append(int(p['engine_min']))
    if p.get('engine_max'):
        where.append("v.engine_cc <= %s"); params.append(int(p['engine_max']))
    if p.get('mileage_max'):
        where.append("v.mileage <= %s"); params.append(int(p['mileage_max']))
    if p.get('search'):
        where.append("(v.brand LIKE %s OR v.model LIKE %s OR s.business_name LIKE %s)")
        params += [f"%{p['search']}%"] * 3

    where_sql = "WHERE " + " AND ".join(where) if where else ""

    sort_map = {
        'price_desc':   'v.price DESC',
        'price_asc':    'v.price ASC',
        'year_desc':    'v.year DESC',
        'year_asc':     'v.year ASC',
        'mileage_asc':  'v.mileage ASC',
        'mileage_desc': 'v.mileage DESC',
        'recent':       'v.vehicle_id DESC',
    }
    order_by = sort_map.get(p.get('sort', 'recent'), 'v.vehicle_id DESC')

    count_sql = f"""
        SELECT COUNT(*) FROM vehicles v
        LEFT JOIN sellers   s ON v.seller_id   = s.seller_id
        LEFT JOIN locations l ON v.location_id = l.location_id
        {where_sql}
    """
    list_sql = f"{_BASE_SELECT} {where_sql} ORDER BY {order_by} LIMIT %s OFFSET %s"

    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute(count_sql, params)
        total = cur.fetchone()[0]
        cur.execute(list_sql, params + [limit, offset])
        items = rows_to_list(cur, cur.fetchall())
        conn.close()
        return jsonify({"total": total, "page": page, "limit": limit, "data": items})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── GET /api/listings/<id> ────────────────────────────────────────
@listings_bp.route('/<int:vehicle_id>', methods=['GET'])
def get_listing(vehicle_id):
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute(f"{_BASE_SELECT} WHERE v.vehicle_id = %s", (vehicle_id,))
        row  = cur.fetchone()
        if not row:
            conn.close()
            return jsonify({"error": "Listing not found"}), 404

        data = row_to_dict(cur, row)

        # Attach all images for the detail page
        cur.execute(
            "SELECT image_id, image_url, is_primary FROM vehicle_images WHERE vehicle_id = %s",
            (vehicle_id,)
        )
        data['images'] = [
            {"image_id": r[0], "image_url": r[1], "is_primary": bool(r[2])}
            for r in cur.fetchall()
        ]
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── POST /api/listings ────────────────────────────────────────────
@listings_bp.route('', methods=['POST'])
def create_listing():
    data   = request.get_json() or {}
    errors = []

    required = ['brand', 'model', 'fuel_type', 'transmission', 'body_type', 'seller_id']
    for f in required:
        if not data.get(f):
            errors.append(f"Field '{f}' is required.")

    try:
        price = int(data.get('price', 0))
        if price <= 0:
            errors.append("price must be > 0.")
    except (ValueError, TypeError):
        errors.append("price must be an integer.")

    try:
        year = int(data.get('year', 0))
        if year < 1981 or year > 2030:
            errors.append("year must be between 1981 and 2030.")
    except (ValueError, TypeError):
        errors.append("year must be an integer.")

    if errors:
        return jsonify({"errors": errors}), 400

    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("""
            INSERT INTO vehicles
                (brand, model, year, price, mileage, fuel_type, transmission,
                 body_type, engine_cc, color, status, category_id, seller_id, location_id)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            data['brand'], data['model'], year, price,
            int(data.get('mileage', 0)),
            data['fuel_type'], data['transmission'], data['body_type'],
            int(data['engine_cc']) if data.get('engine_cc') else None,
            data.get('color'),
            data.get('status', 'available'),
            int(data['category_id']) if data.get('category_id') else None,
            int(data['seller_id']),
            int(data['location_id']) if data.get('location_id') else None,
        ))
        new_id = cur.lastrowid
        conn.commit()
        conn.close()
        return jsonify({"message": "Listing created", "vehicle_id": new_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── PUT /api/listings/<id> ────────────────────────────────────────
@listings_bp.route('/<int:vehicle_id>', methods=['PUT'])
def update_listing(vehicle_id):
    data   = request.get_json() or {}
    errors = []

    required = ['brand', 'model', 'fuel_type', 'transmission', 'body_type']
    for f in required:
        if not data.get(f):
            errors.append(f"Field '{f}' is required.")

    try:
        price = int(data.get('price', 0))
        if price <= 0:
            errors.append("price must be > 0.")
    except (ValueError, TypeError):
        errors.append("price must be an integer.")

    if errors:
        return jsonify({"errors": errors}), 400

    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("SELECT 1 FROM vehicles WHERE vehicle_id = %s", (vehicle_id,))
        if not cur.fetchone():
            conn.close()
            return jsonify({"error": "Listing not found"}), 404

        cur.execute("""
            UPDATE vehicles SET
                brand=%s, model=%s, year=%s, price=%s, mileage=%s,
                fuel_type=%s, transmission=%s, body_type=%s,
                engine_cc=%s, color=%s, status=%s,
                category_id=%s, seller_id=%s, location_id=%s
            WHERE vehicle_id=%s
        """, (
            data['brand'], data['model'],
            int(data.get('year', 2000)),
            price,
            int(data.get('mileage', 0)),
            data['fuel_type'], data['transmission'], data['body_type'],
            int(data['engine_cc']) if data.get('engine_cc') else None,
            data.get('color'),
            data.get('status', 'available'),
            int(data['category_id']) if data.get('category_id') else None,
            int(data['seller_id']) if data.get('seller_id') else None,
            int(data['location_id']) if data.get('location_id') else None,
            vehicle_id,
        ))
        conn.commit()
        conn.close()
        return jsonify({"message": "Listing updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── DELETE /api/listings/<id> ─────────────────────────────────────
@listings_bp.route('/<int:vehicle_id>', methods=['DELETE'])
def delete_listing(vehicle_id):
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("SELECT 1 FROM vehicles WHERE vehicle_id = %s", (vehicle_id,))
        if not cur.fetchone():
            conn.close()
            return jsonify({"error": "Listing not found"}), 404
        cur.execute("DELETE FROM vehicles WHERE vehicle_id = %s", (vehicle_id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Listing deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
