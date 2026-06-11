from flask import Blueprint, request

from ..database import get_connection, rows_to_dicts

spaces_bp = Blueprint("spaces", __name__)


@spaces_bp.get("/", strict_slashes=False)
def list_spaces():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM spaces ORDER BY area, code").fetchall()
        stats = conn.execute(
            """
            SELECT status, COUNT(*) AS count
            FROM spaces
            GROUP BY status
            """
        ).fetchall()
        area_stats = conn.execute(
            """
            SELECT
                area,
                COUNT(*) AS total,
                SUM(CASE WHEN status = 'free' THEN 1 ELSE 0 END) AS free_count,
                SUM(CASE WHEN status = 'occupied' THEN 1 ELSE 0 END) AS occupied_count,
                SUM(CASE WHEN status = 'reserved' THEN 1 ELSE 0 END) AS reserved_count,
                SUM(CASE WHEN status = 'maintenance' THEN 1 ELSE 0 END) AS maintenance_count
            FROM spaces
            GROUP BY area
            ORDER BY free_count * 1.0 / COUNT(*) ASC
            """
        ).fetchall()
    area_ranking = []
    for row in area_stats:
        total = row["total"]
        free = row["free_count"]
        idle_rate = round((free / total) * 100, 1) if total > 0 else 0
        area_ranking.append({
            "area": row["area"],
            "total": total,
            "free": free,
            "occupied": row["occupied_count"],
            "reserved": row["reserved_count"],
            "maintenance": row["maintenance_count"],
            "idle_rate": idle_rate,
        })
    return {
        "items": rows_to_dicts(rows),
        "stats": {row["status"]: row["count"] for row in stats},
        "area_ranking": area_ranking,
    }


@spaces_bp.patch("/<int:space_id>")
def update_space(space_id):
    data = request.get_json() or {}
    status = data.get("status")
    plate_number = data.get("plate_number")
    allowed = {"free", "occupied", "reserved", "maintenance"}

    if status not in allowed:
        return {"message": "车位状态不合法"}, 400

    with get_connection() as conn:
        conn.execute(
            """
            UPDATE spaces
            SET status = ?, plate_number = ?, updated_at = datetime('now', 'localtime')
            WHERE id = ?
            """,
            (status, plate_number if status == "occupied" else None, space_id),
        )
        row = conn.execute("SELECT * FROM spaces WHERE id = ?", (space_id,)).fetchone()

    if not row:
        return {"message": "车位不存在"}, 404
    return dict(row)
