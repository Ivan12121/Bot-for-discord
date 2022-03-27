import time
import discord
from discord.embeds import Embed
import requests
import io
import sqlite3
import random
import intents
from discord import guild
from discord.ext import commands
from discord.utils import get
from PIL import Image, ImageFont, ImageDraw

client = commands.Bot(command_prefix = '!', intents = discord.Intents.all())

connection = sqlite3.connect('server.db')
cursor = connection.cursor()

@client.event
async def on_ready():
    print('BOT ready')
    cursor.execute("""CREATE TABLE IF NOT EXISTS user(
    name TEXT,
    id INT,
    cash BIGINT
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS shop(
    role_id INT,
    id INT,
    cost BIGINT
    )""")

    for guild in client.guilds:
        for member in guild.members:
            if cursor.execute(f"SELECT id FROM user WHERE id = {member.id}").fetchone() is None:
                cursor.execute(f"INSERT INTO user VALUES ('{member}', {member.id}, 0 )")
            else: 
                pass

connection.commit()


@client.command()

async def balance(ctx, member: discord.Member = None):

    if member is None:
        await ctx.send(embed = discord.Embed(
                description = f"""Balance polzovatelya **{ctx.author}** sostovlyaet **{cursor.execute("SELECT cash FROM user WHERE id = {}".format(ctx.author.id)).fetchone()[0]} :leaves:**"""
            ))

    else:
            await ctx.send(embed = discord.Embed(
                description = f"""Balance polzovatelya **{member.mention}** sostovlyaet **{cursor.execute("SELECT cash FROM user WHERE id = {}".format(member.id)).fetchone()[0]} :leaves:**"""
            ))


@client.command()

async def add_money(ctx, member: discord.Member, amount: int):
    cursor.execute("UPDATE user SET cash = cash + {} WHERE id = {}".format(amount, member.id))
    connection.commit()

    await ctx.send(f"vot oni denushki")


@client.command()

async def del_money(ctx, member: discord.Member):
    cursor.execute("UPDATE user SET cash = cash = {} WHERE id = {}".format(0, member.id))
    connection.commit()

    await ctx.send(f"nety denezek...")


@client.command()

async def shop(ctx):
    embed = discord.Embed(title = "Magazin")

    for row in cursor.execute("SELECT role_id, cost FROM shop WHERE id = {}".format(ctx.guild.id)):
        if ctx.guild.get_role(row[0]) != None:
            embed.add_field(
                name = f"Stoimost **{row[1]}** :leaves:",
                value = f"Vi priobrete roli **{ctx.guild.get_role(row[0]).mention}**",
                inline = False
            )
        else:
            pass

    await ctx.send(embed = embed)




@client.command()

async def add_role(ctx, role: discord.Role= None, cost: int = None):
    if role is None:
        await ctx.send(f"**{ctx.author}**, ykazite roli kotoryu hotite vnesti ")
    else:
        if cost is None:
            await ctx.send(f"**{ctx.author}**, ykazite stoimosti")
        elif(cost < 0):
            await ctx.send(f"**{ctx.author}**, stoimosti ne menishe nulya")
        else:
            cursor.execute("INSERT INTO shop VALUES ({}, {}, {})".format(role.id, ctx.guild.id, cost))
            connection.commit()

            await ctx.send(f'Dobavil')



@client.command()

async def buy(ctx, role: discord.Role = None):
    if role is None:
        await ctx.send(f"**{ctx.author}**, ykazite roli kotoryu hotite priobresti")
    else:
        if role in ctx.author.roles:
            await ctx.send(f"**{ctx.author}**, y vas yze esti takaya roli")
        elif cursor.execute("SELECT cost FROM shop WHERE role_id = {}".format(role.id)).fetchone()[0] > cursor.execute("SELECT cash FROM user WHERE id = {}".format(ctx.author.id)).fetchone()[0]:
            await ctx.send(f"**{ctx.author}**, nedostatocno sredst")
        else:
            await ctx.author.add_roles(role)
            cursor.execute("UPDATE user SET cash = cash - {} WHERE id = {}".format(cursor.execute("SELECT cost FROM shop WHERE role_id = {}".format(role.id)).fetchone()[0], ctx.author.id))
            connection.commit()
            await ctx.send(f"Kupleno")



