from flask_restful import Resource
from flask_jwt_extended import jwt_required
import psutil

class ServerStatusAPI(Resource):
    @jwt_required()
    def get(self):
        try:
            return {
                'cpu_usage': psutil.cpu_percent(interval=1),
                'memory_usage': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('C:\\').percent
            }
        except Exception as e:
            return {'error': str(e)}, 500