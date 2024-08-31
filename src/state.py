import time
import aiohttp
import asyncio
from bidict import bidict
import json

class State:
    users: dict[int, dict] = {}
    user_ttl: int = 1800  # time to live in seconds

    # user (dict):
    # {
    #   "name": "username"
    #   "eol": 123456 <-- value of time.time()
    # }                   (PLUS time to live, in seconds) when cached
    queue_users_to_remind: list[int] = []

    bot: object

    def __init__(self, bot: object):
        asyncio.run(self.__queue_tick())
        self.bot = bot

    async def add_user_to_queue(self, user_id: int) -> bool:
        # returns: bool :: whether the user was added to the queue
        # (false = already asked to be reminded)

        if user_id in self.queue_users_to_remind:
            return False

        self.queue_users_to_remind.append(user_id)
        return True
    
    async def __queue_tick(self) -> None:
        while True:
            if len(self.queue_users_to_remind) > 0:

                for user_id in self.queue_users_to_remind:
                    
                    # load the id dictionary
                    with open("id_dictionary.json", "r") as outfile:
                        id_dict = json.load(outfile)
                    id_lookup = bidict(id_dict)
                    game_id = id_lookup.inverse[user_id]

                    # logic to determine spot position
                    async with aiohttp.ClientSession() as session:
                        async with session.post('http://104.207.135.180:44454/vs/queue') as resp:
                            raw_queue = await resp.content.read(4)
                            version_offset = 0
                            online_player_count_offset = 1
                            queue_total_offset = 2
                            queue_returned_offset = 3
                            queue_userids_offset = 4
                            queue_list = []
                            while raw_queue:
                                int_val = int.from_bytes(raw_queue, "little")
                                queue_list.append(int_val)
                                raw_queue = await resp.content.read(4)
                            online_player_count = queue_list[online_player_count_offset]
                            queue_total = queue_list[queue_total_offset]
                            queue_returned =  queue_list[queue_returned_offset]
                            queue_userids = queue_list[queue_userids_offset:]
                    next_up = queue_userids[2]
                    if game_id not in queue_userids:
                        await interaction.channel.send(f"You are not in the queue, please join the queue to turn on a reminder")
                    elif len(queue_userids)
                    else:
                        

                    await self.bot.send_message(self.channel_id, "lock tf in!!!")
                    self.queue_users_to_remind.remove(user_id)


            asyncio.sleep(5)
    
    async def get_user(self, user_id: int) -> dict:
        if (user_id not in self.users):
            await self.__refresh_user(user_id)

        elif (self.users[user_id]["eol"] < time.time()):
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