@client.command()

async def del_role(ctx, role: discord.Role = None):
    if role is None:
        await ctx.send(f"**{ctx.author}**, ykazite roli kotoryu hotite ydalit ")
    else:
        cursor.execute("DELETE FROM shop WHERE role_id = {}".format(role.id))
        connection.commit()

        await ctx.send(f'Ydalil')


@client.command()

async def casino(ctx, amount: int):
    author = ctx.message.author 

    if(amount < cursor.execute("SELECT cash FROM user WHERE id = {}".format(author.id)).fetchone()[0]):
        cursor.execute("UPDATE user SET cash = cash - {} WHERE id = {}".format(amount, author.id))
        connection.commit()
        var1 = [0, 0.5, 0.2, 1.2, 4, 10]
        rvar1 = (random.choice(var1))
        var2 = [0, 0, 0.5, 0.4, 0.3, 0.1, 2]
        rvar2 = (random.choice(var2))
        var3 = [0, 0, 0.5, 0.4, 0.3, 0.1, 1.2]
        rvar3 = (random.choice(var3))
        lastvar = [0.1, 1.2, 0.5, rvar1, rvar2, rvar3]
        multiplier = (random.choice(lastvar))
        exodus = ((int) (multiplier * amount))
        await ctx.send(embed = discord.Embed(
            description = f'Vasha stavka **{amount}** :leaves:'    
        ))
        time.sleep(1)
        await ctx.send(embed = discord.Embed(
            description = f'Krytim baraban...'    
        ))
        time.sleep(1)

        if(multiplier == 10):
            await ctx.send(embed = discord.Embed(
                description = f':money_mouth: :money_mouth: :money_mouth: **{ctx.author}** vipalo... **{multiplier}**, 10!!! AAAAAAAA vash vigrish **{exodus}!!!** :money_mouth: :money_mouth: :money_mouth:'    
            ))
        elif(multiplier == 0):
            await ctx.send(embed = discord.Embed(
                description = f':poop: :poop: :poop: **{ctx.author}** vipalo... **{multiplier}**, emae... ne povezlo tak ne povezlo, **0 na schety** :poop: :poop: :poop:'    
            ))
        else:
            await ctx.send(embed = discord.Embed(
                description = f'**{ctx.author}** vipalo... **{multiplier}**, vash vigrish sostavlyaet **{exodus}** :leaves:'    
            ))

        cursor.execute("UPDATE user SET cash = cash + {} WHERE id = {}".format(exodus, author.id))
        connection.commit()

    else:
        await ctx.send(embed = discord.Embed(
            description = f'Y tebya net stoliko deneg, vvedi menishe'    
        ))


@client.command()

async def kosti(ctx, value: int, amount: int):
    author = ctx.message.author

    if(amount < cursor.execute("SELECT cash FROM user WHERE id = {}".format(author.id)).fetchone()[0] and value > 0 or value <= 12):
        cursor.execute("UPDATE user SET cash = cash - {} WHERE id = {}".format(amount, author.id))
        connection.commit()

        variable = [1, 2, 3, 4, 5, 6]
        final = (random.choice(variable))
        exodus = ((int) (3 * amount))

        if(value == final):

            await ctx.send(embed = discord.Embed(
                description = f'Vasha stavka **{amount}** :leaves: i vashe chislo **{value}**'    
            ))
            time.sleep(1)
            await ctx.send(embed = discord.Embed(
               description = f'Kidaem kubik...'    
            ))
            time.sleep(1)

            await ctx.send(embed = discord.Embed(
                description = f'**{ctx.author}** vipalo... **{final}**, {exodus}!!!**'    
            ))
            cursor.execute("UPDATE user SET cash = cash + {} WHERE id = {}".format(exodus, author.id))
            connection.commit()
        else:
            await ctx.send(embed = discord.Embed(
                description = f'Vasha stavka **{amount}** :leaves: i vashe chislo **{value}**'    
            ))
            time.sleep(1)
            await ctx.send(embed = discord.Embed(
               description = f'Kidaem kubik...'    
            ))
            time.sleep(1)

            await ctx.send(embed = discord.Embed(
                description = f'**{ctx.author}** proebal, vipalo **{final}**'    
            ))






