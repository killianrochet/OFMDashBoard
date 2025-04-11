from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InstagramBot:
    def __init__(self):
        # Configuration Appium pour Android
        self.desired_caps = {
            'platformName': 'Android',
            'automationName': 'UiAutomator2',
            'deviceName': 'Android Device',
            'appPackage': 'com.instagram.android',
            'appActivity': 'com.instagram.mainactivity.MainActivity',
            'noReset': True  # Garde la session Instagram connectée
        }
        
        self.driver = None

    def connect(self):
        try:
            self.driver = webdriver.Remote('http://localhost:4723/wd/hub', self.desired_caps)
            logger.info("Connected to Instagram app")
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {str(e)}")
            return False

    def post_photo(self, image_path, caption):
        try:
            # Cliquer sur le bouton +
            add_button = self.driver.find_element(AppiumBy.ID, 'com.instagram.android:id/new_post_button')
            add_button.click()
            time.sleep(2)

            # Sélectionner la photo
            self.driver.find_element(AppiumBy.XPATH, "//android.widget.Button[contains(@text, 'Gallery')]").click()
            time.sleep(2)
            
            # Sélectionner l'image
            self.driver.find_element(AppiumBy.XPATH, f"//android.widget.Image[contains(@content-desc, '{image_path}')]").click()
            time.sleep(2)

            # Suivant
            next_button = self.driver.find_element(AppiumBy.ID, 'com.instagram.android:id/next_button_textview')
            next_button.click()
            time.sleep(2)

            # Ajouter la légende
            caption_field = self.driver.find_element(AppiumBy.ID, 'com.instagram.android:id/caption_text_view')
            caption_field.send_keys(caption)
            time.sleep(2)

            # Partager
            share_button = self.driver.find_element(AppiumBy.ID, 'com.instagram.android:id/next_button_textview')
            share_button.click()
            
            logger.info("Photo posted successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to post photo: {str(e)}")
            return False

    def post_reel(self, video_path, caption):
        try:
            # Cliquer sur le bouton Reels
            reels_button = self.driver.find_element(AppiumBy.XPATH, "//android.widget.Button[contains(@text, 'Reels')]")
            reels_button.click()
            time.sleep(2)

            # Sélectionner la vidéo
            self.driver.find_element(AppiumBy.XPATH, f"//android.widget.Image[contains(@content-desc, '{video_path}')]").click()
            time.sleep(2)

            # Suivant
            next_button = self.driver.find_element(AppiumBy.ID, 'com.instagram.android:id/next_button_textview')
            next_button.click()
            time.sleep(2)

            # Ajouter la légende
            caption_field = self.driver.find_element(AppiumBy.ID, 'com.instagram.android:id/caption_text_view')
            caption_field.send_keys(caption)
            time.sleep(2)

            # Partager
            share_button = self.driver.find_element(AppiumBy.ID, 'com.instagram.android:id/next_button_textview')
            share_button.click()
            
            logger.info("Reel posted successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to post reel: {str(e)}")
            return False

    def close(self):
        if self.driver:
            self.driver.quit()