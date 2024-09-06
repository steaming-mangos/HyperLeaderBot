import time
import aiohttp
import asyncio
from discord.ext.commands import Bot as DiscordBot
from uid_map import load_map_dict


class State:
    __cached_users: dict[int, dict] = {}
    __user_ttl: int = 1800  # time to live in seconds

    __queue_users_to_remind: list[int] = []
    __queue_reminder_channel: int = 1021477531733471314
    __queue_userids: list[int] = []
    __queue_refresh_secs: int = 5

    __bot: DiscordBot

    async def attach(self, bot: DiscordBot):
        """
        Attach `bot` to this instance of `State`.

        Required for sending a message within `State.__queue_tick()`.

        :param: bot: discord.ext.commands.Bot - The Discord bot
        """
        self.__bot = bot
        asyncio.ensure_future(self.__queue_tick())

    async def add_user_to_queue_reminders(self, user_id: int) -> bool:
        """
        Add a Hyper Demon UID to the list of UIDs to be reminded
        when they are third in queue.

        :param: user_id: int - The HD UID to add

        :returns: bool: whether they were added successfully
        """
        # returns: bool :: whether the user was added to the queue
        if user_id in self.__queue_users_to_remind:
            return False

        self.__queue_users_to_remind.append(user_id)
        return True

    async def get_pvp_queue(self) -> list[int]:
        """
        Get the current PvP "snyper demon" queue.

        :returns: list[int]: HD User IDs in queue
        """
        return self.__queue_userids

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
                self.__queue_userids = queue_list[queue_userids_offset:]

    async def __queue_tick(self) -> None:
        QUEUE_REMINDER_CHANNEL = self.__bot.fetch_channel(
                self.__queue_reminder_channel
        )

        while True:
            id_lookup = load_map_dict()

            await self.__refresh_queue()

            if len(self.__queue_userids) > 2:
                for user_id in self.__queue_users_to_remind:
                    if self.__queue_userids[2] == user_id:
                        user_discord_id = id_lookup[user_id]
                        await QUEUE_REMINDER_CHANNEL.send(
                            f"<@{user_discord_id}>, you're up next! Get ready!"
                        )
                        self.__queue_users_to_remind.remove(user_id)

            await asyncio.sleep(self.__queue_refresh_secs)

    async def get_user(self, user_id: int) -> dict:
        """
        Get HD User information for a given HD User ID.
        If the cached info is older than `State.__user_ttl` it is refreshed.

        :param: user_id: int - The user ID to get info for

        :returns: dict: The user information
        """
        if user_id not in self.__cached_users:
            await self.__refresh_user(user_id)

        elif self.__cached_users[user_id]["eol"] < time.time():
            await self.__refresh_user(user_id)

        return self.__cached_users[user_id]

    async def __refresh_user(self, user_id: int) -> None:
        try:
            user_id = int(user_id)
        except ValueError:
            raise ValueError("user_id must be an integer")

        url = f"https://hyprd.mn/backend_dev/get_user_public.php?id={user_id}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                self.__cached_users[user_id] = await resp.json()
                self.__cached_users[user_id]["eol"] = time.time() + self.__user_ttl
