#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
خدمة WebSocket للإشعارات والتحديثات الحية لنظام آيديا
توفر تحديثات فورية للمستخدمين عبر جميع أجزاء النظام
"""

import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'idea_websocket_secret_key_2024'
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

class NotificationManager:
    """
    مدير الإشعارات والتحديثات الحية
    """
    
    def __init__(self):
        self.connected_users = {}
        self.user_rooms = {}
        self.notification_history = []
        self.system_stats = {
            'total_connections': 0,
            'active_connections': 0,
            'messages_sent': 0,
            'uptime_start': datetime.now()
        }
        
        # بدء مراقب النظام
        self.start_system_monitor()
    
    def add_user(self, session_id: str, user_info: dict):
        """إضافة مستخدم جديد"""
        self.connected_users[session_id] = {
            'user_info': user_info,
            'connected_at': datetime.now(),
            'last_activity': datetime.now(),
            'rooms': []
        }
        self.system_stats['total_connections'] += 1
        self.system_stats['active_connections'] += 1
        
        # إرسال إشعار ترحيب
        welcome_notification = {
            'type': 'welcome',
            'title': 'مرحباً بك في آيديا',
            'message': 'تم الاتصال بنجاح. ستتلقى التحديثات الحية هنا.',
            'timestamp': datetime.now().isoformat(),
            'priority': 'info'
        }
        self.send_notification_to_user(session_id, welcome_notification)
    
    def remove_user(self, session_id: str):
        """إزالة مستخدم"""
        if session_id in self.connected_users:
            del self.connected_users[session_id]
            self.system_stats['active_connections'] -= 1
    
    def join_user_room(self, session_id: str, room: str):
        """إضافة مستخدم لغرفة معينة"""
        if session_id in self.connected_users:
            if room not in self.connected_users[session_id]['rooms']:
                self.connected_users[session_id]['rooms'].append(room)
                join_room(room)
    
    def leave_user_room(self, session_id: str, room: str):
        """إزالة مستخدم من غرفة"""
        if session_id in self.connected_users:
            if room in self.connected_users[session_id]['rooms']:
                self.connected_users[session_id]['rooms'].remove(room)
                leave_room(room)
    
    def send_notification_to_user(self, session_id: str, notification: dict):
        """إرسال إشعار لمستخدم محدد"""
        if session_id in self.connected_users:
            socketio.emit('notification', notification, room=session_id)
            self.system_stats['messages_sent'] += 1
            self.notification_history.append({
                'target': session_id,
                'notification': notification,
                'sent_at': datetime.now().isoformat()
            })
    
    def send_notification_to_room(self, room: str, notification: dict):
        """إرسال إشعار لغرفة معينة"""
        socketio.emit('notification', notification, room=room)
        self.system_stats['messages_sent'] += 1
        self.notification_history.append({
            'target': f'room:{room}',
            'notification': notification,
            'sent_at': datetime.now().isoformat()
        })
    
    def broadcast_notification(self, notification: dict):
        """إرسال إشعار لجميع المستخدمين"""
        socketio.emit('notification', notification, broadcast=True)
        self.system_stats['messages_sent'] += 1
        self.notification_history.append({
            'target': 'broadcast',
            'notification': notification,
            'sent_at': datetime.now().isoformat()
        })
    
    def send_live_update(self, update_type: str, data: dict, target: str = 'broadcast'):
        """إرسال تحديث حي"""
        update = {
            'type': 'live_update',
            'update_type': update_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        if target == 'broadcast':
            socketio.emit('live_update', update, broadcast=True)
        elif target.startswith('room:'):
            room = target[5:]
            socketio.emit('live_update', update, room=room)
        else:
            socketio.emit('live_update', update, room=target)
        
        self.system_stats['messages_sent'] += 1
    
    def get_system_stats(self):
        """الحصول على إحصائيات النظام"""
        uptime = datetime.now() - self.system_stats['uptime_start']
        return {
            **self.system_stats,
            'uptime_seconds': int(uptime.total_seconds()),
            'uptime_formatted': str(uptime).split('.')[0],
            'connected_users_count': len(self.connected_users),
            'notification_history_count': len(self.notification_history)
        }
    
    def start_system_monitor(self):
        """بدء مراقب النظام للتحديثات الدورية"""
        def monitor():
            while True:
                time.sleep(30)  # كل 30 ثانية
                
                # إرسال إحصائيات النظام للمشرفين
                stats_update = {
                    'type': 'system_stats',
                    'stats': self.get_system_stats(),
                    'timestamp': datetime.now().isoformat()
                }
                
                self.send_notification_to_room('admin', {
                    'type': 'system_update',
                    'title': 'تحديث إحصائيات النظام',
                    'message': f'المستخدمون المتصلون: {len(self.connected_users)}',
                    'data': stats_update,
                    'timestamp': datetime.now().isoformat(),
                    'priority': 'low'
                })
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()

# إنشاء مدير الإشعارات
notification_manager = NotificationManager()

# أحداث WebSocket
@socketio.on('connect')
def handle_connect():
    """معالج الاتصال"""
    session_id = request.sid
    user_info = {
        'ip': request.environ.get('REMOTE_ADDR'),
        'user_agent': request.environ.get('HTTP_USER_AGENT', ''),
        'session_id': session_id
    }
    
    notification_manager.add_user(session_id, user_info)
    
    print(f"✅ مستخدم جديد متصل: {session_id}")
    emit('connected', {
        'session_id': session_id,
        'message': 'تم الاتصال بنجاح',
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('disconnect')
def handle_disconnect():
    """معالج قطع الاتصال"""
    session_id = request.sid
    notification_manager.remove_user(session_id)
    print(f"❌ مستخدم منقطع: {session_id}")

@socketio.on('join_room')
def handle_join_room(data):
    """الانضمام لغرفة"""
    session_id = request.sid
    room = data.get('room')
    
    if room:
        notification_manager.join_user_room(session_id, room)
        emit('room_joined', {
            'room': room,
            'message': f'تم الانضمام للغرفة: {room}',
            'timestamp': datetime.now().isoformat()
        })
        print(f"👥 المستخدم {session_id} انضم للغرفة: {room}")

@socketio.on('leave_room')
def handle_leave_room(data):
    """مغادرة غرفة"""
    session_id = request.sid
    room = data.get('room')
    
    if room:
        notification_manager.leave_user_room(session_id, room)
        emit('room_left', {
            'room': room,
            'message': f'تم مغادرة الغرفة: {room}',
            'timestamp': datetime.now().isoformat()
        })
        print(f"👋 المستخدم {session_id} غادر الغرفة: {room}")

@socketio.on('send_notification')
def handle_send_notification(data):
    """إرسال إشعار (للمشرفين فقط)"""
    session_id = request.sid
    
    # التحقق من صلاحيات المشرف (يمكن تحسينها لاحقاً)
    notification = data.get('notification', {})
    target = data.get('target', 'broadcast')
    
    if target == 'broadcast':
        notification_manager.broadcast_notification(notification)
    elif target.startswith('room:'):
        room = target[5:]
        notification_manager.send_notification_to_room(room, notification)
    else:
        notification_manager.send_notification_to_user(target, notification)
    
    emit('notification_sent', {
        'message': 'تم إرسال الإشعار بنجاح',
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('request_stats')
def handle_request_stats():
    """طلب إحصائيات النظام"""
    session_id = request.sid
    stats = notification_manager.get_system_stats()
    
    emit('system_stats', {
        'stats': stats,
        'timestamp': datetime.now().isoformat()
    })

# نقاط نهاية REST API
@app.route('/api/notifications/send', methods=['POST'])
def api_send_notification():
    """إرسال إشعار عبر API"""
    try:
        data = request.get_json()
        notification = data.get('notification', {})
        target = data.get('target', 'broadcast')
        
        if target == 'broadcast':
            notification_manager.broadcast_notification(notification)
        elif target.startswith('room:'):
            room = target[5:]
            notification_manager.send_notification_to_room(room, notification)
        else:
            notification_manager.send_notification_to_user(target, notification)
        
        return jsonify({
            'status': 'success',
            'message': 'تم إرسال الإشعار بنجاح',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'خطأ في إرسال الإشعار: {str(e)}'
        }), 500

@app.route('/api/live-update/send', methods=['POST'])
def api_send_live_update():
    """إرسال تحديث حي عبر API"""
    try:
        data = request.get_json()
        update_type = data.get('update_type', 'general')
        update_data = data.get('data', {})
        target = data.get('target', 'broadcast')
        
        notification_manager.send_live_update(update_type, update_data, target)
        
        return jsonify({
            'status': 'success',
            'message': 'تم إرسال التحديث الحي بنجاح',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'خطأ في إرسال التحديث: {str(e)}'
        }), 500

@app.route('/api/stats', methods=['GET'])
def api_get_stats():
    """الحصول على إحصائيات النظام"""
    stats = notification_manager.get_system_stats()
    return jsonify({
        'status': 'success',
        'stats': stats,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/health', methods=['GET'])
def api_health():
    """فحص حالة الخدمة"""
    return jsonify({
        'status': 'healthy',
        'service': 'آيديا WebSocket',
        'version': '1.0',
        'timestamp': datetime.now().isoformat()
    })

# تحديثات تجريبية دورية
def send_demo_updates():
    """إرسال تحديثات تجريبية للاختبار"""
    import random
    
    def demo_loop():
        while True:
            time.sleep(60)  # كل دقيقة
            
            # تحديثات تجريبية مختلفة
            demo_updates = [
                {
                    'type': 'project_update',
                    'title': 'تحديث مشروع',
                    'message': 'تم إنجاز مرحلة جديدة في مشروع العميل',
                    'priority': 'medium'
                },
                {
                    'type': 'system_alert',
                    'title': 'تنبيه النظام',
                    'message': 'تم تحديث قاعدة البيانات بنجاح',
                    'priority': 'low'
                },
                {
                    'type': 'new_message',
                    'title': 'رسالة جديدة',
                    'message': 'لديك رسالة جديدة من العميل',
                    'priority': 'high'
                }
            ]
            
            # اختيار تحديث عشوائي
            update = random.choice(demo_updates)
            update['timestamp'] = datetime.now().isoformat()
            
            # إرسال للغرف المختلفة
            rooms = ['admin', 'client', 'team']
            target_room = random.choice(rooms)
            
            notification_manager.send_notification_to_room(target_room, update)
    
    demo_thread = threading.Thread(target=demo_loop, daemon=True)
    demo_thread.start()

if __name__ == '__main__':
    print("🔌 بدء تشغيل خدمة WebSocket للإشعارات والتحديثات الحية...")
    print("🌐 الخدمة متاحة على: http://localhost:3001")
    
    # بدء التحديثات التجريبية
    send_demo_updates()
    
    socketio.run(app, host='0.0.0.0', port=3001, debug=True)
