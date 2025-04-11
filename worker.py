import time
import logging
from threading import Thread
from automation import InstagramAutomation
from database import Database

logger = logging.getLogger(__name__)

class DeviceWorker(Thread):
    def __init__(self, device_id, task_queue):
        super().__init__(daemon=True)
        self.device_id = device_id
        self.queue = task_queue
        self.db = Database()

    def run(self):
        logger.info(f"🧵 Lancement du worker pour {self.device_id}")

        while True:
            if self.queue.empty():
                time.sleep(3)
                continue

            task = self.queue.get()
            post_id = task.get("post_id")
            media_path = task.get("media_path")
            caption = task.get("caption")
            post_type = task.get("post_type")
            account = task.get("account")  # 💡 Nouveau champ utilisé ici
            logger.info(f"[DEBUG TASK] post_id={post_id}, media_path={media_path}, caption={caption}, post_type={post_type}, account={account}")

            logger.info(f"📬 [{self.device_id}] Traitement du post {post_id} pour @{account}...")

            automation = InstagramAutomation(self.device_id)
            try:
                automation.connect()
                if post_type == "photo":
                    automation.post_photo(media_path, caption, account)
                elif post_type == "reel":
                    automation.post_reel(media_path, caption, account)

                logger.info(f"✅ [{self.device_id}] Post {post_id} effectué avec succès sur @{account}")
                self.db.update_post_status(post_id, "completed")
                

            except Exception as e:
                logger.error(f"❌ [{self.device_id}] Échec du post {post_id} (@{account}) : {e}")
                self.db.update_post_status(post_id, "failed")

            finally:
                automation.close()
                self.queue.task_done()
