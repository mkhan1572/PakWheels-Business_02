"""
routes/search.py
Full-text search across vehicles.
Logs every search to the search_logs table (Milestone schema).
"""
from flask import Blueprint, jsonify, request
from config import get_db

search_bp = Blueprint('search', __name__)


# ── GET /api/search?q=toyota&page=1&limit=20 ─────────────────────
@search_bp.route('', methods=['GET'])
def search():
    q     = (request.args.get('q') or '').strip()
    page  = max(1, int(request.args.get('page',  1)))
    limit = min(100, max(1, int(request.args.get('limit', 20))))
    offset = (page - 1) * limit

    if not q:
        return jsonify({"error": "Query parameter 'q' is required"}), 400

    like = f"%{q}%"
    try:
        conn = get_db()
        cur  = conn.cursor()

        # Count first
        cur.execute("""
            SELECT COUNT(*)
            FROM vehicles v
            LEFT JOIN locations l ON v.location_id = l.location_id
            WHERE v.brand LIKE %s OR v.model LIKE %s
               OR v.body_type LIKE %s OR l.city LIKE %s
        """, (like, like, like, like))
        total = cur.fetchone()[0]

        # Results
        cur.execute("""
            SELECT v.vehicle_id, v.brand, v.model, v.year, v.price,
                   v.mileage, v.fuel_type, v.transmission, v.body_type,
                   v.color, v.status, l.city
            FROM vehicles v
            LEFT JOIN locations l ON v.location_id = l.location_id
            WHERE v.brand LIKE %s OR v.model LIKE %s
               OR v.body_type LIKE %s OR l.city LIKE %s
            ORDER BY v.vehicle_id DESC
            LIMIT %s OFFSET %s
        """, (like, like, like, like, limit, offset))
        cols  = [d[0] for d in cur.description]
        items = [dict(zip(cols, r)) for r in cur.fetchall()]

        # Log the search (user_id = NULL for anonymous)
        user_id = request.args.get('user_id')
        cur.execute("""
            INSERT INTO search_logs (user_id, query_text, results_count)
            VALUES (%s, %s, %s)
        """, (int(user_id) if user_id else None, q, total))
        conn.commit()
        conn.close()

        return jsonify({"total": total, "page": page, "limit": limit, "data": items})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── GET /api/search/logs ──────────────────────────────────────────
@search_bp.route('/logs', methods=['GET'])
def search_logs():
    """Recent search log entries (admin use)."""
    limit = min(100, int(request.args.get('limit', 20)))
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("""
            SELECT sl.log_id, sl.query_text, sl.results_count,
                   sl.searched_at, u.name AS user_name
            FROM search_logs sl
            LEFT JOIN users u ON sl.user_id = u.user_id
            ORDER BY sl.searched_at DESC
            LIMIT %s
        """, (limit,))
        cols = [d[0] for d in cur.description]
        data = [dict(zip(cols, r)) for r in cur.fetchall()]
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
