"""
routes/admin.py
Admin panel endpoints covering all 12 Milestone tables:
users, sellers, admins, inquiries, reviews, comparisons, favorites, search_logs.
"""
import hmac

from flask import Blueprint, jsonify, request
from config import get_db

try:
    import bcrypt
except ImportError:
    bcrypt = None

try:
    from werkzeug.security import check_password_hash
except ImportError:
    check_password_hash = None

admin_bp = Blueprint('admin', __name__)


def fetchall_dict(cur):
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def verify_password(stored_hash, password):
    if not stored_hash or not password:
        return False

    # Seed SQL documents Password123 but stores placeholder bcrypt strings.
    if 'sampleHashFor' in stored_hash:
        return hmac.compare_digest(password, 'Password123')

    if stored_hash.startswith(('$2a$', '$2b$', '$2y$')) and bcrypt:
        try:
            return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
        except ValueError:
            return False

    if check_password_hash:
        try:
            return check_password_hash(stored_hash, password)
        except ValueError:
            return False

    return False


def admin_permissions(row):
    permission_map = [
        ('Manage users', 'can_manage_users'),
        ('Manage listings', 'can_manage_listings'),
        ('View reports', 'can_view_reports'),
        ('Manage settings', 'can_manage_settings'),
    ]
    return [label for label, field in permission_map if row.get(field)]


