import discord
import asyncio
import os
import aiohttp
import aiofiles
import random
from PIL import Image
import hitherdither
from giphypop import upload

f = open("token.txt","r")
token = file.read()
f.close()

error_msgs = [
    "something really broke",
    "broken program alert",
    "error code: 56709",
    "(you) ▄︻̷̿┻̿═━一              (the program)",
    "god why",
    "i'm glad i added an array of possible error messages to choose from. speaking of which, there is an error",
    "gah my brain!",
    "<:dan:555135217602527242>",
    ":(",
    "since there is absolutely nothing wrong with the code, it appears you are trying to break the program. this incident will be reported",
    "why was i programmed to feel self hatred"
]

palette = hitherdither.palette.Palette(
    [0xffffff,0xff0000,0x000000,0x00ff00,0x0000ff,0xff00ff,0x00ffff,0xffff00]
)

async def get_file_from(message):
    if len(message.attachments) > 0:
        attachment = message.attachments[0]
        #get and download file
        filename = "tmp/"+attachment.filename
        async with aiohttp.ClientSession(headers={"Referer": "https://discordapp.com"}) as session:
            async with session.get(attachment.url) as resp:
                f = await aiofiles.open(filename, mode='wb')
                await f.write(await resp.read())
                await f.close()
    else:
        for substring in message.content.replace("\n"," ").split(" "):
            if substring.startswith("http"):
                if ("tenor" in substring or "gfycat" in substring) and not ".gif" in substring: url = substring.split("?")[0]+".gif"
                elif "giphy" in substring: url = "https://media.giphy.com/media/"+substring.split("/")[4]+"/giphy.gif"
                else: url = substring.split("?")[0]
        filename = "tmp/"+str(random.randint(10000000,99999999))+"."+url.split(".")[len(url.split("."))-1]
        async with aiohttp.ClientSession(headers={"Referer": "https://discordapp.com"}) as session:
            async with session.get(url) as resp:
                f = await aiofiles.open(filename, mode='wb')
                await f.write(await resp.read())
                await f.close()
    return filename

bot = discord.Client()

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("!help"))
    print("image bot is now ready")

