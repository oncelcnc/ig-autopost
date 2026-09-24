#!/usr/bin/env python3
"""
Kuyruktaki bir sonraki gönderiyi Instagram'a otomatik yükler.

Her gün GitHub Actions tarafından çalıştırılır. content_queue/queue.json
içindeki sırayla ilerler, yüklediği her gönderiyi "posted": true olarak işaretler.

Gerekli ortam değişkenleri (GitHub Secrets üzerinden sağlanır):
  IG_ACCESS_TOKEN   -> Meta Graph API uzun ömürlü erişim token'ı
  IG_USER_ID        -> Instagram professional hesabının Graph API user id'si
  GITHUB_REPOSITORY -> görsellerin ham (raw) URL'sini oluşturmak için (otomatik gelir)
"""

import json
import os
import sys
import time
import requests

GRAPH_API_VERSION = "v21.0"
GRAPH_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

QUEUE_PATH = os.path.join(os.path.dirname(__file__), "..", "content_queue", "queue.json")


def load_queue():
    with open(QUEUE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_queue(queue):
    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)


def raw_github_url(image_relative_path: str) -> str:
    """content_queue/images/xxx.jpg -> raw.githubusercontent.com üzerinden herkese açık URL."""
    repo = os.environ["GITHUB_REPOSITORY"]  # örn: kullaniciadi/ig-autopost
    branch = os.environ.get("GITHUB_REF_NAME", "main")
    return f"https://raw.githubusercontent.com/{repo}/{branch}/{image_relative_path}"


def create_media_container(ig_user_id, token, image_url, caption):
    resp = requests.post(
        f"{GRAPH_BASE}/{ig_user_id}/media",
        data={
            "image_url": image_url,
            "caption": caption,
            "access_token": token,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["id"]


def wait_until_ready(container_id, token, max_wait_seconds=120):
    """Instagram görseli işlerken container FINISHED olana kadar bekler."""
    waited = 0
    while waited < max_wait_seconds:
        resp = requests.get(
            f"{GRAPH_BASE}/{container_id}",
            params={"fields": "status_code", "access_token": token},
            timeout=30,
        )
        resp.raise_for_status()
        status = resp.json().get("status_code")
        if status == "FINISHED":
            return True
        if status == "ERROR":
            return False
        time.sleep(5)
        waited += 5
    return False


def publish_container(ig_user_id, token, container_id):
    resp = requests.post(
        f"{GRAPH_BASE}/{ig_user_id}/media_publish",
        data={
            "creation_id": container_id,
            "access_token": token,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def main():
    token = os.environ["IG_ACCESS_TOKEN"]
    ig_user_id = os.environ["IG_USER_ID"]

    queue = load_queue()
    next_post = next((p for p in queue["posts"] if not p.get("posted")), None)

    if next_post is None:
        print("Kuyrukta yayınlanmamış içerik kalmadı. content_queue/queue.json'a yeni gönderi ekleyin.")
        sys.exit(0)

    image_url = raw_github_url(next_post["image_path"])
    caption = next_post["caption"]

    print(f"Yayınlanıyor: {next_post['id']} -> {image_url}")

    container_id = create_media_container(ig_user_id, token, image_url, caption)
    ready = wait_until_ready(container_id, token)

    if not ready:
        print("HATA: Görsel işlenemedi (status_code ERROR ya da zaman aşımı). Yayınlanmadı.")
        sys.exit(1)

    result = publish_container(ig_user_id, token, container_id)
    print("Yayınlandı:", result)

    next_post["posted"] = True
    next_post["published_media_id"] = result.get("id")
    save_queue(queue)


if __name__ == "__main__":
    main()
