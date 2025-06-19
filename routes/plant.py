"""
AI model route'ları
Bitki türü tespiti ve hastalık kontrolü
Tek kullanıcı sistemi için optimize edildi
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

# Blueprint oluştur
plant_bp = Blueprint('plant', __name__)
logger = logging.getLogger(__name__)

@plant_bp.route('/plants', methods=['GET'])
def get_plants():
    """Seçilebilir bitki listesini döndür"""
    try:
        from services.model_service import ModelService
        model_service = ModelService()
        
        result = model_service.get_available_plants()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting plant list: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to get plant list: {str(e)}"
        }), 500

@plant_bp.route('/identify-plant', methods=['POST'])
def identify_plant():
    """
    Bitki türü tespiti - 5 sonuç döndür
    Tek kullanıcı sistemi
    """
    try:
        # Dosya kontrolü
        if 'image' not in request.files:
            return jsonify({
                "status": "error",
                "message": "No image file provided"
            }), 400
        
        image_file = request.files['image']
        plant_id = request.form.get('plant_id', 'main_plant')  # Tek bitki
        
        if image_file.filename == '':
            return jsonify({
                "status": "error", 
                "message": "No image selected"
            }), 400
        
        logger.info(f"🔍 Plant identification requested for plant: {plant_id}")
        
        # Model ile tahmin yap
        from services.model_service import ModelService
        model_service = ModelService()
        
        result = model_service.predict_plant_type(image_file)
        
        if "error" in result:
            return jsonify({
                "status": "error",
                "message": result["error"]
            }), 500
        
        # Sonucu Firebase'e kaydet
        from services.firebase_service import FirebaseService
        firebase_service = FirebaseService()
        
        # Görseli Firebase Storage'a yükle
        image_url = firebase_service.upload_image(image_file, f"plant_identification")
        
        identification_record = {
            "plant_id": plant_id,
            "image_url": image_url,
            "predictions": result.get("predictions"),
            "model_used": result.get("model_used"),
            "timestamp": datetime.now().isoformat()
        }
        firebase_service.save_plant_identification(identification_record)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in plant identification: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Plant identification failed: {str(e)}"
        }), 500

@plant_bp.route('/check-disease', methods=['POST'])
def check_disease():
    """
    Bitki hastalığı kontrolü - hibrit sistem
    Tek kullanıcı sistemi
    """
    try:
        # Dosya kontrolü
        if 'image' not in request.files:
            return jsonify({
                "status": "error",
                "message": "No image file provided"
            }), 400
        
        image_file = request.files['image']
        plant_type = request.form.get('plant_type')
        plant_id = request.form.get('plant_id', 'main_plant')  # Tek bitki
        
        logger.info(f"🏥 Disease check requested for plant type: {plant_type}")
        
        # Model ile hastalık tahmini
        from services.model_service import ModelService
        model_service = ModelService()
        
        result = model_service.predict_disease(image_file, plant_type)
        
        if "error" in result:
            return jsonify({
                "status": "error",
                "message": result["error"]
            }), 500
        
        # Sonucu Firebase'e kaydet
        from services.firebase_service import FirebaseService
        firebase_service = FirebaseService()
        
        # Görseli Firebase Storage'a yükle
        image_url = firebase_service.upload_image(image_file, f"disease_checks")
        
        disease_record = {
            "plant_id": plant_id,
            "plant_type": plant_type,
            "image_url": image_url,
            "is_healthy": result.get("is_healthy"),
            "disease_status": result.get("disease_status"),
            "confidence": result.get("confidence"),
            "model_used": result.get("model_used"),
            "timestamp": datetime.now().isoformat()
        }
        firebase_service.save_disease_check(disease_record)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in disease check: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Disease check failed: {str(e)}"
        }), 500

@plant_bp.route('/plant-selection', methods=['POST'])
def plant_selection():
    """Seçilen bitki türünü kaydet (tek kullanıcı)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data received"
            }), 400
        
        selected_plant = data.get('selected_plant')
        model_predictions = data.get('model_predictions', [])
        image_url = data.get('image_url')
        plant_id = data.get('plant_id', 'main_plant')
        
        if not selected_plant:
            return jsonify({
                "status": "error",
                "message": "selected_plant is required"
            }), 400
        
        # Seçilen bitki mevcut listede mi kontrol et
        from config import Config
        if selected_plant not in Config.AVAILABLE_PLANTS:
            return jsonify({
                "status": "error",
                "message": f"Selected plant '{selected_plant}' is not in available plants list"
            }), 400
        
        logger.info(f"🌱 Plant selected: {selected_plant}")
        
        # Firebase'e seçimi kaydet
        from services.firebase_service import FirebaseService
        firebase_service = FirebaseService()
        
        selection_record = {
            "plant_id": plant_id,
            "selected_plant": selected_plant,
            "model_predictions": model_predictions,
            "image_url": image_url,
            "timestamp": datetime.now().isoformat()
        }
        firebase_service.save_plant_selection(selection_record)
        
        # Özel model var mı kontrol et
        has_specific_model = selected_plant in Config.SPECIFIC_DISEASE_MODELS
        
        return jsonify({
            "status": "success",
            "message": f"Plant selection saved: {selected_plant}",
            "selected_plant": selected_plant,
            "plant_id": plant_id,
            "has_specific_disease_model": has_specific_model,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error saving plant selection: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to save plant selection: {str(e)}"
        }), 500
