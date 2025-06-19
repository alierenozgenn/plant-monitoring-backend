"""
Smart Plant Monitoring System
Render deployment için optimize edildi
"""

from flask import Flask, jsonify
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
    try:
        from config import Config
        app.config.from_object(Config)
    except ImportError:
        # Config dosyası yoksa varsayılan ayarlar
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
        logging.warning("⚠️ Config.py bulunamadı, varsayılan ayarlar kullanılıyor")
    
    # Logging ayarları
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Blueprint'leri kaydet
    register_blueprints(app)
    
    # Servisleri başlat
    initialize_services(app)
    
    # Ana endpoint (sistem durumu için)
    @app.route('/')
    def home():
        return jsonify({
            "message": "🌱 Smart Plant Monitoring API",
            "status": "running",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "endpoints": {
                "sensor": "/api/sensor",
                "water": "/api/water", 
                "plant": "/api/plant",
                "profile": "/api/profile"
            }
        })
    
    # Health check endpoint (Render için)
    @app.route('/health')
    def health():
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        }), 200
    
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
        
    except ImportError as e:
        logger.error(f"❌ Blueprint import error: {str(e)}")
        logger.warning("⚠️ Some routes may not be available")
    except Exception as e:
        logger.error(f"❌ Error registering blueprints: {str(e)}")

def initialize_services(app):
    """Servisleri başlat ve durumlarını kontrol et"""
    
    logger = logging.getLogger(__name__)
    
    with app.app_context():
        try:
            # Model servisini başlat
            try:
                from services.model_service import ModelService
                model_service = ModelService()
                
                # Model durumlarını logla
                models_loaded = len(getattr(model_service, 'specific_disease_interpreters', {}))
                plant_model = getattr(model_service, 'plant_type_interpreter', None) is not None
                general_model = getattr(model_service, 'general_disease_interpreter', None) is not None
                
                logger.info(f"🤖 AI Models for Flutter:")
                logger.info(f"   Plant Type Model: {'✅' if plant_model else '❌ (Mock mode)'}")
                logger.info(f"   General Disease Model: {'✅' if general_model else '❌ (Mock mode)'}")
                logger.info(f"   Specific Disease Models: {models_loaded}/6")
                
            except ImportError:
                logger.warning("⚠️ Model service not available, using mock mode")
            
            # Firebase servisini başlat
            try:
                from services.firebase_service import FirebaseService
                firebase_service = FirebaseService()
                
                firebase_connected = getattr(firebase_service, 'db', None) is not None
                logger.info(f"🔥 Firebase for Flutter: {'✅ Connected' if firebase_connected else '⚠️ Mock Mode'}")
                
            except ImportError:
                logger.warning("⚠️ Firebase service not available, using mock mode")
            
            # ESP32 servisini başlat
            try:
                from services.esp32_service import ESP32Service
                esp32_service = ESP32Service()
                logger.info(f"📡 ESP32 Service: ✅ Ready for Flutter")
                
            except ImportError:
                logger.warning("⚠️ ESP32 service not available, using mock mode")
            
            # Sistem durumu özeti
            logger.info("📱 Smart Plant Monitoring API ready for Flutter!")
            logger.info(f"🎯 System Mode: Single User + Single Plant")
            
        except Exception as e:
            logger.error(f"❌ Error initializing services: {str(e)}")
            logger.warning("⚠️ Some services failed, but API will work in mock mode")

# Flask uygulamasını oluştur
app = create_app()

# Ana çalıştırma
if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    
    # Port ayarı (Render için)
    port = int(os.environ.get('PORT', 5000))
    
    # Debug mode (production'da False)
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    # Başlatma mesajları
    print("=" * 60)
    print("📱 Smart Plant Monitoring API for Flutter")
    print("=" * 60)
    print(f"📍 Port: {port}")
    print(f"🔧 Debug Mode: {debug_mode}")
    print(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print("🚀 Ready for Flutter connection!")
    
    try:
        app.run(
            host='0.0.0.0',  # Render için
            port=port,
            debug=debug_mode
        )
    except KeyboardInterrupt:
        print("\n🛑 API stopped")
    except Exception as e:
        print(f"\n❌ API error: {str(e)}")