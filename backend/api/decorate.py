from flask_jwt_extended import verify_jwt_in_request, get_jwt
from functools import wraps
from flask import Blueprint, request, jsonify


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        role = claims.get("role")
        if role != 'admin' :
            return jsonify({"error": "Admin only!"}), 403
        return fn(*args, **kwargs)
    return wrapper