@admin_bp.route('/login', methods=['POST'])
def admin_login():
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("""
            SELECT
                u.user_id, u.name, u.email, u.password_hash, u.role, u.is_active,
                a.admin_id, a.can_manage_users, a.can_manage_listings,
                a.can_view_reports, a.can_manage_settings
            FROM users u
            LEFT JOIN admins a ON u.user_id = a.user_id
            WHERE LOWER(u.email) = %s
            LIMIT 1
        """, (email,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return jsonify({"error": "Invalid email or password."}), 401

        admin = dict(zip([d[0] for d in cur.description], row))
        conn.close()

        if admin.get('role') != 'admin' or not admin.get('admin_id'):
            return jsonify({"error": "This account does not have admin access."}), 403
        if not admin.get('is_active'):
            return jsonify({"error": "This admin account is inactive."}), 403
        if not verify_password(admin.get('password_hash'), password):
            return jsonify({"error": "Invalid email or password."}), 401

        return jsonify({
            "admin": {
                "user_id": admin["user_id"],
                "admin_id": admin["admin_id"],
                "name": admin["name"],
                "email": admin["email"],
                "permissions": admin_permissions(admin),
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── GET /api/admin/stats ──────────────────────────────────────────
@admin_bp.route('/stats', methods=['GET'])
def admin_stats():
    """High-level table counts for admin dashboard."""
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("""
            SELECT
                (SELECT COUNT(*) FROM users)          AS total_users,
                (SELECT COUNT(*) FROM sellers)        AS total_sellers,
                (SELECT COUNT(*) FROM vehicles)       AS total_vehicles,
                (SELECT COUNT(*) FROM inquiries)      AS total_inquiries,
                (SELECT COUNT(*) FROM reviews)        AS total_reviews,
                (SELECT COUNT(*) FROM favorites)      AS total_favorites,
                (SELECT COUNT(*) FROM comparisons)    AS total_comparisons,
                (SELECT COUNT(*) FROM search_logs)    AS total_searches
        """)
        row  = cur.fetchone()
        data = dict(zip([d[0] for d in cur.description], row))
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── GET /api/admin/users ──────────────────────────────────────────
@admin_bp.route('/users', methods=['GET'])
def get_users():
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("""
            SELECT user_id, name, email, phone, role, is_active
            FROM users ORDER BY role, name
        """)
        data = fetchall_dict(cur)
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── GET /api/admin/sellers ────────────────────────────────────────
@admin_bp.route('/sellers', methods=['GET'])
def get_sellers():
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("""
            SELECT s.seller_id, u.name, u.email, u.phone,
                   s.business_name, s.seller_type, s.verified_status,
                   s.rating, l.city
            FROM sellers s
            JOIN users     u ON s.user_id     = u.user_id
            LEFT JOIN locations l ON s.location_id = l.location_id
            ORDER BY s.seller_id
        """)
        data = fetchall_dict(cur)
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── GET /api/admin/inquiries ──────────────────────────────────────
@admin_bp.route('/inquiries', methods=['GET'])
def get_inquiries():
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("""
            SELECT i.inquiry_id, i.message, i.status,
                   u.name  AS buyer_name,
                   v.brand, v.model, v.year,
                   s.business_name AS seller_name
            FROM inquiries i
            LEFT JOIN users   u ON i.user_id   = u.user_id
            JOIN vehicles v ON i.vehicle_id = v.vehicle_id
            JOIN sellers  s ON i.seller_id  = s.seller_id
            ORDER BY i.inquiry_id DESC
        """)
        data = fetchall_dict(cur)
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── PATCH /api/admin/inquiries/<id>/status ────────────────────────
@admin_bp.route('/inquiries/<int:inquiry_id>/status', methods=['PATCH'])
def update_inquiry_status(inquiry_id):
    data   = request.get_json() or {}
    status = data.get('status')
    if status not in ('new', 'read', 'replied', 'closed'):
        return jsonify({"error": "Invalid status value"}), 400
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("UPDATE inquiries SET status=%s WHERE inquiry_id=%s",
                    (status, inquiry_id))
        conn.commit()
        conn.close()
        return jsonify({"message": "Status updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── GET /api/admin/reviews ────────────────────────────────────────
@admin_bp.route('/reviews', methods=['GET'])
def get_reviews():
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("""
            SELECT r.review_id, r.rating, r.comment,
                   u.name AS reviewer_name,
                   s.business_name AS seller_name
            FROM reviews r
            JOIN users   u ON r.reviewer_id = u.user_id
            JOIN sellers s ON r.seller_id   = s.seller_id
            ORDER BY r.review_id DESC
        """)
        data = fetchall_dict(cur)
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── DELETE /api/admin/reviews/<id> ───────────────────────────────
@admin_bp.route('/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("DELETE FROM reviews WHERE review_id = %s", (review_id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Review deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── GET /api/admin/comparisons ────────────────────────────────────
@admin_bp.route('/comparisons', methods=['GET'])
def get_comparisons():
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("""
            SELECT c.comparison_id, u.name AS user_name,
                   CONCAT(v1.brand,' ',v1.model) AS vehicle_1,
                   CONCAT(v2.brand,' ',v2.model) AS vehicle_2,
                   CONCAT(v3.brand,' ',v3.model) AS vehicle_3
            FROM comparisons c
            JOIN users    u  ON c.user_id      = u.user_id
            JOIN vehicles v1 ON c.vehicle_id_1 = v1.vehicle_id
            JOIN vehicles v2 ON c.vehicle_id_2 = v2.vehicle_id
            LEFT JOIN vehicles v3 ON c.vehicle_id_3 = v3.vehicle_id
            ORDER BY c.comparison_id DESC
        """)
        data = fetchall_dict(cur)
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── GET /api/admin/favorites ──────────────────────────────────────
@admin_bp.route('/favorites', methods=['GET'])
def get_favorites():
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute("""
            SELECT f.favorite_id, u.name AS user_name,
                   v.brand, v.model, v.year, v.price
            FROM favorites f
            JOIN users    u ON f.user_id    = u.user_id
            JOIN vehicles v ON f.vehicle_id = v.vehicle_id
            ORDER BY f.favorite_id DESC LIMIT 100
        """)
        data = fetchall_dict(cur)
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── PATCH /api/admin/users/<id>/toggle ───────────────────────────
@admin_bp.route('/users/<int:user_id>/toggle', methods=['PATCH'])
def toggle_user(user_id):
    """Activate / deactivate a user account."""
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute(
            "UPDATE users SET is_active = 1 - is_active WHERE user_id = %s",
            (user_id,)
        )
        conn.commit()
        cur.execute("SELECT is_active FROM users WHERE user_id = %s", (user_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"user_id": user_id, "is_active": bool(row[0])})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
