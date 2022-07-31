import discord
import api
import config

from discord.ext import tasks, commands
from datetime import datetime

from discord.ext import tasks, commands
from datetime import datetime

_SCHEDULE_HOUR = 12
_SCHEDULE_MIN = 0

class DailyImageCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.send_daily_image.start()
    
    @tasks.loop(minutes=1.0)
    async def send_daily_image(self):
        if not self.client.active:
            print("Client not active")
            return
        
        now = datetime.now()
        channel = self.client.get_channel(config.discord_channel_id())

        if now.hour == _SCHEDULE_HOUR and now.minute == _SCHEDULE_MIN:
            new_img, reason = api.get_random_image()

            if not new_img:
                await channel.send(reason)
                return

            try:
                await self.client.send_img_to_channel(new_img["original"], channel, new_img["title"])
            except discord.HTTPException as httpErr:
                print(f"Failed to send message: {httpErr}")
            except discord.Forbidden as forbiddenErr:
                print(f"Improper permissions to send message: {forbiddenErr}")
            except discord.InvalidArgument as invalidErr:
                print(f"Invalid message argument: {invalidErr}")

class ImageClient(discord.Client):
    def __init__(self):
        self.active = False
        super().__init__()

    async def send_img_to_channel(self, url, channel, title = ""):
        print(f"Sending image with url {url}")

        embed = discord.Embed(
            description = title if title else None
        )
        embed.set_image(url=url)

        await channel.send(embed=embed)

    async def on_ready(self):
        print(f"Logged on as {self.user}")
        self.active = True

    async def on_message(self, message):
        # Don't respond to messages from bots
        if message.author == self.user or message.author.id == 913559549309489162:
            print(f"Bot message, not responding. [{message.content[:max(len(message.content), 30)]}...]")
            return
        else:
            print(f"Got message {message.content[:max(len(message.content), 70)]}")

        channel = message.channel

        # Check to see if it's a command
        match message.content.split(" "):
            case ["!imagesearch", *query]:
                img, reason = api.get_image_from_query(" ".join(query))

                if not img:
                    await channel.send(reason)
                else:
                    await self.send_img_to_channel(img["original"], channel, img["title"])

            case ["!remaining"]:
                await channel.send(f"You have {api.num_requests_remaining()} searches remaining.")

            case ["!safesearch", *args]:
                if not args:
                    await channel.send(f"Safe search is {'enabled' if api.safe_search() else 'disabled'}.")
                elif args[0] in ["yes", "enable", "on", "true"]:
                    api.set_safe_search(True)
                    await channel.send(f"Safe search is {'enabled' if api.safe_search() else 'disabled'}.")
                elif args[0] in ["no", "disable", "off", "false"]:
                    api.set_safe_search(False)
                    await channel.send(f"Safe search is {'enabled' if api.safe_search() else 'disabled'}.")
                else:
                    await channel.send(f"Invalid argument to command !safesearch: {' '.join(args)}")

            case ["!commands"] | ["!help"]:
                await channel.send("Commands: !imagesearch <query>, !remaining, !safesearch [on/off], !commands, !help")

            case _:
                print("No command found in message.")
                pass

def main():
    client = ImageClient()
    cog = DailyImageCog(client)

    client.run(config.discord_client_token())

if __name__ == "__main__":
    main()