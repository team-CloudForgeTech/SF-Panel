from flask import Flask, jsonify, render_template, request, send_from_directory, redirect, url_for
from flask_cors import CORS
import psutil
import os
import subprocess
from werkzeug.utils import secure_filename
from concurrent.futures import ThreadPoolExecutor
import logging
import re
import platform
import socket
import time
import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime

app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app.logger.setLevel(logging.INFO)

# 文件上传路径
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 创建线程池
executor = ThreadPoolExecutor(max_workers=5)

def sanitize_filename(filename):
    # 使用正则表达式过滤不安全的字符，但保留中文字符
    sanitized = re.sub(r'[\\/*?:"<>|]', '', filename)
    return sanitized

@app.route('/')
def index():
    # 移除模板渲染，直接返回成功状态
    return jsonify({
        'code': 200,
        'message': 'API server is running'
    })

@app.route('/api/server-status')
def server_status():
    try:
        data = {
            'cpu_usage': psutil.cpu_percent(interval=1),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('C:\\').percent
        }
        return jsonify({
            'code': 200,
            'data': data,
            'message': 'success'
        })
    except Exception as e:
        logging.error(f"Error getting server status: {e}")
        return jsonify({
            'code': 500,
            'message': str(e),
            'data': None
        }), 500

@app.route('/api/files', methods=['GET'])
def list_files():
    try:
        directory = request.args.get('directory', app.config['UPLOAD_FOLDER'])
        if not os.path.exists(directory) or not os.path.isdir(directory):
            raise Exception("目录不存在")
            
        files = os.listdir(directory)
        files_info = [
            {
                'name': file,
                'type': 'directory' if os.path.isdir(os.path.join(directory, file)) else 'file'
            }
            for file in files
        ]
        
        return jsonify({
            'code': 200,
            'data': files_info,
            'message': 'success'
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': str(e),
            'data': None
        }), 500

@app.route('/api/system-info')
def system_info():
    try:
        boot_time = psutil.boot_time()
        uptime_seconds = int(time.time() - boot_time)
        
        info = {
            'os': f"{platform.system()} {platform.release()}",
            'hostname': socket.gethostname(),
            'uptime': str(datetime.timedelta(seconds=uptime_seconds)),
            'platform': {
                'architecture': platform.machine(),
                'processor': platform.processor(),
                'python_version': platform.python_version()
            }
        }
        app.logger.info(f"Successfully retrieved system info: {info}")
        return jsonify({
            'code': 200,
            'data': info,
            'message': 'success'
        })
    except psutil.Error as pe:
        error_msg = f"PSUtil error: {str(pe)}"
        app.logger.error(error_msg)
        return jsonify({
            'code': 500,
            'message': error_msg,
            'data': None
        }), 500
    except Exception as e:
        error_msg = f"获取系统信息失败: {str(e)}"
        app.logger.error(error_msg)
        return jsonify({
            'code': 500,
            'message': error_msg,
            'data': None
        }), 500

@app.route('/api/process-info')
def process_info():
    try:
        processes = list(psutil.process_iter(['pid', 'name', 'status']))
        info = {
            'total': len(processes),
            'running': len([p for p in processes if p.info['status'] == 'running'])
        }
        return jsonify({
            'code': 200,
            'data': info,
            'message': 'success'
        })
    except Exception as e:
        app.logger.error(f"获取进程信息失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': str(e),
            'data': None
        }), 500

@app.route('/api/processes')
def list_processes():
    try:
        processes = [
            {
                'pid': proc.info['pid'],
                'name': proc.info['name']
            }
            for proc in psutil.process_iter(['pid', 'name'])
        ]
        return jsonify({
            'code': 200,
            'data': processes,
            'message': 'success'
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': str(e),
            'data': None
        }), 500

@app.route('/api/shell/execute', methods=['POST'])
def execute_shell_command():
    try:
        command = request.json.get('command')
        if not command:
            raise Exception("命令不能为空")
            
        # 这里需要添加命令验证和安全检查
        result = os.popen(command).read()
        return jsonify({
            'code': 200,
            'data': result,
            'message': 'success'
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': str(e),
            'data': None
        }), 500

# 添加到现有导入下方

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sfpanel.db'
app.config['SECRET_KEY'] = 'your-secret-key'  # 用于JWT加密
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# 添加登录相关路由
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        
        if user and user.check_password(data['password']):
            token = jwt.encode({
                'user_id': user.id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
            }, app.config['SECRET_KEY'])
            
            return jsonify({
                'code': 200,
                'message': '登录成功',
                'data': {'token': token}
            })
        
        return jsonify({
            'code': 401,
            'message': '用户名或密码错误',
            'data': None
        }), 401
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': str(e),
            'data': None
        }), 500

@app.route('/api/change-password', methods=['POST'])
def change_password():
    try:
        data = request.get_json()
        token = request.headers.get('Authorization').split(' ')[1]
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        
        user = User.query.get(payload['user_id'])
        if user and user.check_password(data['old_password']):
            user.set_password(data['new_password'])
            db.session.commit()
            return jsonify({
                'code': 200,
                'message': '密码修改成功',
                'data': None
            })
        
        return jsonify({
            'code': 401,
            'message': '原密码错误',
            'data': None
        }), 401
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': str(e),
            'data': None
        }), 500

# 在 if __name__ == '__main__': 之前添加初始化代码
with app.app_context():
    db.create_all()
    # 创建默认管理员账户
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin')
        admin.set_password('admin')
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
