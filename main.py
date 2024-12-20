from flask import Flask, jsonify, render_template, request, send_from_directory, redirect, url_for
import psutil
import os
import subprocess
from werkzeug.utils import secure_filename
from concurrent.futures import ThreadPoolExecutor
import logging
import re

app = Flask(__name__)

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
    return render_template('index.html')

@app.route('/api/server-status')
def server_status():
    def get_status():
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory_usage = psutil.virtual_memory().percent
            disk_usage = psutil.disk_usage('C:\\').percent  # 根据你的服务器操作系统调整路径
            return {'cpu_usage': cpu_usage, 'memory_usage': memory_usage, 'disk_usage': disk_usage}
        except Exception as e:
            app.logger.error(f"Error getting server status: {e}")
            return {'error': "获取服务器状态时出错"}, 500

    future = executor.submit(get_status)
    return jsonify(future.result())

@app.route('/api/list-files', methods=['GET'])
def list_files():
    directory = request.args.get('directory', app.config['UPLOAD_FOLDER'])

    def get_files(directory):
        if not os.path.exists(directory) or not os.path.isdir(directory):
            return {'error': "目录不存在"}, 400
        files = os.listdir(directory)
        files_info = []
        for file in files:
            file_path = os.path.join(directory, file)
            if os.path.isdir(file_path):
                files_info.append({'name': file, 'type': 'directory'})
            else:
                files_info.append({'name': file, 'type': 'file'})
        return {'files': files_info}, 200

    future = executor.submit(get_files, directory)
    result, status_code = future.result()
    return jsonify(result), status_code

@app.route('/api/upload-file', methods=['POST'])
def upload_file():
    directory = request.form.get('directory', app.config['UPLOAD_FOLDER'])

    def save_file(directory, file):
        if not os.path.exists(directory) or not os.path.isdir(directory):
            return {'error': "目录不存在"}, 400
        if file.filename == '':
            return {'error': "未选择文件"}, 400
        filename = sanitize_filename(file.filename)
        file_path = os.path.join(directory, filename)
        file.save(file_path)
        return {'success': "文件上传成功"}, 200

    if 'file' not in request.files:
        return jsonify(error="未找到文件部分"), 400
    file = request.files['file']
    future = executor.submit(save_file, directory, file)
    result = future.result()
    if result.get('error'):
        return jsonify(result), 400
    return jsonify(result)  # 直接返回结果，确保前端能够正确处理

@app.route('/api/delete-file', methods=['POST'])
def delete_file():
    filename = request.form.get('filename')
    directory = request.form.get('directory', app.config['UPLOAD_FOLDER'])

    def remove_file(directory, filename):
        if not filename:
            return {'error': "未提供文件名"}, 400
        file_path = os.path.join(directory, filename)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            os.remove(file_path)
            return {'success': "文件删除成功"}, 200
        else:
            return {'error': "文件不存在"}, 400

    future = executor.submit(remove_file, directory, filename)
    result = future.result()
    return jsonify(result), result.get('status_code', 200)

@app.route('/api/create-directory', methods=['POST'])
def create_directory():
    directory_name = request.form.get('directory_name')
    directory = request.form.get('directory', app.config['UPLOAD_FOLDER'])

    def create_dir(directory, directory_name):
        if not directory_name:
            return {'error': "未提供目录名"}, 400
        new_directory_path = os.path.join(directory, directory_name)
        if not os.path.exists(new_directory_path):
            os.makedirs(new_directory_path)
            return {'success': "目录创建成功"}, 200
        else:
            return {'error': "目录已存在"}, 400

    future = executor.submit(create_dir, directory, directory_name)
    result = future.result()
    return jsonify(result), result.get('status_code', 200)

@app.route('/api/delete-directory', methods=['POST'])
def delete_directory():
    directory_name = request.form.get('directory_name')
    directory = request.form.get('directory', app.config['UPLOAD_FOLDER'])

    def remove_dir(directory, directory_name):
        if not directory_name:
            return {'error': "未提供目录名"}, 400
        directory_path = os.path.join(directory, directory_name)
        if os.path.exists(directory_path) and os.path.isdir(directory_path):
            try:
                os.rmdir(directory_path)  # 注意：os.rmdir只能删除空目录
            except OSError as e:
                return {'error': "目录不为空"}, 400
            return {'success': "目录删除成功"}, 200
        else:
            return {'error': "目录不存在"}, 400

    future = executor.submit(remove_dir, directory, directory_name)
    result = future.result()
    return jsonify(result), result.get('status_code', 200)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    directory = request.args.get('directory', app.config['UPLOAD_FOLDER'])

    def get_file(directory, filename):
        file_path = os.path.join(directory, filename)
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return {'error': "文件不存在"}, 400
        return send_from_directory(directory, filename), 200

    future = executor.submit(get_file, directory, filename)
    result = future.result()
    if isinstance(result, dict):
        return jsonify(result), result.get('status_code', 200)
    return result

@app.route('/api/view-file', methods=['GET'])
def view_file():
    filename = request.args.get('filename')
    directory = request.args.get('directory', app.config['UPLOAD_FOLDER'])

    def read_file(directory, filename):
        if not filename:
            return {'error': "未提供文件名"}, 400
        file_path = os.path.join(directory, filename)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
            except UnicodeDecodeError:
                return {'error': "文件不是文本文件"}, 400
            return {'content': content}, 200
        else:
            return {'error': "文件不存在"}, 400

    future = executor.submit(read_file, directory, filename)
    result = future.result()
    return jsonify(result), result.get('status_code', 200)

@app.route('/process-manager')
def process_manager():
    return render_template('process_manager.html')

@app.route('/shell-terminal')
def shell_terminal():
    return render_template('shell_terminal.html')

@app.route('/file-manager')
def file_manager():
    directory = request.args.get('directory', app.config['UPLOAD_FOLDER'])
    return render_template('file_manager.html', upload_folder=directory)

@app.route('/api/shell-command', methods=['POST'])
def execute_shell_command():
    try:
        # 获取POST请求中的命令
        command = request.form['command']
        app.logger.info(f"Received command: {command}")

        # 执行命令
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        app.logger.info(f"Command output: {result.stdout}")
        app.logger.info(f"Command error: {result.stderr}")

        # 返回结果
        return jsonify({
            'output': result.stdout,
            'error': result.stderr
        })
    except Exception as e:
        app.logger.error(f"Error executing command: {e}")
        return jsonify({
            'output': '',
            'error': str(e)
        }), 500

@app.route('/api/list-processes')
def list_processes():
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                processes.append({'pid': proc.info['pid'], 'name': proc.info['name']})
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # 忽略不存在的进程、访问被拒绝的进程和僵尸进程
                continue
        return jsonify({'processes': processes}), 200
    except Exception as e:
        app.logger.error(f"Error listing processes: {e}")
        return jsonify({'error': f"获取进程列表时出错: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
