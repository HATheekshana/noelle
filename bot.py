
import asyncio
from playwright.async_api import async_playwright
from aiogram import Bot
from aiogram.types import InputMediaPhoto

BOT_TOKEN = "8596651439:AAG8f6HnKayox8KWVhrtUS8wm7nlVbZfqK8"
CHAT_ID = "-1001459190925"
USERNAME = "noelle_helper_bot"

bot = Bot(token=BOT_TOKEN)

LAST_TWEET = None


async def fetch_latest_tweet():
    global LAST_TWEET

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto(f"https://twitter.com/{USERNAME}", timeout=60000)
        await page.wait_for_timeout(5000)

        tweets = await page.locator("article").all()

        if not tweets:
            await browser.close()
            return None

        tweet = tweets[0]

        text = await tweet.inner_text()

        # tweet link
        links = await tweet.locator("a").all()
        tweet_url = None

        for l in links:
            href = await l.get_attribute("href")
            if href and "/status/" in href:
                tweet_url = "https://twitter.com" + href
                break

        # images
        imgs = await tweet.locator("img").all()
        images = []

        for img in imgs:
            src = await img.get_attribute("src")
            if src and "profile_images" not in src:
                images.append(src)

        await browser.close()

        if not tweet_url:
            return None

        if tweet_url == LAST_TWEET:
            return None

        LAST_TWEET = tweet_url

        return {
            "text": text,
            "url": tweet_url,
            "images": list(set(images))  # remove duplicates
        }


async def send(tweet):
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


async def loop():
    print("Bot started...")
    await bot.send_message(CHAT_ID, "✅ Bot test successful")
    while True:
        try:
            tweet = await fetch_latest_tweet()
            await send(tweet)

        except Exception as e:
            print("Error:", e)

        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(loop())