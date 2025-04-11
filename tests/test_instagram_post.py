import os
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pytest
import logging
from dotenv import load_dotenv

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()

class TestInstagramBot:
    def setup_method(self):
        # Configuration pour l'émulateur Android Studio
        self.desired_caps = {
            'platformName': 'Android',
            'automationName': 'UiAutomator2',
            'deviceName': 'Pixel_6_API_33',  # Nom de l'émulateur Android Studio
            'platformVersion': '13.0',  # Version Android de l'émulateur
            'appPackage': 'com.instagram.android',
            'appActivity': 'com.instagram.mainactivity.MainActivity',
            'noReset': True,
            'fullReset': False
        }
        
        # Connexion à Appium
        self.driver = webdriver.Remote('http://localhost:4723/wd/hub', self.desired_caps)
        self.driver.implicitly_wait(10)

    def test_post_photo(self):
        try:
            # Chemin vers une photo de test
            test_image = os.path.join(os.path.dirname(__file__), 'test_media', 'test_photo.jpg')
            test_caption = "Test post automatisé #test"

            # Cliquer sur le bouton +
            add_button = self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, "New post")
            add_button.click()
            time.sleep(2)

            # Sélectionner la photo
            self.driver.find_element(AppiumBy.XPATH, "//android.widget.Button[contains(@text, 'Gallery')]").click()
            time.sleep(2)

            # Sélectionner l'image de test
            self.driver.find_element(AppiumBy.XPATH, f"//android.widget.ImageView[contains(@content-desc, 'Photo')]").click()
            time.sleep(2)

            # Suivant
            next_button = self.driver.find_element(AppiumBy.ID, 'com.instagram.android:id/next_button_textview')
            next_button.click()
            time.sleep(2)

            # Ajouter la légende
            caption_field = self.driver.find_element(AppiumBy.ID, 'com.instagram.android:id/caption_text_view')
            caption_field.send_keys(test_caption)
            time.sleep(2)

            # Ne pas partager réellement pendant le test
            logger.info("Test photo post successful")
            
        except Exception as e:
            logger.error(f"Test failed: {str(e)}")
            pytest.fail(f"Test failed: {str(e)}")

    def test_post_reel(self):
        try:
            # Chemin vers une vidéo de test
            test_video = os.path.join(os.path.dirname(__file__), 'test_media', 'test_video.mp4')
            test_caption = "Test reel automatisé #testreel"

            # Aller à la section Reels
            reels_button = self.driver.find_element(AppiumBy.XPATH, "//android.widget.Button[contains(@text, 'Reels')]")
            reels_button.click()
            time.sleep(2)

            # Sélectionner la vidéo
            self.driver.find_element(AppiumBy.XPATH, "//android.widget.Button[contains(@text, 'Gallery')]").click()
            time.sleep(2)

            # Sélectionner la vidéo de test
            self.driver.find_element(AppiumBy.XPATH, f"//android.widget.ImageView[contains(@content-desc, 'Video')]").click()
            time.sleep(2)

            # Suivant
            next_button = self.driver.find_element(AppiumBy.ID, 'com.instagram.android:id/next_button_textview')
            next_button.click()
            time.sleep(2)

            # Ajouter la légende
            caption_field = self.driver.find_element(AppiumBy.ID, 'com.instagram.android:id/caption_text_view')
            caption_field.send_keys(test_caption)
            time.sleep(2)

            # Ne pas partager réellement pendant le test
            logger.info("Test reel post successful")
            
        except Exception as e:
            logger.error(f"Test failed: {str(e)}")
            pytest.fail(f"Test failed: {str(e)}")

    def teardown_method(self):
        if self.driver:
            self.driver.quit()

if __name__ == "__main__":
    pytest.main([__file__])