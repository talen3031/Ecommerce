from flask import request
from flask_jwt_extended import decode_token,jwt_required, get_jwt_identity
from flask_socketio import emit, join_room, leave_room
from models import User, ChatMessage, db  # 新增 import
from ext_socketio import socketio
from models import User, ChatMessage, db
# 你自己的 admin_required 裝飾器（如有可直接 import）
from api.decorate import admin_required
from flask import Blueprint, request, jsonify
from models import ChatMessage

# 前端連線時帶 JWT token 參數
@socketio.on('connect')
def handle_connect():
    token = request.args.get('token')
    user = None
    if token:
        try:
            data = decode_token(token)
            user_id = data['sub']
            user = User.get_by_user_id(int(user_id))
        except Exception:
            pass
    if user:
        join_room(f"user_{user.id}")
        # 如果是 admin，也加入 admin 房
        if getattr(user, "role", None) == "admin":
            join_room("admin")
        emit('connected', {'msg': f'歡迎 {user.full_name or user.email} 加入客服聊天'})
    else:
        return False
@socketio.on('disconnect')
def handle_disconnect():
    pass

@socketio.on('join_user_room')
def join_user_room(data):
    user_id = data.get('user_id')
    print("admin join room", user_id, "sid:", request.sid)
    join_room(f"user_{user_id}")

@socketio.on('send_message')
def handle_message(data):
    token = data.get('token')
    msg = data.get('msg')
    user = None
    if token:
        try:
            data_token = decode_token(token)
            user_id = data_token['sub']
            user = User.get_by_user_id(int(user_id))
        except Exception:
            pass
    if user:
        # 儲存用戶訊息
        chat_msg = ChatMessage(user_id=user.id, sender="user", message=msg)
        db.session.add(chat_msg)
        db.session.commit()
        # 廣播給 admin
        emit('receive_message', {'from': user.full_name or user.email, 'msg': msg, 'created_at': chat_msg.created_at.isoformat(), 'user_id': user.id}, room='admin')
        # 廣播給自己（關鍵！讓自己也看到剛發送的訊息）
        if user.role!="admin":
            emit('receive_message', {'from': user.full_name or user.email, 'msg': msg, 'created_at': chat_msg.created_at.isoformat(), 'user_id': user.id}, room=f"user_{user.id}")
        # 檢查是否已經有 admin 回覆過
        has_admin_reply = ChatMessage.query.filter_by(user_id=user.id, sender="admin").count() > 0
        if not has_admin_reply:
            auto_reply = "請稍等，待會會有線上客服回復您"
            chat_msg2 = ChatMessage(user_id=user.id, sender="admin", message=auto_reply)
            db.session.add(chat_msg2)
            db.session.commit()
            emit('receive_message', {'from': '客服', 'msg': auto_reply, 'created_at': chat_msg2.created_at.isoformat()}, room=f"user_{user.id}")
    else:
        emit('receive_message', {'from': '系統', 'msg': '未驗證用戶'}, room=request.sid)

@socketio.on('admin_reply')
def admin_reply(data):
    user_id = data.get('user_id')
    msg = data.get('msg')
    chat_msg = ChatMessage(user_id=user_id, sender="admin", message=msg)
    db.session.add(chat_msg)
    db.session.commit()
    emit_data = {
        'from': '客服',
        'msg': msg,
        'created_at': chat_msg.created_at.isoformat(),
        'user_id': user_id
    }
    # 推給 user
    emit('receive_message', emit_data, room=f"user_{user_id}")
    # 也推給 admin 所有房（或 admin 自己）
    emit('receive_message', emit_data, room="admin")


#==============================api============================================

chat_bp = Blueprint('chat_api', __name__, url_prefix='/chat')

@chat_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_chat_users():
    # 查有聊天室訊息的 user（user_id 不重複）
    user_ids = [row[0] for row in db.session.query(ChatMessage.user_id).distinct()]
    users = User.query.filter(User.id.in_(user_ids)).all()
    result = [
        {"id": u.id, "full_name": u.full_name, "email": u.email}
        for u in users
    ]
    return jsonify(result)
#客戶端自己歷史紀錄
@chat_bp.route('/history', methods=['GET'])
@jwt_required()
def get_chat_history():
    user_id = int(get_jwt_identity())
    msgs = ChatMessage.query.filter_by(user_id=user_id).order_by(ChatMessage.created_at).all()
    user = User.query.get(user_id)
    result = []
    for m in msgs:
        if m.sender == "admin":
            from_name = "客服"
        else:
            from_name = user.full_name or user.email or "用戶"
        result.append({
            "from": from_name,
            "msg": m.message,
            "created_at": m.created_at.isoformat(),
            "user_id": m.user_id
        })
    return jsonify(result)

@chat_bp.route('/history/<int:user_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_user_chat_history(user_id):
    messages = ChatMessage.query.filter_by(user_id=user_id).order_by(ChatMessage.created_at).all()
    user = User.query.get(user_id)
    result = []
    for m in messages:
        if m.sender == "admin":
            from_name = "客服"
        else:
            from_name = user.full_name or user.email or "用戶"
        result.append({
            "from": from_name,
            "msg": m.message,
            "created_at": m.created_at.isoformat(),
            "user_id": m.user_id
        })
    return jsonify(result)

@chat_bp.route('/history/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user_chat_history(user_id):
    # 刪除該 user 所有聊天訊息
    count = ChatMessage.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    return jsonify({"deleted": count, "user_id": user_id})
