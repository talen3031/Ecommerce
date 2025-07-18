from flask_jwt_extended import verify_jwt_in_request, get_jwt
from functools import wraps
from flask import Blueprint, request, jsonify
from service.audit_service import AuditService
from models import User
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        role = claims.get("role")

        if role != 'admin' :
            return jsonify({"error": "Admin only!"}), 403
        #防止別人仿冒 admin
        current_user_id = claims.get("user_id")
        user = User.get_by_user_id(current_user_id)
        if not user or user.role != 'admin':
            AuditService.log(
            user_id=current_user_id,
            action='fake',
            target_type='claims_role(Admin)',
            description=f"claims_role={role}, db_role={getattr(user, 'role', None)}"
            )
            return jsonify({"error": "Admin Not Found!"}), 403
        return fn(*args, **kwargs)
    return wrapper
