# Authentication and role based access control
from functools import wraps
from flask import current_app, g, session
from werkzeug.security import check_password_hash, generate_password_hash
from .errors import ApiError
from .db import query_one

ROLES = ("patient", "doctor", "pharmacist", "admin")

def hash_password(password):
    return generate_password_hash(password)

def verify_password(password_hash, password):
    return check_password_hash(password_hash, password)

def load_current_user():

    user_id = session.get("user_id")
    if not user_id:
        return None
    
    user = query_one(
        "SELECT user_id, full_name, email, phone, role, is_active, FROM users WHERE user_id = %s",
        (user_id,),
    )
    if not user or not user["is_active"]:
        session.clear()
        return None
    # attaching the role specific id
    if user["role"] == "patient":
        row = query_one("SELECT patient_id FROM patients WHERE user_id= %s", (user_id,))
        user["patient_id"] = row["patient_id"] if row else None
    elif user["role"] == "doctor":
        row = query_one("SELECT doctor_id FROM doctors WHERE user_id=%s", (user_id,))
        user["doctor_id"] = row["doctor_id"] if row else None
    elif user["role"] == "pharmacist":
        row = query_one("SELECT pharmacist_id, pharmacy_id FROM pharmacists WHERE user_id=%s", (user_id,))
        user["pharmacist_id"] = row["pharmacist_id"] if row else None
        user["pharmacy_id"] = row["pharmcay_id"] if row else None
    return user


    def current_user():
        if "user" not in g:
            g.user = load_current_user()
        return g.user
# Requires a user to log in before requesting an endpoint
    def login_required(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            # if nobody is logged in reject the request 
            if current_user() is None:
                raise ApiError("login required", 401)
            # otherwise execute the original endpoint
            return view(*args, **keargs)
        return wrapper

def role_required(*roles):
    def decorate(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            user = current_user()
            if user is None:
                raise ApiError("login required", 401)
            if user["role"] not in roles:
                raise ApiError("you do not have permission to do this", 403)
            return view(*args, **kwargs)
        return wrapper
    return decorator

# counting recent failed attempts
def recent_failures(action, user_id=None, details=None):
    window = current_app.config["FAILED_ATTEMPT_WINDOW_MINUTES"]
    if user_id is not None:
        row = query_one(
            "SELECT COUNT(*) AS n FROM audit_log WHERE action=%s AND user_id=%s "
            "AND created_at > NOW() - INTERVAL %s MINUTE",
            (action, user_id, window),
        )
    else:
        row = query_one(
            "SELECT COUNT(*) AS n FROM audit_log WHERE action=%s AND details=%s "
            "AND created_at > NOW() - INTERVAL %s MINUTE",
            (action, details, window),
        )
    return row["n"]




        