@client.command()

async def leaderbords(ctx):
    embed = discord.Embed(title = 'Top 10 servera')
    counter = 0

    for row in cursor.execute("SELECT name, cash FROM user ORDER BY cash DESC LIMIT 10"):
        counter += 1
        embed.add_field(
            name =  f'**#{counter}** | **{row[0]}**',
            value = f'**Balance: {row[1]}**',
            inline = False
        )


    await ctx.send(embed = embed)


@client.command(pass_context = True)

async def hello(ctx):
    author = ctx.message.author
    await ctx.send(f' {author.mention} Privet')


@client.command()

async def rand_game(ctx):
    
    emoji = discord.utils.get(ctx.guild.emojis, id=921045808365854810)
    emoji1 = discord.utils.get(ctx.guild.emojis, id=921045998426533899)
    variants = [1, 0]
    var = (random.choice(variants))

    if(var == 1):
        await ctx.send(f'{emoji}')

    else:
        await ctx.send(f'{emoji1}')


@client.command()

async def duel(ctx, member: discord.Member):
    time_mute = 60
    author = ctx.message.author
    variants = [member.mention, author.mention]
    user = (random.choice(variants))

    await ctx.send(f'duel mezhdy {member.mention} u {author.mention}')
    time.sleep(1)
    await ctx.send('1...')
    time.sleep(1)
    await ctx.send('2...')
    time.sleep(1)
    await ctx.send('3!...')
    time.sleep(1)
    await ctx.send(f'{user} proigral')

    if(user == member.mention):
        mute_role = discord.utils.get(ctx.message.guild.roles, name = 'mute')
        await member.add_roles(mute_role)
        time.sleep(time_mute)
        if(time_mute >=60):
            await member.remove_roles(mute_role)

    else:
        mute_role = discord.utils.get(ctx.message.guild.roles, name = 'mute')
        await author.add_roles(mute_role)
        time.sleep(time_mute)
        if(time_mute >=60):
            await member.remove_roles(mute_role)


@client.command()

async def id(ctx):
    await ctx.send(f'{ctx.author.id}')


@client.command()

async def user_mute(ctx, member: discord.Member):
    if(ctx.author.id == 295243966658641922):
        time_mute = 60
        member_roles = member.roles 
        mute_role = discord.utils.get(ctx.message.guild.roles, name = 'mute')
        await member.add_roles(mute_role)
        await ctx.send(f' {member.mention}, potishe')
        time.sleep(time_mute)
        if(time_mute >=60):
            await member.remove_roles(mute_role)
    else:
        await ctx.send(f'nea')


@client.command()
async def join(ctx):
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild = ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()


@client.command()
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild = ctx.guild)
    if voice and voice.is_connected():
        await voice.disconnect()
    else:
        voice = await channel.connect()


@client.command()
async def card(ctx):
    img = Image.new('RGBA', (400,200), '#232529')
    url = str(ctx.author.avatar_url)

    response = requests.get(url, stream = True)
    response = Image.open(io.BytesIO(response.content))
    response = response.convert('RGBA')
    response = response.resize((100,100 ), Image.ANTIALIAS)
    img.paste(response, (15,15, 115,115))
     
    idraw = ImageDraw.Draw(img)
    name = ctx.author.name 
    tag = ctx.author.discriminator

    headline = ImageFont.truetype('arial.ttf', size = 20)
    undertext = ImageFont.truetype('arial.ttf', size = 12)

    idraw.text((145,15), f'{name}#{tag}', font= headline)
    idraw.text((145, 50), f'ID: {ctx.author.id}', font = undertext)
    img.save('user.png')

    await ctx.send(file = discord.File(fp = 'user.png'))

token = open('token.txt', 'r').readline()

client.run(token)
 