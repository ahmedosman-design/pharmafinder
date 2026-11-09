"""Patient endpoints: Health Passport, sharing/revoking access, prescription-based search."""
from datetime import timedelta

from flask import Blueprint, current_app, jsonify, request

from ..audit import log_action
from ..db import execute, query, query_one, transaction
from ..errors import ApiError
from ..geo import format_time, haversine_km, is_open, rank_prescription_matches
from ..rx import expire_overdue, load_prescriptions, now_local
from ..security import current_user, roles_required
from ..validation import as_float, as_int, json_body

bp = Blueprint("patient", __name__, url_prefix="/api/patient")


def _own_prescription(rx_id):
    """Return the prescription only if it belongs to the logged-in patient (else 404)."""
    rows = load_prescriptions("p.prescription_id=%s AND p.patient_id=%s",
                              (rx_id, current_user()["patient_id"]))
    if not rows:
        raise ApiError("Prescription not found", 404)
    return rows[0]


def _grants_for(where, params):
    now = now_local()
    rows = query(
        f"""SELECT g.grant_id, g.prescription_id, p.code, g.pharmacy_id, ph.name AS pharmacy_name,
                   g.granted_at, g.expires_at, g.revoked_at
            FROM grant_access g
            JOIN prescriptions p ON p.prescription_id = g.prescription_id
            JOIN pharmacies ph ON ph.pharmacy_id = g.pharmacy_id
            WHERE {where} ORDER BY g.granted_at DESC""",
        params,
    )
    for g in rows:
        if g["revoked_at"]:
            g["state"] = "revoked"
        elif g["expires_at"] <= now:
            g["state"] = "expired"
        else:
            g["state"] = "active"
    return rows


@bp.get("/prescriptions")
@roles_required("patient")
def list_prescriptions():
    expire_overdue()
    rows = load_prescriptions("p.patient_id=%s", (current_user()["patient_id"],))
    grants = _grants_for("p.patient_id=%s", (current_user()["patient_id"],))
    for rx in rows:
        rx["grants"] = [g for g in grants if g["prescription_id"] == rx["prescription_id"]]
    return jsonify(rows)


@bp.get("/prescriptions/<int:rx_id>")
@roles_required("patient")
def get_prescription(rx_id):
    expire_overdue()
    rx = _own_prescription(rx_id)
    rx["grants"] = _grants_for("g.prescription_id=%s", (rx_id,))
    return jsonify(rx)


@bp.post("/prescriptions/<int:rx_id>/grants")
@roles_required("patient")
def grant_access(rx_id):
    """Let one pharmacy open this prescription for a limited number of hours."""
    user = current_user()
    cfg = current_app.config
    data = json_body()
    expire_overdue()
    rx = _own_prescription(rx_id)
    if rx["status"] != "active":
        raise ApiError(f"Only active prescriptions can be shared (this one is {rx['status']})", 409)

    pharmacy_id = as_int(data.get("pharmacy_id"), "pharmacy_id", 1)
    hours = as_int(data.get("hours", cfg["GRANT_DEFAULT_HOURS"]), "hours", 1, cfg["GRANT_MAX_HOURS"])
    pharmacy = query_one("SELECT pharmacy_id, name FROM pharmacies WHERE pharmacy_id=%s AND is_active=TRUE",
                         (pharmacy_id,))
    if not pharmacy:
        raise ApiError("Pharmacy not found", 404)

    now = now_local()
    expires = now + timedelta(hours=hours)
    with transaction():
        # One live grant per pharmacy: end any existing one before creating the new window
        execute(
            """UPDATE grant_access SET revoked_at=%s
               WHERE prescription_id=%s AND pharmacy_id=%s AND revoked_at IS NULL AND expires_at > %s""",
            (now, rx_id, pharmacy_id, now),
        )
        grant_id = execute(
            "INSERT INTO grant_access (prescription_id, pharmacy_id, granted_at, expires_at) VALUES (%s,%s,%s,%s)",
            (rx_id, pharmacy_id, now, expires),
        )
        log_action(user["user_id"], "GRANT_ACCESS", "prescription", rx_id,
                   f"pharmacy_id={pharmacy_id}; hours={hours}")
    return jsonify({"grant_id": grant_id, "prescription_id": rx_id, "pharmacy_id": pharmacy_id,
                    "pharmacy_name": pharmacy["name"], "granted_at": now, "expires_at": expires,
                    "state": "active"}), 201


@bp.get("/grants")
@roles_required("patient")
def list_grants():
    return jsonify(_grants_for("p.patient_id=%s", (current_user()["patient_id"],)))


@bp.post("/grants/<int:grant_id>/revoke")
@roles_required("patient")
def revoke_grant(grant_id):
    user = current_user()
    now = now_local()
    with transaction():
        grant = query_one(
            """SELECT g.grant_id, g.prescription_id, g.revoked_at, p.patient_id
               FROM grant_access g JOIN prescriptions p ON p.prescription_id = g.prescription_id
               WHERE g.grant_id=%s FOR UPDATE""",
            (grant_id,),
        )
        if not grant or grant["patient_id"] != user["patient_id"]:
            raise ApiError("Access grant not found", 404)
        if grant["revoked_at"]:
            raise ApiError("This access has already been revoked", 409)
        execute("UPDATE grant_access SET revoked_at=%s WHERE grant_id=%s", (now, grant_id))
        log_action(user["user_id"], "REVOKE_ACCESS", "prescription", grant["prescription_id"],
                   f"grant_id={grant_id}")
    return jsonify({"grant_id": grant_id, "state": "revoked", "revoked_at": now})


@bp.get("/prescriptions/<int:rx_id>/pharmacies")
@roles_required("patient")