"""
Ana sayfa ve sistem durumu route'ları - Flutter için optimize edildi
"""

from flask import Blueprint, jsonify
from datetime import datetime
import logging

# Blueprint oluştur
main_bp = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

@main_bp.route('/', methods=['GET'])
def home():
    """Ana sayfa - Flutter için sistem durumu"""
    return jsonify({
        "message": "🌱 Smart Plant Monitoring API",
        "status": "running",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "flutter_ready": True,
        "endpoints": {
            "plant_management": {
                "get_plants": "GET /api/plants",
                "identify_plant": "POST /api/identify-plant",
                "plant_selection": "POST /api/plant-selection",
                "plant_profile": "GET/POST /api/plant-profile",
                "plant_settings": "GET/PUT /api/plant-settings"
            },
            "watering_system": {
                "trigger_watering": "POST /api/trigger-watering",
                "watering_history": "GET /api/watering-history",
                "moisture_history": "GET /api/moisture-history"
            },
            "health_monitoring": {
                "check_disease": "POST /api/check-disease",
                "disease_history": "GET /api/disease-history"
            },
            "esp32_communication": {
                "pump_status": "POST /api/pump-status",
                "should_water": "GET /api/should-water",
                "sensor_data": "POST /api/sensor-data"
            },
            "system": {
                "health_check": "GET /health",
                "system_status": "GET /api/system-status"
            }
        }
    })

@main_bp.route('/health', methods=['GET'])
def health_check():
    """Flutter için sistem sağlık kontrolü"""
    try:
        from services.model_service import ModelService
        from services.firebase_service import FirebaseService
        
        model_service = ModelService()
        firebase_service = FirebaseService()
        
        # Model durumları
        models_loaded = len(model_service.specific_disease_interpreters)
        plant_model_ready = model_service.plant_type_interpreter is not None
        disease_model_ready = model_service.general_disease_interpreter is not None
        
        # Firebase durumu
        firebase_connected = firebase_service.db is not None
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "ai_models": {
                    "plant_identification": plant_model_ready,
                    "disease_detection": disease_model_ready,
                    "specific_models_count": models_loaded,
                    "total_plants_supported": len(model_service.get_available_plants().get("plants", []))
                },
                "database": {
                    "firebase_connected": firebase_connected,
                    "mode": "production" if firebase_connected else "mock"
                },
                "esp32": {
                    "communication_ready": True,
                    "status": "waiting_for_connection"
                }
            },
            "flutter_compatible": True
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "flutter_compatible": True
        }), 500

@main_bp.route('/api/system-status', methods=['GET'])
def system_status():
    """Flutter için detaylı sistem durumu"""
    try:
        from services.model_service import ModelService
        from services.firebase_service import FirebaseService
        from services.moisture_service import MoistureService
        
        model_service = ModelService()
        firebase_service = FirebaseService()
        moisture_service = MoistureService()
        
        return jsonify({
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "system": {
                "version": "2.0.0",
                "uptime": "Running",
                "mode": "single_user_single_plant"
            },
            "ai_capabilities": {
                "plant_identification_available": model_service.plant_type_interpreter is not None,
                "disease_detection_available": model_service.general_disease_interpreter is not None,
                "supported_plants": len(model_service.get_available_plants().get("plants", [])),
                "specific_disease_models": list(model_service.specific_disease_interpreters.keys())
            },
            "connectivity": {
                "firebase_status": "connected" if firebase_service.db else "mock_mode",
                "esp32_status": "ready_for_connection"
            },
            "pending_commands": {
                "water_commands": len(moisture_service.get_pending_commands())
            }
        })
        
    except Exception as e:
        logger.error(f"System status error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500
