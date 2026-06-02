"""
routes/analytics.py
Dashboard analytics using the Milestone schema.
Column names: mileage (not mileage_km), brand (not make), seller_id FK.
"""
from flask import Blueprint, jsonify, request
from config import get_db

analytics_bp = Blueprint('analytics', __name__)


def fetchall_dict(cur):
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


# ── GET /api/analytics/overview ───────────────────────────────────
@analytics_bp.route('/overview', methods=['GET'])
def overview():
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("""
            SELECT
                COUNT(*)                        AS total_listings,
                ROUND(AVG(price), 2)            AS avg_price,
                MIN(price)                      AS min_price,
                MAX(price)                      AS max_price,
                ROUND(AVG(mileage), 0)          AS avg_mileage,
                ROUND(AVG(engine_cc), 0)        AS avg_engine_cc,
                COUNT(DISTINCT model)           AS total_models,
                COUNT(DISTINCT brand)           AS total_brands,
                SUM(price)                      AS total_market_value,
                COUNT(DISTINCT location_id)     AS distinct_locations
            FROM vehicles
        """)
        row   = cur.fetchone()
        stats = dict(zip([d[0] for d in cur.description], row))
        conn.close()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── GET /api/analytics/trends ─────────────────────────────────────
@analytics_bp.route('/trends', methods=['GET'])
def trends():
    try:
        conn = get_db()
        cur  = conn.cursor()

        cur.execute("""
            SELECT transmission, COUNT(*), AVG(price)
            FROM vehicles GROUP BY transmission
        """)
        trans_data = {r[0]: {"count": r[1], "avg_price": float(r[2] or 0)}
                      for r in cur.fetchall()}

        premium_pct = 0
        if "Automatic" in trans_data and "Manual" in trans_data:
            auto_avg   = trans_data["Automatic"]["avg_price"]
            manual_avg = trans_data["Manual"]["avg_price"]
            if manual_avg > 0:
                premium_pct = round(((auto_avg - manual_avg) / manual_avg) * 100, 1)

        cur.execute("""
            SELECT brand, COUNT(*) * 100.0 / (SELECT COUNT(*) FROM vehicles) AS pct
            FROM vehicles GROUP BY brand ORDER BY COUNT(*) DESC LIMIT 1
        """)
        r = cur.fetchone()
        make_dom = {"make": r[0], "percentage": round(float(r[1] or 0), 1)} if r else None

        cur.execute("""
            SELECT l.city, AVG(v.price) AS avg_p, COUNT(*) AS cnt
            FROM vehicles v
            JOIN locations l ON v.location_id = l.location_id
            GROUP BY l.city HAVING cnt >= 3
            ORDER BY avg_p DESC LIMIT 1
        """)
        r = cur.fetchone()
        high_city = {"city": r[0], "avg_price": float(r[1] or 0)} if r else None

        conn.close()
        return jsonify({
            "transmission_split":  trans_data,
            "auto_premium_pct":    premium_pct,
            "dominant_make":       make_dom,
            "high_pricing_city":   high_city,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── GET /api/analytics/makes ──────────────────────────────────────
@analytics_bp.route('/makes', methods=['GET'])
def makes_analytics():
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("""
            SELECT brand AS category, COUNT(*) AS total_listings,
                   ROUND(AVG(price), 2) AS avg_price,
                   MIN(price) AS min_price, MAX(price) AS max_price
            FROM vehicles GROUP BY brand ORDER BY total_listings DESC
        """)
        data = fetchall_dict(cur)
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── GET /api/analytics/cities ─────────────────────────────────────
@analytics_bp.route('/cities', methods=['GET'])
def cities_analytics():
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("""
            SELECT l.city AS city_name, COUNT(*) AS total_listings,
                   ROUND(AVG(v.price), 2) AS avg_price
            FROM vehicles v
            JOIN locations l ON v.location_id = l.location_id
            GROUP BY l.city ORDER BY total_listings DESC LIMIT 20
        """)
        data = fetchall_dict(cur)
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── GET /api/analytics/fuel-types ─────────────────────────────────
@analytics_bp.route('/fuel-types', methods=['GET'])
def fuel_analytics():
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("""
            SELECT fuel_type AS category, COUNT(*) AS total_listings,
                   ROUND(AVG(price), 2) AS avg_price
            FROM vehicles GROUP BY fuel_type ORDER BY total_listings DESC
        """)
        data = fetchall_dict(cur)
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── GET /api/analytics/body-types ─────────────────────────────────
@analytics_bp.route('/body-types', methods=['GET'])
def body_type_analytics():
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("""
            SELECT body_type AS category, COUNT(*) AS total_listings,
                   ROUND(AVG(price), 2) AS avg_price
            FROM vehicles GROUP BY body_type ORDER BY total_listings DESC
        """)
        data = fetchall_dict(cur)
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── GET /api/analytics/transmissions ──────────────────────────────
@analytics_bp.route('/transmissions', methods=['GET'])
def transmission_analytics():
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("""
            SELECT transmission AS category, COUNT(*) AS total_listings,
                   ROUND(AVG(price), 2) AS avg_price
            FROM vehicles GROUP BY transmission ORDER BY total_listings DESC
        """)
        data = fetchall_dict(cur)
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── GET /api/analytics/price-distribution ─────────────────────────
@analytics_bp.route('/price-distribution', methods=['GET'])
def price_distribution():
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("""
            SELECT
                CASE
                    WHEN price < 500000    THEN 'Below 500K'
                    WHEN price < 1000000   THEN '500K-1M'
                    WHEN price < 2000000   THEN '1M-2M'
                    WHEN price < 4000000   THEN '2M-4M'
                    ELSE '4M+'
                END AS range_label,
                COUNT(*) AS listings,
                ROUND(AVG(price), 2) AS avg_price
            FROM vehicles
            GROUP BY range_label ORDER BY MIN(price)
        """)
        data = fetchall_dict(cur)
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── GET /api/analytics/vehicle-age ────────────────────────────────
@analytics_bp.route('/vehicle-age', methods=['GET'])
def vehicle_age():
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("""
            SELECT year AS category, COUNT(*) AS total_listings,
                   ROUND(AVG(price), 2) AS avg_price,
                   ROUND(AVG(mileage), 0) AS avg_mileage
            FROM vehicles
            WHERE year > 1980
            GROUP BY year ORDER BY year DESC LIMIT 20
        """)
        data = fetchall_dict(cur)
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── GET /api/analytics/models ─────────────────────────────────────
@analytics_bp.route('/models', methods=['GET'])
def model_performance():
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("""
            SELECT model AS category, COUNT(*) AS listings,
                   ROUND(AVG(price), 2) AS avg_price,
                   ROUND(AVG(mileage), 0) AS avg_mileage
            FROM vehicles GROUP BY model ORDER BY listings DESC LIMIT 50
        """)
        data = fetchall_dict(cur)
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── GET /api/analytics/top-makes ──────────────────────────────────
@analytics_bp.route('/top-makes', methods=['GET'])
def top_makes():
    limit = min(20, int(request.args.get('limit', 5)))
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("""
            SELECT brand AS make_name, COUNT(*) AS count
            FROM vehicles GROUP BY brand ORDER BY count DESC LIMIT %s
        """, (limit,))
        data = fetchall_dict(cur)
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── GET /api/analytics/sellers ────────────────────────────────────
@analytics_bp.route('/sellers', methods=['GET'])
def seller_analytics():
    """Top sellers by number of listings and average price."""
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("""
            SELECT s.seller_id, s.business_name, s.seller_type,
                   s.verified_status, s.rating,
                   COUNT(v.vehicle_id)      AS total_listings,
                   ROUND(AVG(v.price), 2)   AS avg_price
            FROM sellers s
            LEFT JOIN vehicles v ON s.seller_id = v.seller_id
            GROUP BY s.seller_id
            ORDER BY total_listings DESC
            LIMIT 20
        """)
        data = fetchall_dict(cur)
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
