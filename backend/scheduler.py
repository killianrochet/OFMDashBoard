import time
import datetime
import logging
from queue import Queue
from threading import Thread
from database import Database
from worker import DeviceWorker

logging.basicConfig(
    level=logging.INFO,  # ou DEBUG si tu veux tout voir
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("scheduler")

def main():
    db = Database()
    device_queues = {}
    workers = {}

    logger.info("🔄 Initialisation du scheduler...")

    while True:
        pending_posts = db.get_pending_posts()
        logger.info(f"📋 {len(pending_posts)} posts en attente")

        for post in pending_posts:
            print(f"DEBUG RAW POST: {post}")
            post_id, device_id, scheduled_time, media_path, caption, post_type, account, status, created_at = post

            # Vérifie si le post est encore dans le futur
            scheduled_datetime = datetime.datetime.fromisoformat(scheduled_time)
            now = datetime.datetime.now()
            if scheduled_datetime > now:
                continue  # Ne traite pas ce post maintenant

            if device_id not in device_queues:
                device_queues[device_id] = Queue()
                worker = DeviceWorker(device_id, device_queues[device_id])
                worker.start()
                workers[device_id] = worker
                logger.info(f"👷‍♂️ Worker lancé pour le device {device_id}")

            task = {
                "post_id": post_id,
                "media_path": media_path,
                "caption": caption,
                "post_type": post_type,
                "account": account
            }

            device_queues[device_id].put(task)
            db.update_post_status(post_id, "processing")

        time.sleep(30)

if __name__ == "__main__":
    main()
