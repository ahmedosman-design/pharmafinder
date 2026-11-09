# Records important activities done by the user in the system

from .db import execute


def log_action(user_id, action, target_type=None, target_id=None, details=None):

    # Convert details to text and limit it to 500 characters
    if details:
        details = str(details)[:500]
    else:
        details = None

    # Saves the activity in the audit_log table
    sql = """
        INSERT INTO audit_log
        (user_id, action, target_type, target_id, details)
        VALUES (%s, %s, %s, %s, %s)
    """

    values = (user_id, action, target_type, target_id, details)

    execute(sql, values)
