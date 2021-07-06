from functools import wraps
from flask import session, request, redirect, url_for, abort
from wtforms.validators import Length

def accessLevel(access_level):
    def access(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'auth' in session:
                if session["auth"] not in access_level:
                    abort(403)
                return func(*args, **kwargs)
            if len(access_level) == 1 and access_level[0] == "USER":
                return redirect(url_for('login_register', next=request.url))
            abort(403)
        return wrapper
    return access
