import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

class Config:
    # Flask ayarları
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # ESP32 ayarları
    ESP32_IP = os.environ.get('ESP32_IP') or '192.168.1.100'
    ESP32_PORT = os.environ.get('ESP32_PORT') or '80'
    
    # Firebase ayarları
    FIREBASE_CREDENTIALS_PATH = os.environ.get('FIREBASE_CREDENTIALS_PATH')
    
    # Model dosya yolları (TFLite)
    PLANT_TYPE_MODEL_PATH = 'models/tur_tespit.tflite'
    GENERAL_DISEASE_MODEL_PATH = 'models/genel_hasta.tflite'
    
    # Özel hastalık modelleri (TFLite) - Hepsini geri ekledim
    SPECIFIC_DISEASE_MODELS = {
        'Aloe Vera': 'models/aloe_vera.tflite',
        'Barış Çiçeği': 'models/baris_cicegi.tflite',
        'Kaktüs': 'models/kaktus.tflite',
        'Orkide': 'models/orkide.tflite',
        'Paşa Kılıcı': 'models/pasakilici.tflite',
        'Sukulent': 'models/sukulent.tflite'
    }
    
    # Hastalık tespit eşik değeri
    DISEASE_THRESHOLD = 0.85  # %85 üstü hasta kabul edilir
    
    # Genişletilmiş Türkçe bitki listesi
    AVAILABLE_PLANTS = [
        # Orijinal liste
        'Afrika Menekşesi',
        'Aloe Vera',
        'Antoryum',
        'Aptal Kamışı',
        'Atatürk Çiçeği',
        'Barış Çiçeği',
        'Begonya',
        'Benekli Bitki',
        'Drasena',
        'Dua Çiçeği',
        'Dökme Demir Bitkisi',
        'Eğreltiotu',
        'Fil Kulağı',
        'Kaktüs',
        'Kalathea',
        'Kauçuk Bitkisi',
        'Krizantem',
        'Monstera',
        'Orkide',
        'Palmiye',
        'Para Ağacı',
        'Paşa Kılıcı',
        'Sarmaşık (Pothos)',
        'Sukulent',
        'Telgraf Çiçeği',
        'Yeşim Bitkisi',
        'Yılbaşı Kaktüsü',
        'ZZ Bitkisi',
        'Çin Herdemyeşili',
        'Çin Para Bitkisi',
        'Şeflera',
        
        # Ek Türkçe ev bitkileri
        'Ficus Benjamin',
        'Bambu Palmiyesi',
        'Lavanta',
        'Biberiye',
        'Nane',
        'Fesleğen',
        'Adaçayı',
        'Karanfil',
        'Petunya',
        'Sardunya',
        'Menekşe',
        'Begonvil',
        'Yasemin',
        'Gül',
        'Papatya',
        'Çiçek Bambusu',
        'Kedi Otu',
        'Köpek Dili',
        'Aslan Ağzı',
        'Gelincik',
        'Lale',
        'Sümbül',
        'Nergis',
        'Zambak',
        'İris',
        'Kadife Çiçeği',
        'Ateş Çiçeği',
        'Güneş Çiçeği',
        'Ayçiçeği',
        'Çan Çiçeği',
        'Yıldız Çiçeği',
        'Prenses Çiçeği',
        'Kraliçe Çiçeği',
        'Sultan Çiçeği',
        'Hanım Eli',
        'Gelin Çiçeği',
        'Damat Çiçeği',
        'Aşk Çiçeği',
        'Mutluluk Çiçeği',
        'Şans Çiçeği',
        'Bereket Çiçeği',
        'Sağlık Çiçeği',
        'Huzur Çiçeği',
        'Barış Otu',
        'Sevgi Çiçeği',
        'Dostluk Çiçeği',
        'Umut Çiçeği',
        'Hayal Çiçeği',
        'Rüya Çiçeği',
        'Melek Çiçeği',
        'Peri Çiçeği',
        'Ejder Çiçeği',
        'Aslan Çiçeği',
        'Kartal Çiçeği',
        'Güvercin Çiçeği',
        'Kelebek Çiçeği',
        'Arı Çiçeği',
        'Böcek Çiçeği',
        'Yılan Çiçeği',
        'Kedi Çiçeği',
        'Köpek Çiçeği',
        'At Çiçeği',
        'İnek Çiçeği',
        'Koyun Çiçeği',
        'Keçi Çiçeği',
        'Tavuk Çiçeği',
        'Horoz Çiçeği',
        'Balık Çiçeği',
        'Kuş Çiçeği',
        'Kartal Pençesi',
        'Aslan Pençesi',
        'Kaplan Pençesi',
        'Kurt Pençesi',
        'Ayı Pençesi',
        'Tilki Kuyruğu',
        'Tavşan Kulağı',
        'Geyik Boynuzu',
        'Fil Hortumu',
        'Zürafa Boynu',
        'Deve Hörgücü',
        'At Kuyruğu',
        'İnek Dili',
        'Koyun Kulağı',
        'Keçi Sakalı',
        'Horoz İbrişi',
        'Tavuk Tüyü',
        'Güvercin Göğsü',
        'Kartal Kanadı',
        'Kelebek Kanadı',
        'Arı Kovanı',
        'Bal Peteği',
        'Çiçek Balı',
        'Orman Çiçeği',
        'Dağ Çiçeği',
        'Deniz Çiçeği',
        'Göl Çiçeği',
        'Nehir Çiçeği',
        'Çay Çiçeği',
        'Su Çiçeği',
        'Buz Çiçeği',
        'Kar Çiçeği',
        'Yağmur Çiçeği',
        'Güneş Işığı',
        'Ay Işığı',
        'Yıldız Işığı',
        'Şafak Çiçeği',
        'Gün Doğumu',
        'Gün Batımı',
        'Akşam Çiçeği',
        'Gece Çiçeği',
        'Sabah Çiçeği',
        'Öğle Çiçeği'
    ]
    
    # Diğer ayarlar
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
