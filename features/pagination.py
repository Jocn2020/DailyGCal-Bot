from discord.ext import commands
import pytz
from .embedFormat import schedule_format
from datetime import datetime
import asyncio
import json

async def pagination(pages, client, author):
    num_pages = len(pages)
    buttons = [u"\u2B05", u"\u27A1"] # prev and next emoji
    current = 0
    embedVal = schedule_format(pages[current], num_pages)
    if num_pages > 1:
        embedVal.add_field(
            name="Page command",
            value=u"\u2B05" + ": [prev] and " + u"\u27A1" + ": [next]\n(This message expires in 7.5 seconds)",
            inline=False
        )
        reply = await author.send(embed=embedVal)
        for button in buttons:
            await reply.add_reaction(button)      

        while True:
            try:
                reaction, user = await client.wait_for("reaction_add", check=lambda reaction, user: user == author and reaction.emoji in buttons, timeout=7.5)
            except asyncio.TimeoutError:
                await reply.edit(embed=schedule_format(pages[current], num_pages))
                return 0

            else:
                previous_page = current
        
                if reaction.emoji == u"\u2B05":
                    if current > 0:
                        current -= 1
                    
                elif reaction.emoji == u"\u27A1":
                    if current < len(pages)-1:
                        current += 1
                
                if current != previous_page:  
                    embedVal = schedule_format(pages[current], num_pages)
                    embedVal.add_field(
                        name="Page command",
                        value=u"\u2B05" + ": [prev] and " + u"\u27A1" + ": [next]\n(This message expires in 10 seconds)"
                    )
                    await reply.edit(embed=embedVal)
    else:
        await author.send(embed=embedVal)



    