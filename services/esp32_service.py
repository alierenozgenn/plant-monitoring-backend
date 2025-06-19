import requests
import logging
from config import Config

logger = logging.getLogger(__name__)

class ESP32Service:
    def __init__(self):
        self.esp32_base_url = f"http://{Config.ESP32_IP}:{Config.ESP32_PORT}"
    
    def send_water_command(self, plant_id, duration=5):
        """ESP32'ye sulama komutu gönder"""
        try:
            url = f"{self.esp32_base_url}/water"
            payload = {
                "plant_id": plant_id,
                "duration": duration
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Water command sent successfully to ESP32")
                return True
            else:
                logger.error(f"ESP32 water command failed: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending water command to ESP32: {str(e)}")
            return False
    
    def get_sensor_data(self):
        """ESP32'den anlık sensör verilerini al"""
        try:
            url = f"{self.esp32_base_url}/sensors"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get sensor data: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting sensor data from ESP32: {str(e)}")
            return None
    
    def request_plant_image(self):
        """ESP32'den bitki görüntüsü iste"""
        try:
            url = f"{self.esp32_base_url}/capture"
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                return response.content  # Binary image data
            else:
                logger.error(f"Failed to get plant image: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting plant image from ESP32: {str(e)}")
            return None
