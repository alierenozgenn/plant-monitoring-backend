import firebase_admin
from firebase_admin import credentials, firestore, storage, messaging
import logging
from datetime import datetime, timedelta
import os
from config import Config

logger = logging.getLogger(__name__)

class FirebaseService:
    def __init__(self):
        self.db = None
        self.bucket = None
        self.initialize_firebase()
    
    def initialize_firebase(self):
        """Firebase'i başlat"""
        try:
            if not firebase_admin._apps:
                # Firebase credentials dosyası varsa kullan
                if Config.FIREBASE_CREDENTIALS_PATH and os.path.exists(Config.FIREBASE_CREDENTIALS_PATH):
                    cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS_PATH)
                    firebase_admin.initialize_app(cred, {
                        'storageBucket': 'your-project-id.appspot.com'  # Proje ID'nizi buraya yazın
                    })
                else:
                    # Geliştirme ortamı için mock
                    logger.warning("Firebase credentials not found, running in mock mode")
                    return
                
                self.db = firestore.client()
                self.bucket = storage.bucket()
                logger.info("Firebase initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Firebase: {str(e)}")
    
    # ========== PLANT PROFILE METHODS ==========
    
    def get_plant_profile(self, plant_id):
        """Bitki profilini getir"""
        try:
            if not self.db:
                # Mock data döndür
                return {
                    "plant_id": plant_id,
                    "plant_name": "Test Plant",
                    "plant_type": "Aloe Vera",
                    "moisture_threshold": 30,
                    "location": "Indoor",
                    "created_at": datetime.now().isoformat(),
                    "status": "active",
                    "mock": True
                }
            
            doc_ref = self.db.collection('plant_profiles').document(plant_id)
            doc = doc_ref.get()
            
            if doc.exists:
                profile = doc.to_dict()
                profile['id'] = doc.id
                return profile
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting plant profile: {str(e)}")
            return None
    
    def save_plant_profile(self, profile_data):
        """Yeni bitki profili kaydet"""
        try:
            if not self.db:
                logger.warning("Firebase not initialized, profile saved to mock")
                return True
            
            plant_id = profile_data.get('plant_id')
            doc_ref = self.db.collection('plant_profiles').document(plant_id)
            doc_ref.set(profile_data)
            
            logger.info(f"Plant profile saved: {plant_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving plant profile: {str(e)}")
            return False
    
    def update_plant_profile(self, plant_id, profile_data):
        """Bitki profilini güncelle"""
        try:
            if not self.db:
                logger.warning("Firebase not initialized, profile update mocked")
                return True
            
            doc_ref = self.db.collection('plant_profiles').document(plant_id)
            doc_ref.update(profile_data)
            
            logger.info(f"Plant profile updated: {plant_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating plant profile: {str(e)}")
            return False
    
    def update_plant_settings(self, plant_id, settings_data):
        """Bitki ayarlarını güncelle"""
        try:
            if not self.db:
                logger.warning("Firebase not initialized, settings update mocked")
                return True
            
            doc_ref = self.db.collection('plant_profiles').document(plant_id)
            doc_ref.update(settings_data)
            
            logger.info(f"Plant settings updated: {plant_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating plant settings: {str(e)}")
            return False
    
    # ========== HISTORY METHODS ==========
    
    def save_moisture_data(self, data):
        """Nem verisini Firestore'a kaydet"""
        try:
            if not self.db:
                logger.warning("Firebase not initialized, skipping moisture data save")
                return
            
            collection_ref = self.db.collection('moisture_data')
            collection_ref.add(data)
            logger.info(f"Moisture data saved for plant {data.get('plant_id')}")
            
        except Exception as e:
            logger.error(f"Error saving moisture data: {str(e)}")
    
    def save_sensor_data(self, data):
        """Sensör verisini kaydet"""
        try:
            if not self.db:
                logger.warning("Firebase not initialized, skipping sensor data save")
                return
            
            collection_ref = self.db.collection('sensor_data')
            collection_ref.add(data)
            logger.info(f"Sensor data saved for plant {data.get('plant_id')}")
            
        except Exception as e:
            logger.error(f"Error saving sensor data: {str(e)}")
    
    def save_watering_history(self, data):
        """Sulama geçmişini Firestore'a kaydet"""
        try:
            if not self.db:
                logger.warning("Firebase not initialized, skipping watering history save")
                return
            
            collection_ref = self.db.collection('watering_history')
            collection_ref.add(data)
            logger.info(f"Watering history saved for plant {data.get('plant_id')}")
            
        except Exception as e:
            logger.error(f"Error saving watering history: {str(e)}")
    
    def save_disease_check(self, data):
        """Hastalık kontrolü sonucunu Firestore'a kaydet"""
        try:
            if not self.db:
                logger.warning("Firebase not initialized, skipping disease check save")
                return
            
            collection_ref = self.db.collection('disease_checks')
            collection_ref.add(data)
            logger.info(f"Disease check saved for plant {data.get('plant_id')}")
            
        except Exception as e:
            logger.error(f"Error saving disease check: {str(e)}")
    
    def save_plant_identification(self, data):
        """Bitki tanıma sonucunu Firestore'a kaydet"""
        try:
            if not self.db:
                logger.warning("Firebase not initialized, skipping plant identification save")
                return
            
            collection_ref = self.db.collection('plant_identifications')
            collection_ref.add(data)
            logger.info(f"Plant identification saved for plant {data.get('plant_id')}")
            
        except Exception as e:
            logger.error(f"Error saving plant identification: {str(e)}")
    
    def save_plant_selection(self, data):
        """Bitki seçimini kaydet"""
        try:
            if not self.db:
                logger.warning("Firebase not initialized, skipping plant selection save")
                return
            
            collection_ref = self.db.collection('plant_selections')
            collection_ref.add(data)
            logger.info(f"Plant selection saved for plant {data.get('plant_id')}")
            
        except Exception as e:
            logger.error(f"Error saving plant selection: {str(e)}")
    
    # ========== GET HISTORY METHODS ==========
    
    def get_watering_history(self, plant_id, limit=50):
        """Sulama geçmişini getir"""
        try:
            if not self.db:
                # Mock data döndür
                return [
                    {
                        "id": "mock_1",
                        "plant_id": plant_id,
                        "type": "manual",
                        "duration": 3,
                        "timestamp": datetime.now().isoformat(),
                        "triggered_by": "mobile_app",
                        "mock": True
                    }
                ]
            
            query = self.db.collection('watering_history')
            query = query.where('plant_id', '==', plant_id)
            query = query.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)
            
            docs = query.stream()
            history = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                history.append(data)
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting watering history: {str(e)}")
            return []
    
    def get_moisture_history(self, plant_id, limit=100, days=7):
        """Nem geçmişini getir"""
        try:
            if not self.db:
                # Mock data döndür
                return [
                    {
                        "id": "mock_1",
                        "plant_id": plant_id,
                        "moisture": 35,
                        "temperature": 23.5,
                        "humidity": 60,
                        "timestamp": datetime.now().isoformat(),
                        "mock": True
                    }
                ]
            
            # Son X gün için tarih filtresi
            start_date = datetime.now() - timedelta(days=days)
            
            query = self.db.collection('moisture_data')
            query = query.where('plant_id', '==', plant_id)
            query = query.where('timestamp', '>=', start_date.isoformat())
            query = query.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)
            
            docs = query.stream()
            history = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                history.append(data)
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting moisture history: {str(e)}")
            return []
    
    def get_disease_history(self, plant_id, limit=50):
        """Hastalık kontrol geçmişini getir"""
        try:
            if not self.db:
                # Mock data döndür
                return [
                    {
                        "id": "mock_1",
                        "plant_id": plant_id,
                        "plant_type": "Aloe Vera",
                        "is_healthy": True,
                        "disease_status": "Healthy",
                        "confidence": 0.92,
                        "timestamp": datetime.now().isoformat(),
                        "mock": True
                    }
                ]
            
            query = self.db.collection('disease_checks')
            query = query.where('plant_id', '==', plant_id)
            query = query.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)
            
            docs = query.stream()
            history = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                history.append(data)
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting disease history: {str(e)}")
            return []
    
    # ========== UTILITY METHODS ==========
    
    def upload_image(self, image_file, path):
        """Görseli Firebase Storage'a yükle"""
        try:
            if not self.bucket:
                logger.warning("Firebase Storage not initialized")
                return f"mock_image_url_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            
            # Dosya adı oluştur
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{path}/{timestamp}_{image_file.filename}"
            
            # Dosyayı yükle
            blob = self.bucket.blob(filename)
            blob.upload_from_file(image_file, content_type=image_file.content_type)
            
            # Public URL al
            blob.make_public()
            return blob.public_url
            
        except Exception as e:
            logger.error(f"Error uploading image: {str(e)}")
            return None
    
    def send_notification_to_user(self, plant_id, title, message):
        """Kullanıcıya push notification gönder"""
        try:
            # Bu kısım FCM token'ları ile çalışır
            # Şimdilik log olarak bırakıyoruz
            logger.info(f"📱 NOTIFICATION - Plant: {plant_id}, Title: {title}, Message: {message}")
            
            # Gerçek implementasyon:
            # message = messaging.Message(
            #     notification=messaging.Notification(
            #         title=title,
            #         body=message,
            #     ),
            #     token=user_fcm_token,
            # )
            # response = messaging.send(message)
            
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
