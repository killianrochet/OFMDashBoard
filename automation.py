# automation.py

import os
import time
import random
import logging
import subprocess
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from database import Database
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def human_typing(element, text, min_delay=0.05, max_delay=0.15):
    typed = ""
    for word in text.split(" "):
        typed += word + " "
        element.set_value(typed.strip())
        time.sleep(random.uniform(min_delay, max_delay))

class InstagramAutomation:
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.driver = None

    def connect(self):
        desired_caps = {
            "platformName": "Android",
            "automationName": "UiAutomator2",
            "deviceName": self.device_id,
            "appPackage": "com.instagram.android",
            "appActivity": "com.instagram.mainactivity.MainActivity",
            "noReset": True
        }
        self.driver = webdriver.Remote("http://localhost:4723", desired_caps)
        self.wait = WebDriverWait(self.driver, 20)
        logger.info(f"✅ Appium connecté au device {self.device_id}")

    def delete_media(self, filename: str):
        possible_paths = [
            f"/sdcard/DCIM/Camera/{filename}",
            f"/sdcard/DCIM/{filename}",
            f"/storage/emulated/0/DCIM/{filename}"
        ]

        for path in possible_paths:
            try:
                subprocess.run(["adb", "-s", self.device_id, "shell", "rm", "-f", path], check=True)
                logger.info(f"🗑️ Média supprimé depuis {path}")
                subprocess.run([
                    "adb", "-s", self.device_id, "shell",
                    "am", "broadcast", "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE",
                    "-d", f"file://{path}"
                ], check=True)
                logger.info("♻️ Galerie rescannée")
                return
            except subprocess.CalledProcessError:
                logger.debug(f"❌ Impossible de supprimer ou scanner {path}, tentative suivante...")

        logger.warning("⚠️ Aucun chemin valide trouvé pour supprimer le média.")
        
        
    def get_current_username(self):
        try:
            profile_icon = self.wait.until(EC.presence_of_element_located((
                AppiumBy.XPATH, "//android.widget.ImageView[@resource-id='com.instagram.android:id/tab_avatar']"
            )))
            profile_icon.click()
            time.sleep(1)

            dropdown = self.wait.until(EC.presence_of_element_located((
                AppiumBy.XPATH, "//android.widget.LinearLayout[@resource-id='com.instagram.android:id/action_bar_title_and_icons']"
            )))
            dropdown.click()
            time.sleep(1)

            current_element = self.driver.find_element(AppiumBy.XPATH, "(//android.view.ViewGroup[@content-desc])[1]")
            desc = current_element.get_attribute("content-desc")
            if desc:
                return desc.split(",")[0].strip()
            return None
        except Exception as e:
            logger.warning(f"⚠️ Impossible de récupérer le compte actuel : {e}")
            return None


    def get_instagram_accounts(self):
        try:
            logger.info("👤 Récupération des comptes Instagram")

            # Aller sur le profil
            profile_icon = self.wait.until(EC.presence_of_element_located((
                AppiumBy.XPATH, "//android.widget.ImageView[@resource-id='com.instagram.android:id/tab_avatar']"
            )))
            profile_icon.click()
            time.sleep(1)

            # Ouvrir le menu déroulant
            dropdown = self.wait.until(EC.presence_of_element_located((
                AppiumBy.XPATH, "//android.widget.LinearLayout[@resource-id='com.instagram.android:id/action_bar_title_and_icons']"
            )))
            dropdown.click()
            time.sleep(1)

            # Récupération des éléments du menu
            all_items = self.driver.find_elements(AppiumBy.XPATH, "//android.view.ViewGroup[@content-desc]")
            usernames = []

            for item in all_items:
                desc = item.get_attribute("content-desc")
                if not desc:
                    continue

                desc_lower = desc.lower()
                if "go to accounts center" in desc_lower or "add instagram account" in desc_lower:
                    continue

                username = desc.split(",")[0].strip()
                if username:
                    usernames.append(username)

            logger.info(f"📦 Comptes trouvés : {usernames}")

            # ✅ Revenir à l'écran d'accueil
            try:
                logger.info("🏠 Retour à l'écran principal Instagram...")
                blank_area = self.wait.until(EC.presence_of_element_located((
                    AppiumBy.XPATH, "//android.widget.FrameLayout[@resource-id='android:id/content']/android.widget.FrameLayout/android.view.ViewGroup"
                )))
                blank_area.click()
                time.sleep(0.5)

                home_btn = self.wait.until(EC.presence_of_element_located((
                    AppiumBy.XPATH, "(//android.widget.ImageView[@resource-id='com.instagram.android:id/tab_icon'])[1]"
                )))
                home_btn.click()
                time.sleep(1)
                logger.info("✅ Revenu à l'accueil")
            except Exception as e:
                logger.warning(f"⚠️ Impossible de revenir à l'accueil : {e}")

            return usernames

        except Exception as e:
            logger.error(f"❌ Erreur récupération comptes : {e}")
            return []


    def switch_to_account(self, target_username: str):
        logger.info(f"🔁 Tentative de basculement vers le compte : {target_username}")

        try:
            logger.debug("🧭 Attente de l'icône de profil (tab_avatar)...")
            profile_icon = self.wait.until(EC.presence_of_element_located((
                AppiumBy.XPATH,
                "//android.widget.ImageView[@resource-id='com.instagram.android:id/tab_avatar']"
            )))
            profile_icon.click()
            time.sleep(1)

            logger.debug("🧭 Attente du menu déroulant (action_bar_title_and_icons)...")
            dropdown = self.wait.until(EC.presence_of_element_located((
                AppiumBy.XPATH,
                "//android.widget.LinearLayout[@resource-id='com.instagram.android:id/action_bar_title_and_icons']"
            )))
            dropdown.click()
            time.sleep(2)

            logger.debug("🧭 Recherche des comptes disponibles dans le menu déroulant")
            all_accounts = self.driver.find_elements(AppiumBy.XPATH, "//android.view.ViewGroup[@content-desc]")
            logger.info(f"📦 {len(all_accounts)} éléments trouvés dans le menu de comptes")
            self.driver.save_screenshot(f"screenshot_switch_fail_{self.device_id}.png")


            if not all_accounts:
                print("⚠️ Aucun élément trouvé avec le content-desc. Vérifie si la fenêtre est bien ouverte.")
            
            found = False
            for account in all_accounts:
                content_desc = account.get_attribute("content-desc") or ""
                print(f"🔍 Élément détecté : '{content_desc}'")

                username = content_desc.split(",")[0].strip()

                if target_username.lower() == username.lower():
                    print(f"✅ Compte trouvé : '{username}' → on clique dessus.")
                    account.click()
                    time.sleep(2)
                    found = True
                    break

            if not found:
                raise Exception(f"❌ Le compte '{target_username}' n’a pas été trouvé dans les éléments listés.")

        except Exception as e:
            logger.error(f"❌ Erreur lors du changement de compte : {e}")
            screenshot_path = f"switch_to_account_fail_{self.device_id}.png"
            self.driver.save_screenshot(screenshot_path)
            logger.info(f"📸 Capture enregistrée : {screenshot_path}")
            raise


    def post_photo(self, image_path: str, caption: str, account: str):
        self.ensure_account(account)
        try:
            logger.info("📸 Début du post photo")

            logger.info("📸 Clic sur le bouton '+' depuis la page principale")
            add_btn_from_home = self.wait.until(EC.presence_of_element_located((
                AppiumBy.XPATH,
                "(//android.widget.ImageView[@resource-id='com.instagram.android:id/tab_icon'])[4]"
            )))
            add_btn_from_home.click()
            time.sleep(2)
            
            logger.info("🎞️ Sélection du bouton POST")
            reel_btn = self.wait.until(EC.presence_of_element_located((
                AppiumBy.XPATH,
                "//android.widget.TextView[@content-desc='POST']"
            )))
            reel_btn.click()
            time.sleep(2)

            logger.info("📂 Ouverture du menu des dossiers")
            folder_menu = self.wait.until(EC.presence_of_element_located((
                AppiumBy.XPATH,
                "//android.widget.FrameLayout[@resource-id='com.instagram.android:id/gallery_folder_menu_container']"
            )))
            folder_menu.click()
            time.sleep(1)

            logger.info("📁 Sélection du dossier DCIM")
            dcim_folder = self.wait.until(EC.presence_of_element_located((
                AppiumBy.XPATH,
                "//android.widget.LinearLayout[@content-desc='DCIM']"
            )))
            dcim_folder.click()
            time.sleep(1)

            image = self.wait.until(EC.presence_of_element_located((
                AppiumBy.XPATH, "//android.view.View[@resource-id='com.instagram.android:id/gallery_grid_item_selection_overlay']")))
            image.click()
            time.sleep(2)

            logger.info("➡️ Premier bouton 'Next'")
            next_btn1 = self.wait.until(EC.presence_of_element_located((
                AppiumBy.XPATH,
                "//android.widget.Button[@content-desc='Next']"
            )))
            next_btn1.click()
            time.sleep(2)

            logger.info("➡️ Deuxième bouton 'Next'")
            next_btn2 = self.wait.until(EC.presence_of_element_located((
                AppiumBy.XPATH,
                "//android.widget.Button[@content-desc='Next']"
            )))
            next_btn2.click()
            time.sleep(2)

            logger.info("📝 Saisie humaine de la description...")
            caption_field = self.wait.until(EC.presence_of_element_located((
                AppiumBy.XPATH,
                "//android.widget.AutoCompleteTextView[@resource-id='com.instagram.android:id/caption_input_text_view']"
            )))
            human_typing(caption_field, caption)
            time.sleep(1)

            logger.info("🚀 Publication du post...")
            share_btn = self.wait.until(EC.presence_of_element_located((
                AppiumBy.XPATH,
                "//android.widget.Button[@resource-id='com.instagram.android:id/share_footer_button']"
            )))
            share_btn.click()
            time.sleep(1)
            logger.info("✅ Post publié avec succès !")

            self.delete_media(os.path.basename(image_path))

            # try:
            #     home_btn = self.driver.find_element(AppiumBy.XPATH, "(//android.widget.ImageView[@resource-id='com.instagram.android:id/tab_icon'])[2]")
            #     home_btn.click()
            #     time.sleep(1)
            #     logger.info("🏠 Revenu à l’accueil Instagram")
            # except Exception as e:
            #     logger.warning(f"⚠️ Impossible de revenir à l’accueil : {e}")

        except Exception as e:
            logger.error(f"❌ Erreur publication photo: {e}")
            raise e

    def post_reel(self, video_path: str, caption: str, account: str):
        self.ensure_account(account)
        try:
            logger.info("🎬 Début du post reel")

            logger.info("📸 Clic sur le bouton '+' depuis la page principale")
            add_btn_from_home = self.wait.until(EC.presence_of_element_located((
                AppiumBy.XPATH,
                "(//android.widget.ImageView[@resource-id='com.instagram.android:id/tab_icon'])[4]"
            )))
            add_btn_from_home.click()
            time.sleep(2)

            logger.info("🎞️ Sélection du bouton REEL")
            reel_btn = self.wait.until(EC.presence_of_element_located((
                AppiumBy.XPATH,
                "//android.widget.TextView[@content-desc='REEL']"
            )))
            reel_btn.click()
            time.sleep(2)

            logger.info("📂 Ouverture du menu 'All Albums'")
            album_menu = self.wait.until(EC.presence_of_element_located((
                AppiumBy.XPATH,
                "//android.widget.TextView[@resource-id='com.instagram.android:id/gallery_folder_menu_tv']"
            )))
            album_menu.click()
            time.sleep(1)

            logger.info("📁 Sélection de 'All Albums'")
            all_albums = self.wait.until(EC.presence_of_element_located((
                AppiumBy.XPATH,
                "//android.widget.TextView[@resource-id='com.instagram.android:id/context_menu_item_label' and @text='All Albums']"
            )))
            all_albums.click()
            time.sleep(1)

            logger.info("📁 Sélection du dossier DCIM")
            dcim_folder = self.wait.until(EC.presence_of_element_located((
                AppiumBy.XPATH,
                "//android.widget.LinearLayout[@content-desc='DCIM']"
            )))
            dcim_folder.click()
            time.sleep(1)

            logger.info("🖼️ Sélection du média dans la galerie")
            media = self.wait.until(EC.presence_of_element_located((
                AppiumBy.XPATH,
                '(//android.widget.ImageView[@resource-id="com.instagram.android:id/background_color"])[1]'
            )))
            media.click()
            time.sleep(2)

            logger.info("➡️ Bouton 'Next'")
            next_btn1 = self.wait.until(EC.presence_of_element_located((
                AppiumBy.XPATH,
                "//android.widget.TextView[@text='Next']"
            )))
            next_btn1.click()
            time.sleep(2)

            logger.info("📝 Saisie humaine de la description...")
            caption_field = self.wait.until(EC.presence_of_element_located((
                AppiumBy.XPATH,
                "//android.widget.AutoCompleteTextView[@resource-id='com.instagram.android:id/caption_input_text_view']"
            )))
            human_typing(caption_field, caption)
            time.sleep(2)

            logger.info("⚙️ Paramétrage audience et grille")
            audience_btn = self.wait.until(EC.presence_of_element_located((
                AppiumBy.XPATH,
                "//android.widget.TextView[@resource-id='com.instagram.android:id/inline_subtitle' and @text='Everyone']"
            )))
            audience_btn.click()
            time.sleep(1)

            profile_display = self.wait.until(EC.presence_of_element_located((
                AppiumBy.XPATH,
                "//android.widget.TextView[@resource-id='com.instagram.android:id/inline_subtitle']"
            )))
            profile_display.click()
            time.sleep(1)

            reel_only_radio = self.wait.until(EC.presence_of_element_located((
                AppiumBy.XPATH,
                "(//android.widget.RadioButton[@resource-id='com.instagram.android:id/igds_textcell_radio'])[4]"
            )))
            reel_only_radio.click()
            time.sleep(1)

            done_btn = self.wait.until(EC.presence_of_element_located((
                AppiumBy.XPATH,
                "//android.widget.Button[@content-desc='Done']"
            )))
            done_btn.click()
            time.sleep(1)

            back_btn = self.wait.until(EC.presence_of_element_located((
                AppiumBy.XPATH,
                "//android.widget.ImageView[@content-desc='Back']"
            )))
            back_btn.click()
            time.sleep(1)

            logger.info("🚀 Bouton 'Share'")
            share_btn = self.wait.until(EC.presence_of_element_located((
                AppiumBy.XPATH,
                "//android.widget.TextView[@text='Share']"
            )))
            share_btn.click()
            logger.info("✅ Reel publié avec succès !")
            time.sleep(2)

            self.delete_media(os.path.basename(video_path))

            # try:
            #     home_btn = self.driver.find_element(AppiumBy.XPATH, "(//android.widget.ImageView[@resource-id='com.instagram.android:id/tab_icon'])[2]")
            #     home_btn.click()
            #     time.sleep(1)
            #     logger.info("🏠 Revenu à l’accueil Instagram")
            # except Exception as e:
            #     logger.warning(f"⚠️ Impossible de revenir à l’accueil : {e}")

        except Exception as e:
            logger.error(f"❌ Erreur publication reel: {e}")
            raise e
        
        
    def ensure_account(self, expected_account: str):
        logger.info(f"📌 ensure_account() → expected = {expected_account}")

        db = Database()
        current = db.get_active_account(self.device_id)
        logger.info(f"📌 ensure_account() → current = {current} (from DB)")

        if current and current.lower() != expected_account.lower():
            logger.info(f"🔄 Changement nécessaire : de {current} vers {expected_account}")
            self.switch_to_account(expected_account)
            db.set_active_account(self.device_id, expected_account)
            logger.info(f"✅ Base mise à jour avec {expected_account} comme compte actif")
        else:
            logger.info("✅ Aucun changement de compte nécessaire.")

    def close(self):
        if self.driver:
            self.driver.quit()
            logger.info(f"🛑 Session Appium fermée pour {self.device_id}")
