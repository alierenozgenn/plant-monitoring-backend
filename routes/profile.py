"""
Bitki profili route'ları
Tek kullanıcı + tek bitki sistemi için optimize edildi
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

# Blueprint oluştur
profile_bp = Blueprint('profile', __name__)
logger = logging.getLogger(__name__)

@profile_bp.route('/plant-profile', methods=['GET'])
def get_plant_profile():
    """Ana bitki profilini getir (tek bitki sistemi)"""
    try:
        plant_id = request.args.get('plant_id', 'main_plant')
        
        from services.firebase_service import FirebaseService
        firebase_service = FirebaseService()
        
        profile = firebase_service.get_plant_profile(plant_id)
        
        return jsonify({
            "status": "success",
            "plant_profile": profile,
            "plant_id": plant_id,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting plant profile: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to get plant profile: {str(e)}"
        }), 500

@profile_bp.route('/plant-profile', methods=['POST'])
def create_or_update_plant_profile():
    """Bitki profili oluştur veya güncelle (tek bitki sistemi)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data received"
            }), 400
        
        plant_id = data.get('plant_id', 'main_plant')
        plant_name = data.get('plant_name', 'My Plant')
        plant_type = data.get('plant_type')
        moisture_threshold = data.get('moisture_threshold', 30)  # Varsayılan %30
        location = data.get('location', 'Indoor')
        notes = data.get('notes', '')
        
        if not plant_type:
            return jsonify({
                "status": "error",
                "message": "plant_type is required"
            }), 400
        
        logger.info(f"🌱 Updating plant profile: {plant_name} ({plant_type})")
        
        # Firebase'e profil kaydet/güncelle
        from services.firebase_service import FirebaseService
        firebase_service = FirebaseService()
        
        profile_data = {
            "plant_id": plant_id,
            "plant_name": plant_name,
            "plant_type": plant_type,
            "moisture_threshold": moisture_threshold,
            "location": location,
            "notes": notes,
            "updated_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        # Mevcut profil var mı kontrol et
        existing_profile = firebase_service.get_plant_profile(plant_id)
        
        if existing_profile:
            # Güncelle
            profile_data['created_at'] = existing_profile.get('created_at', datetime.now().isoformat())
            firebase_service.update_plant_profile(plant_id, profile_data)
            action = "updated"
        else:
            # Yeni oluştur
            profile_data['created_at'] = datetime.now().isoformat()
            firebase_service.save_plant_profile(profile_data)
            action = "created"
        
        return jsonify({
            "status": "success",
            "message": f"Plant profile {action} successfully",
            "plant_id": plant_id,
            "plant_name": plant_name,
            "plant_type": plant_type,
            "moisture_threshold": moisture_threshold,
            "action": action,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error saving plant profile: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to save plant profile: {str(e)}"
        }), 500

@profile_bp.route('/plant-settings', methods=['GET'])
def get_plant_settings():
    """Bitki ayarlarını getir (nem eşiği vs)"""
    try:
        plant_id = request.args.get('plant_id', 'main_plant')
        
        from services.firebase_service import FirebaseService
        firebase_service = FirebaseService()
        
        profile = firebase_service.get_plant_profile(plant_id)
        
        if profile:
            settings = {
                "moisture_threshold": profile.get('moisture_threshold', 30),
                "auto_watering": profile.get('auto_watering', True),
                "notification_enabled": profile.get('notification_enabled', True),
                "watering_duration": profile.get('watering_duration', 3)
            }
        else:
            # Varsayılan ayarlar
            settings = {
                "moisture_threshold": 30,
                "auto_watering": True,
                "notification_enabled": True,
                "watering_duration": 3
            }
        
        return jsonify({
            "status": "success",
            "plant_settings": settings,
            "plant_id": plant_id,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting plant settings: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to get plant settings: {str(e)}"
        }), 500

@profile_bp.route('/plant-settings', methods=['PUT'])
def update_plant_settings():
    """Bitki ayarlarını güncelle"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data received"
            }), 400
        
        plant_id = data.get('plant_id', 'main_plant')
        
        logger.info(f"🔧 Updating plant settings for: {plant_id}")
        
        # Firebase'de ayarları güncelle
        from services.firebase_service import FirebaseService
        firebase_service = FirebaseService()
        
        # Sadece ayar alanlarını güncelle
        settings_data = {
            "moisture_threshold": data.get('moisture_threshold'),
            "auto_watering": data.get('auto_watering'),
            "notification_enabled": data.get('notification_enabled'),
            "watering_duration": data.get('watering_duration'),
            "settings_updated_at": datetime.now().isoformat()
        }
        
        # None değerleri temizle
        settings_data = {k: v for k, v in settings_data.items() if v is not None}
        
        success = firebase_service.update_plant_settings(plant_id, settings_data)
        
        return jsonify({
            "status": "success",
            "message": "Plant settings updated successfully",
            "plant_id": plant_id,
            "updated_settings": settings_data,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error updating plant settings: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to update plant settings: {str(e)}"
        }), 500
