import numpy as np
from PIL import Image
import tensorflow as tf
import logging
import os
from config import Config

logger = logging.getLogger(__name__)

class ModelService:
    def __init__(self):
        self.plant_type_interpreter = None
        self.general_disease_interpreter = None
        self.specific_disease_interpreters = {}
        self.load_models()
    
    def load_models(self):
        """TFLite modellerini yükle - farklı yöntemlerle dene"""
        try:
            # Bitki türü tespit modeli
            self.plant_type_interpreter = self._load_single_model(
                Config.PLANT_TYPE_MODEL_PATH, "Plant type"
            )
            
            # Genel hastalık tespit modeli
            self.general_disease_interpreter = self._load_single_model(
                Config.GENERAL_DISEASE_MODEL_PATH, "General disease"
            )
            
            # Özel hastalık modellerini yükle
            for plant_type, model_path in Config.SPECIFIC_DISEASE_MODELS.items():
                interpreter = self._load_single_model(model_path, f"{plant_type} disease")
                if interpreter:
                    self.specific_disease_interpreters[plant_type] = interpreter
                    
        except Exception as e:
            logger.error(f"General error in loading TFLite models: {str(e)}")
    
    def _load_single_model(self, model_path, model_name):
        """Tek bir modeli farklı yöntemlerle yüklemeye çalış"""
        if not os.path.exists(model_path):
            logger.warning(f"{model_name} model not found: {model_path}")
            return None
        
        # Dosya boyutunu kontrol et
        file_size = os.path.getsize(model_path)
        logger.info(f"Loading {model_name} model: {model_path} (Size: {file_size} bytes)")
        
        # Yöntem 1: Normal TFLite yükleme
        try:
            interpreter = tf.lite.Interpreter(model_path=model_path)
            interpreter.allocate_tensors()
            logger.info(f"{model_name} TFLite model loaded successfully (Method 1)")
            return interpreter
        except Exception as e1:
            logger.warning(f"Method 1 failed for {model_name}: {str(e1)}")
        
        # Yöntem 2: Experimental delegates olmadan
        try:
            interpreter = tf.lite.Interpreter(
                model_path=model_path,
                experimental_delegates=None
            )
            interpreter.allocate_tensors()
            logger.info(f"{model_name} TFLite model loaded successfully (Method 2)")
            return interpreter
        except Exception as e2:
            logger.warning(f"Method 2 failed for {model_name}: {str(e2)}")
        
        # Yöntem 3: Farklı thread ayarları ile
        try:
            interpreter = tf.lite.Interpreter(
                model_path=model_path,
                num_threads=1
            )
            interpreter.allocate_tensors()
            logger.info(f"{model_name} TFLite model loaded successfully (Method 3)")
            return interpreter
        except Exception as e3:
            logger.warning(f"Method 3 failed for {model_name}: {str(e3)}")
        
        # Yöntem 4: Model dosyasını binary olarak oku
        try:
            with open(model_path, 'rb') as f:
                model_content = f.read()
            
            interpreter = tf.lite.Interpreter(model_content=model_content)
            interpreter.allocate_tensors()
            logger.info(f"{model_name} TFLite model loaded successfully (Method 4)")
            return interpreter
        except Exception as e4:
            logger.error(f"All methods failed for {model_name}: {str(e4)}")
        
        return None
    
    def preprocess_image_for_tflite(self, image_data, target_size=(224, 224)):
        """Görüntüyü TFLite model için hazırla"""
        try:
            # PIL Image'a çevir
            if isinstance(image_data, bytes):
                from io import BytesIO
                image = Image.open(BytesIO(image_data))
            else:
                image = Image.open(image_data)
            
            # RGB'ye çevir
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Boyutlandır
            image = image.resize(target_size)
            
            # NumPy array'e çevir ve normalize et
            image_array = np.array(image, dtype=np.float32) / 255.0
            
            # Batch dimension ekle
            image_array = np.expand_dims(image_array, axis=0)
            
            return image_array
            
        except Exception as e:
            logger.error(f"Error preprocessing image for TFLite: {str(e)}")
            return None
    
    def predict_with_tflite(self, interpreter, image_array):
        """TFLite interpreter ile tahmin yap"""
        try:
            # Input tensor bilgilerini al
            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()
            
            # Input'u set et
            interpreter.set_tensor(input_details[0]['index'], image_array)
            
            # Inference çalıştır
            interpreter.invoke()
            
            # Output'u al
            output_data = interpreter.get_tensor(output_details[0]['index'])
            
            return output_data
            
        except Exception as e:
            logger.error(f"Error in TFLite prediction: {str(e)}")
            return None
    
    def predict_plant_type(self, image_data):
        """Bitki türü tahmini yap - 5 sonuç döndür"""
        try:
            if self.plant_type_interpreter is None:
                # Model yoksa mock data döndür (geliştirme için)
                return self._get_mock_plant_predictions()
            
            processed_image = self.preprocess_image_for_tflite(image_data)
            if processed_image is None:
                return {"error": "Image preprocessing failed"}
            
            # TFLite ile tahmin yap
            predictions = self.predict_with_tflite(self.plant_type_interpreter, processed_image)
            if predictions is None:
                return {"error": "TFLite prediction failed"}
            
            # En yüksek 5 tahmini döndür
            predictions_flat = predictions.flatten()
            top_5_indices = np.argsort(predictions_flat)[-5:][::-1]
            
            results = []
            for i, idx in enumerate(top_5_indices):
                if idx < len(Config.AVAILABLE_PLANTS):
                    confidence = float(predictions_flat[idx])
                    results.append({
                        "plant_type": Config.AVAILABLE_PLANTS[idx],
                        "confidence": confidence,
                        "confidence_percentage": f"{confidence * 100:.1f}%"
                    })
            
            return {
                "status": "success",
                "predictions": results,
                "total_available_plants": len(Config.AVAILABLE_PLANTS),
                "model_used": "tflite"
            }
            
        except Exception as e:
            logger.error(f"Error in plant type prediction: {str(e)}")
            return {"error": str(e)}
    
    def _get_mock_plant_predictions(self):
        """Model yokken test için mock data"""
        import random
        
        # Rastgele 5 bitki seç
        selected_plants = random.sample(Config.AVAILABLE_PLANTS, 5)
        
        results = []
        for i, plant in enumerate(selected_plants):
            confidence = random.uniform(0.6, 0.95)  # Rastgele güven skoru
            results.append({
                "plant_type": plant,
                "confidence": confidence,
                "confidence_percentage": f"{confidence * 100:.1f}%"
            })
        
        # Güven skoruna göre sırala
        results.sort(key=lambda x: x['confidence'], reverse=True)
        
        return {
            "status": "success",
            "predictions": results,
            "total_available_plants": len(Config.AVAILABLE_PLANTS),
            "model_used": "mock",
            "note": "Mock data - TFLite model not loaded"
        }
    
    def predict_disease(self, image_data, plant_type=None):
        """Hibrit hastalık tahmini - özel model varsa onu kullan, yoksa genel model"""
        try:
            processed_image = self.preprocess_image_for_tflite(image_data)
            if processed_image is None:
                return {"error": "Image preprocessing failed"}
            
            model_used = "general"
            interpreter = self.general_disease_interpreter
            
            # Özel model var mı kontrol et
            if plant_type and plant_type in self.specific_disease_interpreters:
                interpreter = self.specific_disease_interpreters[plant_type]
                model_used = "specific"
                logger.info(f"Using specific TFLite model for {plant_type}")
            else:
                logger.info(f"Using general TFLite model for plant type: {plant_type}")
            
            if interpreter is None:
                return {
                    "error": f"No TFLite model available ({'specific' if plant_type in Config.SPECIFIC_DISEASE_MODELS else 'general'})"
                }
            
            # TFLite ile tahmin yap
            prediction = self.predict_with_tflite(interpreter, processed_image)
            if prediction is None:
                return {"error": "TFLite disease prediction failed"}
            
            # Binary classification (Healthy vs Diseased)
            disease_probability = float(prediction[0][0])
            is_diseased = disease_probability > Config.DISEASE_THRESHOLD
            confidence = disease_probability if is_diseased else (1 - disease_probability)
            
            return {
                "status": "success",
                "is_healthy": not is_diseased,
                "is_diseased": is_diseased,
                "disease_status": "Diseased" if is_diseased else "Healthy",
                "disease_probability": disease_probability,
                "disease_percentage": f"{disease_probability * 100:.1f}%",
                "confidence": confidence,
                "confidence_percentage": f"{confidence * 100:.1f}%",
                "model_used": model_used,
                "plant_type": plant_type,
                "threshold_used": f"{Config.DISEASE_THRESHOLD * 100:.0f}%",
                "message": f"Analysis completed using {model_used} TFLite model" + 
                          (f" for {plant_type}" if model_used == "specific" else "")
            }
            
        except Exception as e:
            logger.error(f"Error in disease prediction: {str(e)}")
            return {"error": str(e)}
    
    def get_available_plants(self):
        """Mevcut bitki listesini döndür"""
        return {
            "status": "success",
            "plants": Config.AVAILABLE_PLANTS,
            "total_count": len(Config.AVAILABLE_PLANTS),
            "plants_with_specific_models": list(Config.SPECIFIC_DISEASE_MODELS.keys()),
            "loaded_specific_models": list(self.specific_disease_interpreters.keys()),
            "disease_threshold": f"{Config.DISEASE_THRESHOLD * 100:.0f}%"
        }
