from models import db, AuditLog

class AuditService:
    @staticmethod
    def log(user_id, action, target_type, target_id=None, description=None):
        log = AuditLog(
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            description=description
        )
        db.session.add(log)
        db.session.commit()
