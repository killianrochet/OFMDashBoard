import os
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
import random

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def human_typing(element, text, min_delay=0.05, max_delay=0.15):
    typed = ""
    for char in text:
        typed += char
        element.set_value(typed)  # Met à jour tout le champ à chaque lettre
        time.sleep(random.uniform(min_delay, max_delay))


def test_custom_post():
    try:
        # Configuration pour l'émulateur
        desired_caps = {
            'platformName': 'Android',
            'automationName': 'UiAutomator2',
            'deviceName': 'emulator-5556', 
            'appPackage': 'com.instagram.android',
            'appActivity': 'com.instagram.mainactivity.MainActivity',
            'noReset': True
        }

        # Connexion à Appium
        driver = webdriver.Remote('http://localhost:4723', desired_caps)
        driver.implicitly_wait(10)
        wait = WebDriverWait(driver, 20)

        # Chemin vers votre photo
        photo_path = os.path.join(os.path.dirname(__file__), 'test_media', 'ma_photo.png')
        
        # Votre description personnalisée
        caption = "Bonne journée à tous je vous aimes #instagram"

        logger.info("🔍 Navigation vers le profil...")
        profile_btn = wait.until(EC.presence_of_element_located((AppiumBy.ID, "com.instagram.android:id/tab_avatar")))
        profile_btn.click()
        logger.info("✅ Profil ouvert")
        time.sleep(2)

        # Bouton + depuis le profil
        logger.info("🔍 Bouton + (Créer) sur le profil...")
        create_btn = wait.until(EC.presence_of_element_located((AppiumBy.ID, "com.instagram.android:id/profile_header_create_button")))
        create_btn.click()
        logger.info("✅ Bouton créer cliqué")
        time.sleep(2)

        # Sélectionner "Post"
        logger.info("🔍 Sélectionner 'Post' dans la liste...")
        post_btn = wait.until(EC.presence_of_element_located((
            AppiumBy.XPATH,
            "//android.widget.TextView[@resource-id='com.instagram.android:id/label' and @text='Reel']"
        )))
        post_btn.click()
        logger.info("✅ Option 'Post' sélectionnée")
        time.sleep(2)

        # Sélectionner la 1ère photo
        logger.info("🖼️ Sélection de la première photo...")
        first_photo = wait.until(EC.presence_of_element_located((
            AppiumBy.XPATH,
            "//android.view.View[@resource-id='com.instagram.android:id/gallery_grid_item_selection_overlay']"
        )))
        first_photo.click()
        logger.info("✅ Photo sélectionnée")
        time.sleep(2)

        # Accès rapide au bouton +
        logger.info("📸 Clic sur le bouton '+' depuis la page principale")
        add_btn_from_home = wait.until(EC.presence_of_element_located((
            AppiumBy.XPATH,
            "(//android.widget.ImageView[@resource-id='com.instagram.android:id/tab_icon'])[4]"
        )))
        add_btn_from_home.click()
        time.sleep(2)
        # Bouton "Next" 1
        logger.info("➡️ Premier bouton 'Next'")
        next_btn1 = wait.until(EC.presence_of_element_located((
            AppiumBy.XPATH,
            "//android.widget.Button[@content-desc='Next']"
        )))
        next_btn1.click()
        time.sleep(2)

        # Bouton "Next" 2
        logger.info("➡️ Deuxième bouton 'Next'")
        next_btn2 = wait.until(EC.presence_of_element_located((
            AppiumBy.XPATH,
            "//android.widget.Button[@content-desc='Next']"
        )))
        next_btn2.click()
        time.sleep(2)

        # Ajouter une description
        logger.info("📝 Saisie humaine de la description...")
        caption_input = wait.until(EC.presence_of_element_located((
            AppiumBy.XPATH,
            "//android.widget.AutoCompleteTextView[@resource-id='com.instagram.android:id/caption_input_text_view']"
        )))
        human_typing(caption_input, caption)
        time.sleep(1)

        # Bouton "Share"
        logger.info("🚀 Publication du post...")
        share_btn = wait.until(EC.presence_of_element_located((
            AppiumBy.XPATH,
            "//android.widget.Button[@resource-id='com.instagram.android:id/share_footer_button']"
        )))
        share_btn.click()
        logger.info("✅ Post publié avec succès !")

    except Exception as e:
        logger.error(f"❌ Une erreur est survenue : {str(e)}")
        raise

    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    test_custom_post()