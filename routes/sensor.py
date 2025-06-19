"""
ESP32 haberleşme route'ları
Tek kullanıcı sistemi için optimize edildi
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

# Blueprint oluştur
sensor_bp = Blueprint('sensor', __name__)
logger = logging.getLogger(__name__)

@sensor_bp.route('/pump-status', methods=['POST'])
def receive_pump_status():
    """
    ESP32'den pompa durumu bilgisi al
    Arduino pompa çalıştırdığında ESP32 bunu Flask'a bildirir
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data received"
            }), 400
        
        pump_active = data.get('pumpActive', False)
        plant_id = data.get('plant_id', 'main_plant')  # Tek bitki
        
        logger.info(f"📡 ESP32 pump status: {'ACTIVE' if pump_active else 'INACTIVE'} for plant {plant_id}")
        
        # Firebase'e kaydet
        from services.firebase_service import FirebaseService
        firebase_service = FirebaseService()
        
        if pump_active:
            # Pompa aktifse sulama geçmişine kaydet
            watering_data = {
                "plant_id": plant_id,
                "type": "automatic",
                "duration": 3,  # ESP32'de 3 saniye
                "timestamp": datetime.now().isoformat(),
                "triggered_by": "arduino_sensor",
                "pump_status": "active",
                "source": "esp32"
            }
            firebase_service.save_watering_history(watering_data)
        
        return jsonify({
            "status": "success",
            "message": "Pump status received and processed",
            "pump_active": pump_active,
            "plant_id": plant_id,
            "timestamp": datetime.now().isoformat(),
            "action_taken": "logged_to_firebase" if pump_active else "status_recorded"
        })
    
    except Exception as e:
        logger.error(f"Error receiving pump status: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to process pump status: {str(e)}"
        }), 500

@sensor_bp.route('/should-water', methods=['GET'])
def should_water():
    """
    ESP32'nin kontrol ettiği sulama komutu endpoint'i
    Mobil uygulamadan manuel sulama komutu geldiğinde ESP32'ye "true" döndürür
    """
    try:
        plant_id = request.args.get('plant_id', 'main_plant')  # Tek bitki
        
        # Bekleyen sulama komutlarını kontrol et
        from routes.water import check_pending_water_command, clear_water_command
        
        has_pending_command = check_pending_water_command(plant_id)
        
        if has_pending_command:
            # Komutu temizle (bir kez kullanım)
            clear_water_command(plant_id)
            logger.info(f"💧 Water command sent to ESP32 for plant: {plant_id}")
            return "true", 200, {'Content-Type': 'text/plain'}
        
        # Komut yoksa false döndür
        return "false", 200, {'Content-Type': 'text/plain'}
    
    except Exception as e:
        logger.error(f"Error checking water command: {str(e)}")
        return "false", 200, {'Content-Type': 'text/plain'}

@sensor_bp.route('/sensor-data', methods=['POST'])
def receive_sensor_data():
    """
    ESP32'den detaylı sensör verisi al (nem, sıcaklık, nem)
    Gelecekte ESP32'ye nem sensörü eklenirse kullanılacak
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No sensor data received"
            }), 400
        
        # Gelen veri formatı:
        # {
        #   "plant_id": "main_plant",
        #   "moisture": 35,
        #   "temperature": 23.5,
        #   "humidity": 60,
        #   "timestamp": "2024-01-15T10:30:00Z"
        # }
        
        plant_id = data.get('plant_id', 'main_plant')  # Tek bitki
        moisture = data.get('moisture')
        temperature = data.get('temperature')
        humidity = data.get('humidity')
        
        logger.info(f"📊 Sensor data from {plant_id}: Moisture={moisture}%, Temp={temperature}°C, Humidity={humidity}%")
        
        # Firebase'e sensör verisini kaydet
        from services.firebase_service import FirebaseService
        firebase_service = FirebaseService()
        
        sensor_data = {
            "plant_id": plant_id,
            "moisture": moisture,
            "temperature": temperature,
            "humidity": humidity,
            "timestamp": data.get('timestamp', datetime.now().isoformat()),
            "source": "esp32_sensor"
        }
        firebase_service.save_sensor_data(sensor_data)
        
        return jsonify({
            "status": "success",
            "message": "Sensor data processed successfully",
            "plant_id": plant_id,
            "moisture_level": moisture,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error processing sensor data: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to process sensor data: {str(e)}"
        }), 500