@bot.event
async def on_message(message):
    if message.content.startswith("!help"):
        embed = discord.Embed(name="command list", color=0xddff00)
        embed.set_author(name="commands list (necessary) [optional]")
        embed.add_field(name="!shift (shiftyness) [url]", value="bitshifts an image. looks cool", inline = True)
        embed.add_field(name="!avatar (@someone)", value="grabs someone's avatar", inline = True)
        embed.add_field(name="!dither [url]", value="dither time", inline = True)
        embed.add_field(name="!impact (top text) | (bottom text) [url]", value="funny image machine", inline = True)
        embed.add_field(name="!jpg [quality from 1-100] [url]", value="ah! the quality!", inline = True)
        embed.add_field(name="!caption (caption) [url]", value="ifunny gif caption", inline = True)
        embed.add_field(name="!shuffle [url]", value="turn gif to mush", inline = True)
        embed.set_thumbnail(url="https://thumbs.dreamstime.com/z/help-wanted-vector-clip-art-31368648.jpg")
        await message.channel.send(embed=embed)

    if message.content.lower().startswith("!shift"):
        if len(message.attachments) == 0 and not "http" in message.content: await message.channel.send("you gotta attach an image")
        elif len(message.content.split(" ")) < 2 or not message.content.split(" ")[1].isdigit(): await message.channel.send("you gotta specify the amount of shiftage")
        elif int(message.content.split(" ")[1]) == 0: await message.channel.send("shut it")
        elif int(message.content.split(" ")[1]) > 7 or int(message.content.split(" ")[1]) < 1: await message.channel.send("that number sucks. try something from 1 to 7")
        else: 
            try:
                status = await message.channel.send("getting file...")
                await bot.change_presence(activity=discord.Game("!help"),status=discord.Status.dnd)
                await message.channel.trigger_typing()
                filename = await get_file_from(message)

                #turn into bmp
                await status.edit(content="converting file...")
                im = Image.open(filename)
                canvas = Image.new('RGBA', im.size, (54,57,63,255))
                if im.mode == "RGBA": canvas.paste(im, mask=im)
                else: canvas.paste(im)
                canvas.thumbnail([im.width, im.height], Image.ANTIALIAS)
                canvas = canvas.convert('RGB')
                converted_file = filename.replace(filename.split(".")[len(filename.split("."))-1],"") + "bmp"
                canvas.save(converted_file)
                

                #bitshift!
                await message.channel.trigger_typing()
                await status.edit(content="bitshifting...")
                shifted_file = converted_file.replace("bmp","_shifted.bmp")
                shift_count = int(message.content.split(" ")[1])
                increment = 1
                with open(converted_file, 'rb') as f:
                    bits = bytearray(f.read())
                start_byte = bits[10]
                i = 0
                goodly_named_variable = (len(bits) - start_byte)
                nf = open(shifted_file,"ab")
                for i in range(0,goodly_named_variable,increment):
                    bits[start_byte + i] = (bits[start_byte + i] << shift_count) & 0xFF
                nf.write(bits)
                nf.close()

                #reconvert
                await status.edit(content="reconverting file...")
                final_file = shifted_file.replace("bmp","png")
                im = Image.open(shifted_file)
                im.save(final_file)
                
                #send
                await status.edit(content="sending...")
                await message.channel.send(file=discord.File(final_file))
                await status.delete()
                os.remove(final_file)
                os.remove(filename)
                os.remove(converted_file)
                os.remove(shifted_file)
                await bot.change_presence(activity=discord.Game("!help"),status=discord.Status.online)

            except:
                await message.channel.send(random.choice(error_msgs))

    if message.content.lower().startswith("!avatar"):
        if len(message.mentions) == 0: await message.channel.send("you gotta @ the user to get the avatar")
        else:
            try:
                await bot.change_presence(activity=discord.Game("!help"),status=discord.Status.dnd)
                status = await message.channel.send("getting avatar...")
                await message.channel.trigger_typing()

                #download
                url = str(message.mentions[0].avatar_url).split("?size")[0]
                og_file = "tmp/"+str(random.randint(10000000,99999999))+"."+url.split(".")[len(url.split("."))-1]
                async with aiohttp.ClientSession(headers={"Referer": "https://discordapp.com"}) as session:
                    async with session.get(url+"?size=1024") as resp:
                        f = await aiofiles.open(og_file, mode='wb')
                        await f.write(await resp.read())
                        await f.close()
                
                #convert
                await status.edit(content="converting avatar...")
                final_file = og_file.replace("webp","png")
                im = Image.open(og_file)
                if not im.mode == 'RGBA':
                    im = im.convert('RGBA')
                im.save(final_file)
                os.remove(og_file)

                #send
                await status.edit(content="sending...")
                await message.channel.send(file=discord.File(final_file))
                await status.delete()
                os.remove(final_file)
                await bot.change_presence(activity=discord.Game("!help"),status=discord.Status.online)
                
            except:
                await message.channel.send(random.choice(error_msgs))

    if message.content.lower().startswith("!dither"):
        if len(message.attachments) == 0 and not "http" in message.content: await message.channel.send("you gotta attach an image")
        else: 
            try:
                status = await message.channel.send("getting file...")
                await bot.change_presence(activity=discord.Game("!help"),status=discord.Status.dnd)
                await message.channel.trigger_typing()
                filename = await get_file_from(message)

                #turn into small png
                await status.edit(content="converting file...")
                im = Image.open(filename)
                canvas = Image.new('RGBA', im.size, (54,57,63,255))
                if im.mode == "RGBA": canvas.paste(im,mask=im)
                else: canvas.paste(im)
                canvas.thumbnail([im.width, im.height], Image.ANTIALIAS)
                canvas = canvas.convert('RGB')
                im2 = canvas.resize((canvas.size[0]//4,canvas.size[1]//4),Image.NEAREST)
                converted_file = filename.replace(filename.split(".")[len(filename.split("."))-1],"") + "png"
                im2.save(converted_file)
                
                #dither
                await status.edit(content="dithering file...")
                img = Image.open(converted_file)
                img_dithered = hitherdither.ordered.bayer.bayer_dithering(img, palette, [256/4, 256/4, 256/4], order=8)
                new_filename = converted_file.replace(".","_dithered.")
                img_dithered_resized = img_dithered.resize((img_dithered.size[0]*4,img_dithered.size[1]*4),Image.NEAREST)
                img_dithered_resized.save(new_filename)

                #send
                await status.edit(content="sending...")
                await message.channel.send(file=discord.File(new_filename))
                await status.delete()
                os.remove(new_filename)
                os.remove(filename)
                try: os.remove(converted_file)
                except: pass
                await bot.change_presence(activity=discord.Game("!help"),status=discord.Status.online)
            
            except:
                await message.channel.send(random.choice(error_msgs))

    if message.content.lower().startswith("!jpg"):
        if len(message.attachments) == 0 and not "http" in message.content: await message.channel.send("you gotta attach an image")
        else: 
            if len(message.content.split(" "))>1 and message.content.split(" ")[1].isdigit(): quality = int(message.content.split(" ")[1])
            else: quality = 10

            if quality < 1 or quality > 100:
                await message.channel.send("sorry, humans can't comprehend images of this quality")
                return

            try:
                #get file
                status = await message.channel.send("getting file...")
                await bot.change_presence(activity=discord.Game("!help"),status=discord.Status.dnd)
                await message.channel.trigger_typing()
                filename = await get_file_from(message)

                #lower quality
                await status.edit(content="jpg-ifying...")
                im = Image.open(filename)
                canvas = Image.new('RGBA', im.size, (54,57,63,255))
                if im.mode == "RGBA": canvas.paste(im,mask=im)
                else: canvas.paste(im)
                canvas.thumbnail([im.width, im.height], Image.ANTIALIAS)
                canvas = canvas.convert('RGB')
                converted_file = filename.replace(filename.split(".")[len(filename.split("."))-1],"") + "jpg"
                canvas.save(converted_file, quality=quality)

                #send
                await status.edit(content="sending...")
                await message.channel.send(file=discord.File(converted_file))
                await status.delete()
                os.remove(converted_file)
                await bot.change_presence(activity=discord.Game("!help"),status=discord.Status.online)
            
            except:
                await message.channel.send(random.choice(error_msgs))

    if message.content.lower().startswith("!impact"):
        if len(message.attachments) == 0 and not "http" in message.content: await message.channel.send("you gotta attach an image")
        else: 
            try:
                msg = message.content.split(" ")
                new_msg = ""
                for piece in msg:
                    if not piece == "!impact" and not piece.startswith("http"):
                        new_msg = new_msg + piece + " "
                top = new_msg.split("|")[0]
                bottom = new_msg.split("|")[1]
            except:
                await message.channel.send("make sure you have !impact (top text) | (bottom text) [url]")
                return
            try:
                #get image
                await message.channel.trigger_typing()
                status = await message.channel.send("getting file...")
                await bot.change_presence(activity=discord.Game("!help"),status=discord.Status.dnd)
                filename = await get_file_from(message)
                
                await status.edit(content="converting file...")
                im = Image.open(filename)
                canvas = Image.new('RGBA', im.size, (54,57,63,255))
                if im.mode == "RGBA": canvas.paste(im, mask=im)
                else: canvas.paste(im)
                canvas.thumbnail([im.width, im.height], Image.ANTIALIAS)
                canvas = canvas.convert('RGB')
                converted_file = filename.replace(filename.split(".")[len(filename.split("."))-1],"") + "jpg"
                canvas.save(converted_file,quality=100)

                #make image
                await status.edit(content="impactifying...")
                new_filename = "tmp/"+str(random.randint(10000000,99999999))+".jpg"
                os.system("python impact.py {0} \"{1}\" \"{2}\" {3}".format(converted_file,top,bottom,new_filename))

                #send
                await status.edit(content="sending...")
                await message.channel.send(file=discord.File(new_filename))
                await status.delete()
                os.remove(new_filename)
                os.remove(converted_file)
                try: os.remove(filename)
                except: pass
                await bot.change_presence(activity=discord.Game("!help"),status=discord.Status.online)
            
            except:
                await message.channel.send(random.choice(error_msgs))



    if message.content.lower().startswith("!caption"):
        if len(message.attachments) == 0 and not "http" in message.content: await message.channel.send("you gotta attach an image")
        else: 
            try:
                msg = message.content.replace("\n"," ").split(" ")
                caption_text = ""
                for piece in msg:
                    if not piece == "!caption" and not piece.startswith("http"):
                        caption_text = caption_text + piece + " "
                        caption_text = caption_text.replace("\n","")
            except:
                await message.channel.send("make sure you have !caption (text) [url]")
                return
            if True:#try:
                #get image
                await message.channel.trigger_typing()
                status = await message.channel.send("getting file...")
                await bot.change_presence(activity=discord.Game("!help"),status=discord.Status.dnd)
                filename = await get_file_from(message)

                #make image
                await status.edit(content="captioning...")
                new_filename = "tmp/"+str(random.randint(10000000,99999999))+".gif"
                os.system("python3.6 caption.py {0} \"{1}\" {2}".format(filename,caption_text,new_filename))

                #send
                await status.edit(content="uploading...")
                gif = upload(["bot","image"],new_filename,username="imagebot",api_key="XPumBNP6Lw0QijMqlvXwVNXBo3udxFfn")
                await message.channel.send(gif.url)
                await status.delete()
                os.remove(new_filename)
                #try: os.remove(filename)
                #except: pass
                await bot.change_presence(activity=discord.Game("!help"),status=discord.Status.online)
            
            #except:
            #    await message.channel.send(random.choice(error_msgs))







    if message.content.lower().startswith("!shuffle"):
        if len(message.attachments) == 0 and not "http" in message.content: await message.channel.send("you gotta attach an image")
        else: 
            if True:#try:
                #get image
                await message.channel.trigger_typing()
                status = await message.channel.send("getting file...")
                await bot.change_presence(activity=discord.Game("!help"),status=discord.Status.dnd)
                filename = await get_file_from(message)

                #make image
                await status.edit(content="shuffling...")
                new_filename = "tmp/"+str(random.randint(10000000,99999999))+".gif"
                os.system("python shuffle.py {0} {1}".format(filename,new_filename))

                #send
                await status.edit(content="uploading...")
                gif = upload(["bot","image"],new_filename,username="imagebot",api_key="XPumBNP6Lw0QijMqlvXwVNXBo3udxFfn")
                await message.channel.send(gif.url)
                await status.delete()
                os.remove(new_filename)
                try: os.remove(filename)
                except: pass
                await bot.change_presence(activity=discord.Game("!help"),status=discord.Status.online)
            
            else:#except:
                await message.channel.send(random.choice(error_msgs))                


bot.run(token)