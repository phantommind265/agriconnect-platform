from functools import wraps
from flask import session, abort

def require_role(*allowed):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            role = session.get("role")
            if role not in allowed:
                abort(403)
            return f(*args, **kwargs)
        return wrapper
    return decorator
