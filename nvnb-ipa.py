# coding: utf-8
import feedparser
import requests
import time
import os
from misskey import Misskey
from atproto import Client, models

f = open("nvnb-ipa.txt", "r", encoding="utf-8")
old_up = f.readline().replace("\n", "")
f.close()

entries = feedparser.parse("https://www.ipa.go.jp/security/alert-rss.rdf")["entries"]
i = 0

feed_size = len(entries)

# ブログのURL
blog_url = "https://nvnb.blossomsarchive.com/"

# WordPressのユーザー名
wordpress_user = os.environ.get("WORDPRESS_USER")
api_user = wordpress_user

# アプリケーションパスワード
wordpress_api_password = os.environ.get("WORDPRESS_API_PASSWORD")
api_password = wordpress_api_password

for i in range(feed_size):
    now_up = entries[i]["updated"]
    if now_up == old_up:
        new_up = entries[0]["updated"]
        g = open("nvnb-ipa.txt", "w", encoding="utf-8")
        g.write(new_up)
        g.close()
        break
    else:
        title = entries[i]["title"]
        page_url = entries[i]["link"]
        # 送信する記事データ
        post_data = {
            "title": "[IPA] " + title,
            "content": "<p>IPAの記事リンク</p>"
            + '<a href= "'
            + page_url
            + '">'
            + page_url
            + "</a>",
            "categories": "9",
            "status": "publish",  # draft=下書き、publish=公開　省略時はdraftになる
            "featured_media": 163,
        }
        # Post APIのURL
        post_api_url = f"{blog_url}/wp-json/wp/v2/posts"

        # 記事投稿リクエスト
        response = requests.post(
            post_api_url, json=post_data, auth=(api_user, api_password)
        )

        post_text = (
            "【IPA】\n"
            + title
            + "\n"
            + page_url
            + "\n\nその他の情報はこちら\nhttps://nvnb.blossomsarchive.com/"
        )
        print(post_text)
        try:
            # SNS投稿API
            # Misskey
            misskey_address = os.environ.get("MISSKEY_SERVER_ADDRESS")
            misskey_token = os.environ.get("MISSKEY_TOKEN")
            api = Misskey(misskey_address, misskey_token)
            api.notes_create(text=post_text)
        except:
            pass

            try:
                # SNS投稿API
                # Bluesky
                bluesky = Client()
                bluesky.login(
                    str(os.environ.get("BLUESKY_MAIL_ADDRESS")),
                    str(os.environ.get("BLUESKY_PASSWORD")),
                )
                embed_external = models.AppBskyEmbedExternal.Main(
                        external=models.AppBskyEmbedExternal.External(
                            title=title, description="title", uri=page_url
                        )
                    )
                bluesky.send_post(post_text,embed=embed_external)
            except:
                pass
        time.sleep(30)
    i = i + 1

new_up = entries[0]["updated"]
g = open("nvnb-ipa.txt", "w", encoding="utf-8")
g.write(new_up)
g.close()
