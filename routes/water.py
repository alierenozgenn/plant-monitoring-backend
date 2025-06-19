"""
Sulama sistemi route'ları
Tek kullanıcı sistemi için optimize edildi
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

# Blueprint oluştur
water_bp = Blueprint('water', __name__)
logger = logging.getLogger(__name__)

# Global sulama komutu flag'i (basit implementasyon)
pending_water_commands = {}  # plant_id: timestamp

@water_bp.route('/trigger-watering', methods=['POST'])
def trigger_watering():
    """
    Manuel sulama komutu (tek kullanıcı sistemi)
    ESP32'ye komut kuyruğa alınır
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data received"
            }), 400
        
        plant_id = data.get('plant_id', 'main_plant')  # Tek bitki
        duration = data.get('duration', 3)  # Varsayılan 3 saniye
        
        logger.info(f"💧 Manual watering requested for plant {plant_id}")
        
        # Global flag'e komut ekle
        pending_water_commands[plant_id] = {
            "timestamp": datetime.now().isoformat(),
            "duration": duration
        }
        
        # Firebase'e manuel sulama geçmişine kaydet
        from services.firebase_service import FirebaseService
        firebase_service = FirebaseService()
        
        watering_data = {
            "plant_id": plant_id,
            "type": "manual",
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
            "triggered_by": "mobile_app",
            "status": "command_queued"
        }
        firebase_service.save_watering_history(watering_data)
        
        return jsonify({
            "status": "success",
            "message": "Manual watering command queued for ESP32",
            "plant_id": plant_id,
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
            "note": "ESP32 will check this command in next polling cycle"
        })
    
    except Exception as e:
        logger.error(f"Error triggering watering: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to trigger watering: {str(e)}"
        }), 500

@water_bp.route('/watering-history', methods=['GET'])
def get_watering_history():
    """Sulama geçmişini getir (tek kullanıcı sistemi)"""
    try:
        limit = request.args.get('limit', 50, type=int)
        plant_id = request.args.get('plant_id', 'main_plant')
        
        from services.firebase_service import FirebaseService
        firebase_service = FirebaseService()
        
        history = firebase_service.get_watering_history(plant_id, limit)
        
        return jsonify({
            "status": "success",
            "watering_history": history,
            "total_records": len(history),
            "plant_id": plant_id,
            "limit": limit
        })
    
    except Exception as e:
        logger.error(f"Error getting watering history: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to get watering history: {str(e)}"
        }), 500

@water_bp.route('/moisture-history', methods=['GET'])
def get_moisture_history():
    """Nem geçmişini getir (tek kullanıcı sistemi)"""
    try:
        limit = request.args.get('limit', 100, type=int)
        days = request.args.get('days', 7, type=int)  # Son X gün
        plant_id = request.args.get('plant_id', 'main_plant')
        
        from services.firebase_service import FirebaseService
        firebase_service = FirebaseService()
        
        history = firebase_service.get_moisture_history(plant_id, limit, days)
        
        return jsonify({
            "status": "success",
            "moisture_history": history,
            "total_records": len(history),
            "plant_id": plant_id,
            "days_covered": days,
            "limit": limit
        })
    
    except Exception as e:
        logger.error(f"Error getting moisture history: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to get moisture history: {str(e)}"
        }), 500

@water_bp.route('/disease-history', methods=['GET'])
def get_disease_history():
    """Hastalık kontrol geçmişini getir (tek kullanıcı sistemi)"""
    try:
        limit = request.args.get('limit', 50, type=int)
        plant_id = request.args.get('plant_id', 'main_plant')
        
        from services.firebase_service import FirebaseService
        firebase_service = FirebaseService()
        
        history = firebase_service.get_disease_history(plant_id, limit)
        
        return jsonify({
            "status": "success",
            "disease_history": history,
            "total_records": len(history),
            "plant_id": plant_id,
            "limit": limit
        })
    
    except Exception as e:
        logger.error(f"Error getting disease history: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to get disease history: {str(e)}"
        }), 500

# Global fonksiyonlar (sensor.py tarafından kullanılır)
def check_pending_water_command(plant_id):
    """Bekleyen sulama komutu var mı kontrol et"""
    return plant_id in pending_water_commands

def clear_water_command(plant_id):
    """Sulama komutunu temizle"""
    if plant_id in pending_water_commands:
        command_info = pending_water_commands[plant_id]
        del pending_water_commands[plant_id]
        logger.info(f"Water command cleared for plant {plant_id}")
        return True
    return False
