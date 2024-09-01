import time
import aiohttp
import asyncio
from discord.ext.commands import Bot as DiscordBot
from uid_map import load_map_dict


class State:
    users: dict[int, dict] = {}
    user_ttl: int = 1800  # time to live in seconds

    queue_users_to_remind: list[int] = []
    queue_reminder_channel: int = 1021477531733471314
    queue_userids: list[int] = []
    queue_refresh_secs: int = 5

    bot: DiscordBot

    async def attach(self, bot: DiscordBot):
        self.bot = bot
        asyncio.ensure_future(self.__queue_tick())

    async def add_user_to_queue_reminders(self, user_id: int) -> bool:
        # returns: bool :: whether the user was added to the queue
        if user_id in self.queue_users_to_remind:
            return False

        self.queue_users_to_remind.append(user_id)
        return True

    async def __refresh_queue(self) -> None:
        # logic to determine spot position
        async with aiohttp.ClientSession() as session:
            url = "http://104.207.135.180:44454/vs/queue"
            async with session.post(url) as resp:
                raw_queue = await resp.content.read(4)
                queue_userids_offset = 4
                queue_list = []
                while raw_queue:
                    int_val = int.from_bytes(raw_queue, "little")
                    queue_list.append(int_val)
                    raw_queue = await resp.content.read(4)
                self.queue_userids = queue_list[queue_userids_offset:]

    async def __queue_tick(self) -> None:
        QUEUE_REMINDER_CHANNEL = self.bot.fetch_channel(
                self.queue_reminder_channel
        )

        while True:
            id_lookup = load_map_dict()

            await self.__refresh_queue()

            for user_id in self.queue_users_to_remind:
                if self.queue_userids[2] == user_id:
                    user_discord_id = id_lookup[user_id]
                    await QUEUE_REMINDER_CHANNEL.send(
                        f"<@{user_discord_id}>, you're up next! Get ready!"
                    )
                    self.queue_users_to_remind.remove(user_id)

            print(self.queue_users_to_remind)
            print(self.queue_userids)

            await asyncio.sleep(self.queue_refresh_secs)

    async def get_user(self, user_id: int) -> dict:
        if user_id not in self.users:
            await self.__refresh_user(user_id)

        elif self.users[user_id]["eol"] < time.time():
            await self.__refresh_user(user_id)

        return self.users[user_id]

    async def __refresh_user(self, user_id: int) -> None:
        try:
            user_id = int(user_id)
        except ValueError:
            raise ValueError("user_id must be an integer")

        url = f"https://hyprd.mn/backend_dev/get_user_public.php?id={user_id}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                self.users[user_id] = await resp.json()
                self.users[user_id]["eol"] = time.time() + self.user_ttl
