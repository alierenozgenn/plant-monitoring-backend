"""
Bildirim servisi
Push notification, email, SMS gibi bildirimler
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.notification_history = []
        self.max_history = 100
    
    def send_moisture_alert(self, plant_id, moisture_level, alert_type="low"):
        """Nem seviyesi uyarısı gönder"""
        try:
            if alert_type == "critical":
                title = "🚨 Kritik Nem Seviyesi!"
                message = f"Bitkinin nem seviyesi çok düşük: %{moisture_level}. Acil sulama gerekiyor!"
                priority = "high"
            elif alert_type == "low":
                title = "⚠️ Düşük Nem Seviyesi"
                message = f"Bitkinin nem seviyesi düşük: %{moisture_level}. Sulama zamanı gelmiş olabilir."
                priority = "normal"
            else:
                title = "📊 Nem Seviyesi Bildirimi"
                message = f"Bitkinin nem seviyesi: %{moisture_level}"
                priority = "low"
            
            notification = {
                "id": len(self.notification_history) + 1,
                "plant_id": plant_id,
                "type": "moisture_alert",
                "title": title,
                "message": message,
                "priority": priority,
                "moisture_level": moisture_level,
                "timestamp": datetime.now().isoformat(),
                "status": "sent"
            }
            
            # Geçmişe ekle
            self._add_to_history(notification)
            
            # Gerçek bildirim gönderme (şimdilik log)
            logger.info(f"📱 NOTIFICATION: {title} - {message}")
            
            return notification
            
        except Exception as e:
            logger.error(f"Error sending moisture alert: {str(e)}")
            return None
    
    def send_watering_notification(self, plant_id, watering_type="manual", duration=3):
        """Sulama bildirimi gönder"""
        try:
            if watering_type == "automatic":
                title = "💧 Otomatik Sulama Yapıldı"
                message = f"Sistem düşük nem algıladı ve {duration} saniye sulama yaptı."
            else:
                title = "💧 Manuel Sulama Yapıldı"
                message = f"Manuel sulama komutu ile {duration} saniye sulama yapıldı."
            
            notification = {
                "id": len(self.notification_history) + 1,
                "plant_id": plant_id,
                "type": "watering_notification",
                "title": title,
                "message": message,
                "priority": "normal",
                "watering_type": watering_type,
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
                "status": "sent"
            }
            
            # Geçmişe ekle
            self._add_to_history(notification)
            
            # Log
            logger.info(f"📱 NOTIFICATION: {title} - {message}")
            
            return notification
            
        except Exception as e:
            logger.error(f"Error sending watering notification: {str(e)}")
            return None
    
    def send_disease_alert(self, plant_id, disease_status, confidence):
        """Hastalık uyarısı gönder"""
        try:
            if disease_status == "Diseased":
                title = "🏥 Hastalık Tespit Edildi!"
                message = f"AI analizi bitkide hastalık belirtisi tespit etti. Güven: %{confidence:.1f}"
                priority = "high"
            else:
                title = "✅ Bitki Sağlıklı"
                message = f"AI analizi bitkinin sağlıklı olduğunu gösteriyor. Güven: %{confidence:.1f}"
                priority = "low"
            
            notification = {
                "id": len(self.notification_history) + 1,
                "plant_id": plant_id,
                "type": "disease_alert",
                "title": title,
                "message": message,
                "priority": priority,
                "disease_status": disease_status,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat(),
                "status": "sent"
            }
            
            # Geçmişe ekle
            self._add_to_history(notification)
            
            # Log
            logger.info(f"📱 NOTIFICATION: {title} - {message}")
            
            return notification
            
        except Exception as e:
            logger.error(f"Error sending disease alert: {str(e)}")
            return None
    
    def get_notification_history(self, plant_id=None, limit=50):
        """Bildirim geçmişini getir"""
        try:
            history = self.notification_history.copy()
            
            # Plant ID filtresi
            if plant_id:
                history = [n for n in history if n.get('plant_id') == plant_id]
            
            # Tarihe göre sırala (en yeni önce)
            history.sort(key=lambda x: x['timestamp'], reverse=True)
            
            # Limit uygula
            return history[:limit]
            
        except Exception as e:
            logger.error(f"Error getting notification history: {str(e)}")
            return []
    
    def _add_to_history(self, notification):
        """Bildirimi geçmişe ekle"""
        self.notification_history.append(notification)
        
        # Geçmiş boyutunu kontrol et
        if len(self.notification_history) > self.max_history:
            self.notification_history = self.notification_history[-self.max_history:]
    
    def clear_history(self):
        """Bildirim geçmişini temizle"""
        self.notification_history.clear()
        logger.info("Notification history cleared")
    
    def get_stats(self):
        """Bildirim istatistikleri"""
        try:
            total = len(self.notification_history)
            
            if total == 0:
                return {"total": 0}
            
            # Tiplere göre sayım
            types = {}
            priorities = {}
            
            for notification in self.notification_history:
                ntype = notification.get('type', 'unknown')
                priority = notification.get('priority', 'unknown')
                
                types[ntype] = types.get(ntype, 0) + 1
                priorities[priority] = priorities.get(priority, 0) + 1
            
            return {
                "total": total,
                "by_type": types,
                "by_priority": priorities,
                "last_notification": self.notification_history[-1]['timestamp'] if total > 0 else None
            }
            
        except Exception as e:
            logger.error(f"Error getting notification stats: {str(e)}")
            return {"total": 0, "error": str(e)}
