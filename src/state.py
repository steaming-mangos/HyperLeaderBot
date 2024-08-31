import time
import aiohttp
import asyncio
from discord.ext.commands import Bot as DiscordBot
import json


class State:
    users: dict[int, dict] = {}
    user_ttl: int = 1800  # time to live in seconds

    queue_users_to_remind: list[int] = []
    queue_reminder_channel: int = 1021477531733471314
    queue_userids: list[int] = []

    bot: DiscordBot

    def __init__(self, bot: DiscordBot):
        asyncio.run(self.__queue_tick())
        self.bot = bot

    async def add_user_to_queue_reminders(self, user_id: int) -> bool:
        # returns: bool :: whether the user was added to the queue
        # (false = already asked to be reminded)
        self.__refresh_queue()

        if len(self.queue_userids) < 3 or user_id in self.queue_users_to_remind:
            return False

        self.queue_users_to_remind.append(user_id)
        return True

    async def __refresh_queue(self) -> None:
        # logic to determine spot position
        async with aiohttp.ClientSession() as session:
            async with session.post("http://104.207.135.180:44454/vs/queue") as resp:
                raw_queue = await resp.content.read(4)
                queue_userids_offset = 4
                queue_list = []
                while raw_queue:
                    int_val = int.from_bytes(raw_queue, "little")
                    queue_list.append(int_val)
                    raw_queue = await resp.content.read(4)
                self.queue_userids = queue_list[queue_userids_offset:]

    async def __queue_tick(self) -> None:
        QUEUE_REMINDER_CHANNEL = self.bot.fetch_channel(self.queue_reminder_channel)

        while True:
            if len(self.queue_users_to_remind) > 0:
                # load the id dictionary
                with open("id_dictionary.json", "r") as outfile:
                    id_dict = json.load(outfile)

                self.__refresh_queue()

                if len(self.queue_userids) < 3:
                    self.queue_users_to_remind = (
                        []
                    )  # empty the reminders: queue is too small

                for user_id in self.queue_users_to_remind:
                    if user_id not in self.queue_userids:
                        self.queue_users_to_remind.remove(
                            user_id
                        )  # no need to keep tracking: not in queue

                    if self.queue_userids[2] == user_id:
                        user_discord_id = id_dict[user_id]
                        await QUEUE_REMINDER_CHANNEL.send(
                            f"<@{user_discord_id}>, you're up next! Get ready!"
                        )
                        self.queue_users_to_remind.remove(user_id)

            asyncio.sleep(5)

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
                self.users[user_id]["eol"] = time.time() + self.user.ttl
