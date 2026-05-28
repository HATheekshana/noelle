
import asyncio
import snscrape.modules.twitter as sntwitter
from aiogram import Bot
from aiogram.types import InputMediaPhoto

# =======================
# CONFIG
# =======================
BOT_TOKEN = "8596651439:AAG8f6HnKayox8KWVhrtUS8wm7nlVbZfqK8"
CHAT_ID = "@genshinimpactenglishgroup"
USERNAME = "noelle_helper_bot"

bot = Bot(token=BOT_TOKEN)

LAST_ID_FILE = "last_id.txt"


# =======================
# STORAGE
# =======================
def load_last_id():
    try:
        with open(LAST_ID_FILE, "r") as f:
            return int(f.read().strip())
    except:
        return 0


def save_last_id(tweet_id):
    with open(LAST_ID_FILE, "w") as f:
        f.write(str(tweet_id))


# =======================
# FETCH TWEETS (FIXED)
# =======================
def fetch_latest_tweet():
    last_id = load_last_id()

    scraper = sntwitter.TwitterSearchScraper(f"from:{USERNAME}")

    for tweet in scraper.get_items():
        if tweet.id <= last_id:
            continue

        images = []

        # FIX: correct media extraction
        if hasattr(tweet, "media") and tweet.media:
            for m in tweet.media:
                if hasattr(m, "fullUrl"):
                    images.append(m.fullUrl)

        return {
            "id": tweet.id,
            "text": tweet.content,
            "images": images,
            "url": f"https://twitter.com/{USERNAME}/status/{tweet.id}"
        }

    return None


# =======================
# SEND TO TELEGRAM
# =======================
async def send_tweet(tweet):
    if not tweet:
        return

    caption = f"{tweet['text']}\n\n🔗 {tweet['url']}"
    images = tweet["images"]

    # no images
    if not images:
        await bot.send_message(CHAT_ID, caption)
        return

    # single image
    if len(images) == 1:
        await bot.send_photo(CHAT_ID, images[0], caption=caption)
        return

    # album
    media = []
    for i, img in enumerate(images[:10]):
        if i == 0:
            media.append(InputMediaPhoto(media=img, caption=caption))
        else:
            media.append(InputMediaPhoto(media=img))

    await bot.send_media_group(CHAT_ID, media=media)


# =======================
# LOOP
# =======================
async def run():
    print("Bot started...")

    while True:
        try:
            tweet = fetch_latest_tweet()

            if tweet:
                print("New tweet:", tweet["id"])
                await send_tweet(tweet)
                save_last_id(tweet["id"])

        except Exception as e:
            print("Error:", e)

        await asyncio.sleep(60)


# =======================
# START
# =======================
async def main():
    await run()


if __name__ == "__main__":
    asyncio.run(main())