"""
Smart Plant Monitoring System
Flutter mobil uygulaması için optimize edildi
"""

from flask import Flask
from flask_cors import CORS
import logging
import os
from datetime import datetime

def create_app():
    """Flask uygulamasını oluştur ve yapılandır"""
    
    # Flask uygulaması oluştur
    app = Flask(__name__)
    
    # Flutter için CORS ayarları
    CORS(app, 
         origins=["*"],  # Flutter için tüm origin'lere izin ver
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"])
    
    # Konfigürasyonu yükle
    from config import Config
    app.config.from_object(Config)
    
    # Logging ayarları
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Blueprint'leri kaydet
    register_blueprints(app)
    
    # Servisleri başlat
    initialize_services(app)
    
    return app

def register_blueprints(app):
    """Tüm Blueprint'leri kaydet"""
    
    logger = logging.getLogger(__name__)
    
    try:
        # Ana sayfa ve sistem
        from routes.main import main_bp
        app.register_blueprint(main_bp)
        logger.info("✅ Main blueprint registered")
        
        # ESP32 haberleşme
        from routes.sensor import sensor_bp
        app.register_blueprint(sensor_bp, url_prefix='/api')
        logger.info("✅ Sensor blueprint registered")
        
        # Sulama sistemi
        from routes.water import water_bp
        app.register_blueprint(water_bp, url_prefix='/api')
        logger.info("✅ Water blueprint registered")
        
        # AI modelleri (bitki tanıma + hastalık)
        from routes.plant import plant_bp
        app.register_blueprint(plant_bp, url_prefix='/api')
        logger.info("✅ Plant blueprint registered")
        
        # Bitki profilleri
        from routes.profile import profile_bp
        app.register_blueprint(profile_bp, url_prefix='/api')
        logger.info("✅ Profile blueprint registered")
        
        logger.info("🎯 All blueprints registered for Flutter")
        
    except Exception as e:
        logger.error(f"❌ Error registering blueprints: {str(e)}")
        raise

def initialize_services(app):
    """Servisleri başlat ve durumlarını kontrol et"""
    
    logger = logging.getLogger(__name__)
    
    with app.app_context():
        try:
            # Model servisini başlat
            from services.model_service import ModelService
            model_service = ModelService()
            
            # Model durumlarını logla
            models_loaded = len(model_service.specific_disease_interpreters)
            plant_model = model_service.plant_type_interpreter is not None
            general_model = model_service.general_disease_interpreter is not None
            
            logger.info(f"🤖 AI Models for Flutter:")
            logger.info(f"   Plant Type Model: {'✅' if plant_model else '❌ (Mock mode)'}")
            logger.info(f"   General Disease Model: {'✅' if general_model else '❌ (Mock mode)'}")
            logger.info(f"   Specific Disease Models: {models_loaded}/6")
            
            # Firebase servisini başlat
            from services.firebase_service import FirebaseService
            firebase_service = FirebaseService()
            
            firebase_connected = firebase_service.db is not None
            logger.info(f"🔥 Firebase for Flutter: {'✅ Connected' if firebase_connected else '⚠️ Mock Mode'}")
            
            # ESP32 servisini başlat
            from services.esp32_service import ESP32Service
            esp32_service = ESP32Service()
            logger.info(f"📡 ESP32 Service: ✅ Ready for Flutter")
            
            # Sistem durumu özeti
            logger.info("📱 Smart Plant Monitoring API ready for Flutter!")
            logger.info(f"🔗 Flutter can connect to: http://YOUR_IP:5000")
            logger.info(f"🎯 System Mode: Single User + Single Plant")
            
        except Exception as e:
            logger.error(f"❌ Error initializing services: {str(e)}")
            logger.warning("⚠️ Some services failed, but API will work in mock mode")

# Flask uygulamasını oluştur
app = create_app()

# Ana çalıştırma
if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    
    # Port ayarı
    port = int(os.environ.get('PORT', 5000))
    
    # Debug mode
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    # Başlatma mesajları
    print("=" * 60)
    print("📱 Smart Plant Monitoring API for Flutter")
    print("=" * 60)
    print(f"📍 Port: {port}")
    print(f"🔧 Debug Mode: {debug_mode}")
    print(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Flutter için endpoint'leri listele
    with app.app_context():
        print("📱 Flutter API Endpoints:")
        print("   System:")
        print("     GET  /              - API info")
        print("     GET  /health        - Health check")
        print("     GET  /api/system-status - Detailed status")
        print("   Plant Management:")
        print("     GET  /api/plants           - Available plants")
        print("     POST /api/identify-plant   - Plant identification")
        print("     POST /api/plant-selection  - Save plant choice")
        print("     GET  /api/plant-profile    - Get plant profile")
        print("     POST /api/plant-profile    - Create/update profile")
        print("   Watering:")
        print("     POST /api/trigger-watering  - Manual watering")
        print("     GET  /api/watering-history  - Watering history")
        print("     GET  /api/moisture-history  - Moisture history")
        print("   Health:")
        print("     POST /api/check-disease     - Disease detection")
        print("     GET  /api/disease-history   - Disease history")
        print("   ESP32:")
        print("     POST /api/pump-status      - Pump status from ESP32")
        print("     GET  /api/should-water     - Water command for ESP32")
        print("=" * 60)
        print("🚀 Ready for Flutter connection!")
    
    try:
        app.run(
            host='0.0.0.0',  # Flutter'dan erişim için
            port=port,
            debug=debug_mode
        )
    except KeyboardInterrupt:
        print("\n🛑 API stopped")
    except Exception as e:
        print(f"\n❌ API error: {str(e)}")
