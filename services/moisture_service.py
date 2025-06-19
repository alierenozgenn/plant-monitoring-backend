"""
Nem seviyesi kontrolü ve sulama karar servisi
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MoistureService:
    def __init__(self):
        # Bekleyen sulama komutları (basit implementasyon)
        self.pending_commands = {}  # plant_id: command_info
        
        # Nem eşik değerleri
        self.default_moisture_threshold = 30  # %30
        self.critical_moisture_threshold = 20  # %20
    
    def check_moisture_level(self, plant_id, moisture_level):
        """
        Nem seviyesini kontrol et ve uyarı gerekip gerekmediğini belirle
        """
        try:
            # Bitki profilinden eşik değerini al
            from services.firebase_service import FirebaseService
            firebase_service = FirebaseService()
            
            profile = firebase_service.get_plant_profile(plant_id)
            threshold = profile.get('moisture_threshold', self.default_moisture_threshold) if profile else self.default_moisture_threshold
            
            logger.info(f"Moisture check: {moisture_level}% (threshold: {threshold}%)")
            
            # Kritik seviye kontrolü
            if moisture_level <= self.critical_moisture_threshold:
                logger.warning(f"🚨 CRITICAL moisture level for {plant_id}: {moisture_level}%")
                return "critical"
            
            # Normal eşik kontrolü
            elif moisture_level <= threshold:
                logger.warning(f"⚠️ Low moisture level for {plant_id}: {moisture_level}%")
                return "low"
            
            else:
                logger.info(f"✅ Moisture level OK for {plant_id}: {moisture_level}%")
                return "normal"
                
        except Exception as e:
            logger.error(f"Error checking moisture level: {str(e)}")
            return "error"
    
    def add_water_command(self, plant_id, duration=3, source="manual"):
        """Sulama komutu ekle"""
        try:
            command_info = {
                "timestamp": datetime.now().isoformat(),
                "duration": duration,
                "source": source,
                "status": "pending"
            }
            
            self.pending_commands[plant_id] = command_info
            logger.info(f"💧 Water command added for {plant_id}: {duration}s ({source})")
            return True
            
        except Exception as e:
            logger.error(f"Error adding water command: {str(e)}")
            return False
    
    def check_pending_water_command(self, plant_id):
        """Bekleyen sulama komutu var mı kontrol et"""
        return plant_id in self.pending_commands
    
    def clear_water_command(self, plant_id):
        """Sulama komutunu temizle"""
        if plant_id in self.pending_commands:
            command_info = self.pending_commands[plant_id]
            del self.pending_commands[plant_id]
            logger.info(f"Water command cleared for plant {plant_id}")
            return command_info
        return None
    
    def get_pending_commands(self):
        """Tüm bekleyen komutları getir"""
        return self.pending_commands.copy()
    
    def should_auto_water(self, plant_id, moisture_level):
        """Otomatik sulama yapılmalı mı?"""
        try:
            # Bitki profilinden otomatik sulama ayarını kontrol et
            from services.firebase_service import FirebaseService
            firebase_service = FirebaseService()
            
            profile = firebase_service.get_plant_profile(plant_id)
            
            if not profile:
                return False
            
            auto_watering_enabled = profile.get('auto_watering', True)
            threshold = profile.get('moisture_threshold', self.default_moisture_threshold)
            
            if not auto_watering_enabled:
                logger.info(f"Auto watering disabled for {plant_id}")
                return False
            
            if moisture_level <= threshold:
                logger.info(f"Auto watering recommended for {plant_id}: {moisture_level}% <= {threshold}%")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking auto water condition: {str(e)}")
            return False
