"""
routes/filters.py
Returns distinct values for frontend filter dropdowns.
Uses Milestone schema column names (brand, mileage, location FK).
"""
from flask import Blueprint, jsonify, request
from config import get_db

filters_bp = Blueprint('filters', __name__)


def simple_list(cur):
    return [r[0] for r in cur.fetchall() if r[0]]


# ── GET /api/filters/makes ────────────────────────────────────────
@filters_bp.route('/makes', methods=['GET'])
def get_makes():
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("SELECT DISTINCT brand FROM vehicles ORDER BY brand")
        data = simple_list(cur)
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── GET /api/filters/models ───────────────────────────────────────
@filters_bp.route('/models', methods=['GET'])
def get_models():
    try:
        conn = get_db()
        cur  = conn.cursor()
        make = request.args.get('make') or request.args.get('brand')
        if make:
            cur.execute(
                "SELECT DISTINCT model FROM vehicles WHERE brand = %s ORDER BY model",
                (make,)
            )
        else:
            cur.execute("SELECT DISTINCT model FROM vehicles ORDER BY model")
        data = simple_list(cur)
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── GET /api/filters/cities ───────────────────────────────────────
@filters_bp.route('/cities', methods=['GET'])
def get_cities():
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("""
            SELECT DISTINCT l.city
            FROM vehicles v
            JOIN locations l ON v.location_id = l.location_id
            ORDER BY l.city
        """)
        data = simple_list(cur)
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── GET /api/filters/fuel-types ───────────────────────────────────
@filters_bp.route('/fuel-types', methods=['GET'])
def get_fuel_types():
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("SELECT DISTINCT fuel_type FROM vehicles ORDER BY fuel_type")
        data = simple_list(cur)
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── GET /api/filters/transmissions ────────────────────────────────
@filters_bp.route('/transmissions', methods=['GET'])
def get_transmissions():
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("SELECT DISTINCT transmission FROM vehicles ORDER BY transmission")
        data = simple_list(cur)
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── GET /api/filters/body-types ───────────────────────────────────
@filters_bp.route('/body-types', methods=['GET'])
def get_body_types():
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("SELECT DISTINCT body_type FROM vehicles ORDER BY body_type")
        data = simple_list(cur)
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── GET /api/filters/categories ───────────────────────────────────
@filters_bp.route('/categories', methods=['GET'])
def get_categories():
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("SELECT category_id, category_name FROM categories ORDER BY category_name")
        cols = [d[0] for d in cur.description]
        data = [dict(zip(cols, r)) for r in cur.fetchall()]
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── GET /api/filters/locations ────────────────────────────────────
@filters_bp.route('/locations', methods=['GET'])
def get_locations():
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("""
            SELECT location_id, city, state, country
            FROM locations ORDER BY state, city
        """)
        cols = [d[0] for d in cur.description]
        data = [dict(zip(cols, r)) for r in cur.fetchall()]
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
