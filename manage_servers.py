#!/usr/bin/env python3
"""
سكريبت إدارة خوادم Django المتعددة لنظام IDEA
يدعم تشغيل وإيقاف وإعادة تشغيل خوادم متعددة لموازنة الأحمال
"""

import os
import sys
import time
import signal
import subprocess
import json
import psutil
from pathlib import Path

class ServerManager:
    """مدير الخوادم المتعددة"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.idea_cms_dir = self.base_dir / 'idea_cms_project'
        self.pid_dir = self.base_dir / 'pids'
        self.log_dir = self.base_dir / 'logs'
        
        # إنشاء المجلدات المطلوبة
        self.pid_dir.mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)
        
        # تكوين الخوادم
        self.servers = {
            'django': [
                {'name': 'django-8000', 'port': 8000, 'workers': 4},
                {'name': 'django-8001', 'port': 8001, 'workers': 4},
                {'name': 'django-8002', 'port': 8002, 'workers': 3},
                {'name': 'django-8003', 'port': 8003, 'workers': 2},  # خادم احتياطي
            ],
            'websocket': [
                {'name': 'websocket-3001', 'port': 3001, 'script': 'websocket_service.py'},
                {'name': 'websocket-3002', 'port': 3002, 'script': 'websocket_service.py'},
            ],
            'chatbot': [
                {'name': 'chatbot-5000', 'port': 5000, 'script': 'website_project_v3/chatbot_service.py'},
                {'name': 'chatbot-5001', 'port': 5001, 'script': 'website_project_v3/chatbot_service.py'},
            ]
        }
    
    def start_django_server(self, server_config):
        """تشغيل خادم Django"""
        name = server_config['name']
        port = server_config['port']
        workers = server_config.get('workers', 4)
        
        print(f"بدء تشغيل خادم Django: {name} على المنفذ {port}")
        
        # ملف PID
        pid_file = self.pid_dir / f"{name}.pid"
        
        # ملف السجل
        log_file = self.log_dir / f"{name}.log"
        
        # أمر تشغيل الخادم
        cmd = [
            sys.executable, 'manage.py', 'runserver',
            f'127.0.0.1:{port}',
            '--noreload'
        ]
        
        # تشغيل الخادم
        with open(log_file, 'w') as log:
            process = subprocess.Popen(
                cmd,
                cwd=self.idea_cms_dir,
                stdout=log,
                stderr=subprocess.STDOUT,
                preexec_fn=os.setsid
            )
        
        # حفظ PID
        with open(pid_file, 'w') as f:
            f.write(str(process.pid))
        
        print(f"تم تشغيل {name} بـ PID: {process.pid}")
        return process.pid
    
    def start_python_service(self, server_config, service_type):
        """تشغيل خدمة Python (WebSocket أو Chatbot)"""
        name = server_config['name']
        port = server_config['port']
        script = server_config['script']
        
        print(f"بدء تشغيل خدمة {service_type}: {name} على المنفذ {port}")
        
        # ملف PID
        pid_file = self.pid_dir / f"{name}.pid"
        
        # ملف السجل
        log_file = self.log_dir / f"{name}.log"
        
        # مسار السكريبت
        script_path = self.base_dir / script
        
        # متغيرات البيئة
        env = os.environ.copy()
        env['PORT'] = str(port)
        env['SERVICE_NAME'] = name
        
        # أمر تشغيل الخدمة
        cmd = [sys.executable, str(script_path)]
        
        # تشغيل الخدمة
        with open(log_file, 'w') as log:
            process = subprocess.Popen(
                cmd,
                cwd=self.base_dir,
                stdout=log,
                stderr=subprocess.STDOUT,
                env=env,
                preexec_fn=os.setsid
            )
        
        # حفظ PID
        with open(pid_file, 'w') as f:
            f.write(str(process.pid))
        
        print(f"تم تشغيل {name} بـ PID: {process.pid}")
        return process.pid
    
    def stop_server(self, name):
        """إيقاف خادم محدد"""
        pid_file = self.pid_dir / f"{name}.pid"
        
        if not pid_file.exists():
            print(f"لم يتم العثور على ملف PID للخادم: {name}")
            return False
        
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # التحقق من وجود العملية
            if psutil.pid_exists(pid):
                # إيقاف العملية بلطف
                os.kill(pid, signal.SIGTERM)
                
                # انتظار إيقاف العملية
                for _ in range(10):
                    if not psutil.pid_exists(pid):
                        break
                    time.sleep(1)
                
                # إيقاف قسري إذا لم تتوقف
                if psutil.pid_exists(pid):
                    os.kill(pid, signal.SIGKILL)
                    time.sleep(2)
                
                print(f"تم إيقاف الخادم: {name} (PID: {pid})")
            else:
                print(f"العملية غير موجودة: {name} (PID: {pid})")
            
            # حذف ملف PID
            pid_file.unlink()
            return True
            
        except Exception as e:
            print(f"خطأ في إيقاف الخادم {name}: {e}")
            return False
    
    def get_server_status(self, name):
        """الحصول على حالة الخادم"""
        pid_file = self.pid_dir / f"{name}.pid"
        
        if not pid_file.exists():
            return {'status': 'stopped', 'pid': None}
        
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            if psutil.pid_exists(pid):
                process = psutil.Process(pid)
                return {
                    'status': 'running',
                    'pid': pid,
                    'cpu_percent': process.cpu_percent(),
                    'memory_percent': process.memory_percent(),
                    'create_time': process.create_time()
                }
            else:
                # حذف ملف PID غير الصحيح
                pid_file.unlink()
                return {'status': 'stopped', 'pid': None}
                
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def start_all(self):
        """تشغيل جميع الخوادم"""
        print("بدء تشغيل جميع الخوادم...")
        
        # تشغيل خوادم Django
        for server in self.servers['django']:
            try:
                self.start_django_server(server)
                time.sleep(2)  # انتظار قصير بين الخوادم
            except Exception as e:
                print(f"خطأ في تشغيل خادم Django {server['name']}: {e}")
        
        # تشغيل خوادم WebSocket
        for server in self.servers['websocket']:
            try:
                self.start_python_service(server, 'WebSocket')
                time.sleep(1)
            except Exception as e:
                print(f"خطأ في تشغيل خادم WebSocket {server['name']}: {e}")
        
        # تشغيل خوادم Chatbot
        for server in self.servers['chatbot']:
            try:
                self.start_python_service(server, 'Chatbot')
                time.sleep(1)
            except Exception as e:
                print(f"خطأ في تشغيل خادم Chatbot {server['name']}: {e}")
        
        print("تم الانتهاء من تشغيل الخوادم")
    
    def stop_all(self):
        """إيقاف جميع الخوادم"""
        print("إيقاف جميع الخوادم...")
        
        all_servers = []
        for server_type in self.servers.values():
            all_servers.extend([s['name'] for s in server_type])
        
        for name in all_servers:
            self.stop_server(name)
        
        print("تم إيقاف جميع الخوادم")
    
    def restart_all(self):
        """إعادة تشغيل جميع الخوادم"""
        print("إعادة تشغيل جميع الخوادم...")
        self.stop_all()
        time.sleep(3)
        self.start_all()
    
    def status_all(self):
        """عرض حالة جميع الخوادم"""
        print("\n=== حالة الخوادم ===")
        
        for server_type, servers in self.servers.items():
            print(f"\n{server_type.upper()} Servers:")
            print("-" * 50)
            
            for server in servers:
                name = server['name']
                status = self.get_server_status(name)
                
                if status['status'] == 'running':
                    print(f"  {name:<20} | ✅ يعمل | PID: {status['pid']} | CPU: {status.get('cpu_percent', 0):.1f}% | Memory: {status.get('memory_percent', 0):.1f}%")
                elif status['status'] == 'stopped':
                    print(f"  {name:<20} | ❌ متوقف")
                else:
                    print(f"  {name:<20} | ⚠️  خطأ: {status.get('error', 'غير معروف')}")
    
    def health_check(self):
        """فحص صحة الخوادم"""
        import requests
        
        print("\n=== فحص صحة الخوادم ===")
        
        # فحص خوادم Django
        for server in self.servers['django']:
            port = server['port']
            name = server['name']
            
            try:
                response = requests.get(f'http://127.0.0.1:{port}/health/', timeout=5)
                if response.status_code == 200:
                    print(f"  {name:<20} | ✅ صحي")
                else:
                    print(f"  {name:<20} | ⚠️  استجابة غير طبيعية: {response.status_code}")
            except Exception as e:
                print(f"  {name:<20} | ❌ غير متاح: {e}")
        
        # فحص خوادم WebSocket
        for server in self.servers['websocket']:
            port = server['port']
            name = server['name']
            
            try:
                response = requests.get(f'http://127.0.0.1:{port}/api/health', timeout=5)
                if response.status_code == 200:
                    print(f"  {name:<20} | ✅ صحي")
                else:
                    print(f"  {name:<20} | ⚠️  استجابة غير طبيعية: {response.status_code}")
            except Exception as e:
                print(f"  {name:<20} | ❌ غير متاح: {e}")
        
        # فحص خوادم Chatbot
        for server in self.servers['chatbot']:
            port = server['port']
            name = server['name']
            
            try:
                response = requests.get(f'http://127.0.0.1:{port}/health', timeout=5)
                if response.status_code == 200:
                    print(f"  {name:<20} | ✅ صحي")
                else:
                    print(f"  {name:<20} | ⚠️  استجابة غير طبيعية: {response.status_code}")
            except Exception as e:
                print(f"  {name:<20} | ❌ غير متاح: {e}")


def main():
    """الدالة الرئيسية"""
    if len(sys.argv) < 2:
        print("الاستخدام:")
        print("  python manage_servers.py start     - تشغيل جميع الخوادم")
        print("  python manage_servers.py stop      - إيقاف جميع الخوادم")
        print("  python manage_servers.py restart   - إعادة تشغيل جميع الخوادم")
        print("  python manage_servers.py status    - عرض حالة الخوادم")
        print("  python manage_servers.py health    - فحص صحة الخوادم")
        return
    
    manager = ServerManager()
    command = sys.argv[1].lower()
    
    if command == 'start':
        manager.start_all()
    elif command == 'stop':
        manager.stop_all()
    elif command == 'restart':
        manager.restart_all()
    elif command == 'status':
        manager.status_all()
    elif command == 'health':
        manager.health_check()
    else:
        print(f"أمر غير معروف: {command}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
