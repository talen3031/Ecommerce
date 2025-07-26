from models import db, AuditLog
class AuditService:
    @staticmethod
    def log(user_id=None, guest_id=None, action=None, target_type=None, target_id=None, description=None):
        if user_id is not None and not isinstance(user_id, int):
            user_id = None
        if guest_id is not None and not isinstance(guest_id, str):
            guest_id = None
        log = AuditLog(
            user_id=user_id,
            guest_id=guest_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            description=description
        )
        db.session.add(log)
        db.session.commit()
