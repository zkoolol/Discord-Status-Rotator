import json, asyncio, aiohttp
from modules.console import Logger

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

async def fetch(session, url, headers=None, json=None):
    async with session.patch(url, headers=headers, json=json) as response:
        return await response.json(), response.status

async def statusChange(session, statuses):
    token = config.get("token", "")
    headers = {"authorization": token}

    while True:
        for status in statuses:
            message = status.get("status", "")
            emoji_id = status.get("emoji_id", "")
            emoji_name = status.get("emoji_name", "")
            nitro_emoji = status.get("nitro_emoji", False)
            delay = config.get("delay", 1)

            if nitro_emoji:
                payload = {"custom_status": {"text": message, "emoji_id": emoji_id, "emoji_name": emoji_name}}
            else:
                payload = {"custom_status": {"text": message, "emoji_name": emoji_name}}

            response_data, status_code = await fetch(session, "https://discord.com/api/v8/users/@me/settings", headers=headers, json=payload)
            if status_code == 200:
                Logger.info(f"Successfully changed status to: {message}")
                await asyncio.sleep(delay)
            elif status_code == 429:
                retry_after = response_data.headers.get('Retry-After', '5')
                Logger.error(f"Ratelimited, sleeping for {retry_after} seconds..")
                await asyncio.sleep(retry_after)
            else:
                Logger.error(f"Error: {status_code}")

async def setup():
    statuses = config.get("statuses", [])
    async with aiohttp.ClientSession() as session:
        await statusChange(session, statuses)

if __name__ == "__main__":
    asyncio.run(setup())