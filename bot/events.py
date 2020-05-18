from bot import client, session
from bot.models import User, Server, Membership
import discord
from datetime import datetime
import time
import asyncio

q = session.query
reset_timer = 0
voice_chat_cooldowns = {}


async def voice_tick():
    print("Voice chat loop started")
    global reset_timer
    await client.wait_until_ready()
    while True:
        reset_timer += 1
        if reset_timer >= 7200:
            activity = discord.Game(name=f"Restarting")
            await client.change_presence(status=discord.Status.do_not_disturb, activity=activity)
            await client.logout()
            exit()

        for server in client.guilds:
            server_sql = q(Server).filter_by(id=str(server.id)).first()
            if not server_sql:
                server_sql = create_server(server)

            for member in server.members:
                if isinstance(member, discord.ClientUser) or member.bot:
                    continue
                if not member.voice:
                    continue
                if member.voice.afk:
                    continue
                if not member.voice.channel:
                    continue

                guild = member.voice.channel.guild
                user_sql = q(User).filter_by(id=str(member.id)).first()
                membership_sql = q(Membership).filter_by(user_id=str(member.id), server_id=str(guild.id)).first()
                if not user_sql:
                    print("User had no data")
                    user_sql = create_member(member)

                if not membership_sql:
                    membership_sql = create_membership(member, guild)

                membership_sql.voice_time += 1
                user_sql.total_seconds += 1

                xp_ready = False
                if str(member.id) not in voice_chat_cooldowns:
                    xp_ready = True
                    voice_chat_cooldowns[str(member.id)] = time.time()
                else:
                    if time.time() - voice_chat_cooldowns[str(member.id)] >= 150:
                        xp_ready = True
                        voice_chat_cooldowns[str(member.id)] = time.time()

                if xp_ready:
                    if user_sql.xp + 1 >= 10 + (user_sql.level * 4):
                        user_sql.xp = 0
                        user_sql.level += 1
                    else:
                        user_sql.xp += 1
        session.commit()
        await asyncio.sleep(1)


def create_member(dmem):
    user_sql = q(User).filter_by(id=str(dmem.id)).first()
    if user_sql:
        print("Use already exists in database")
        return None

    new_user = User(id=str(dmem.id))
    session.add(new_user)
    session.commit()
    return new_user


def create_server(dser):
    server_sql = q(Server).filter_by(id=str(dser.id)).first()
    if server_sql:
        print("Server already exists in the database")
        return None

    new_server = Server(id=str(dser.id))
    session.add(new_server)
    session.commit()
    return new_server


def create_membership(dmem, dser):
    membership_sql = q(Membership).filter_by(user_id=str(dmem.id), server_id=str(dser.id)).first()
    if membership_sql:
        print("Membership already exists in the database")
        return None

    new_membership = Membership(user_id=str(dmem.id), server_id=str(dser.id))
    session.add(new_membership)
    session.commit()
    return new_membership


@client.event
async def on_member_join(dmem):
    create_member(dmem)
    create_server(dmem.guild)
    create_membership(dmem, dmem.guild)


@client.event
async def on_guild_join(dser):
    create_server(dser)
    for dmem in dser.members:
        create_member(dmem)
        create_membership(dmem, dser)


@client.event
async def on_ready():
    client.loop.create_task(voice_tick())
    print("Bot ready at " + datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))

    activity = discord.Game(name=f">help")
    await client.change_presence(status=discord.Status.online, activity=activity)

    for server in client.guilds:
        for member in server.members:
            user_sql = q(User).filter_by(id=str(member.id)).first()
            if not user_sql:
                create_member(member)


@client.event
async def on_message(mes):
    if mes.author.bot:
        return

    if str(mes.author.id) == "172780337963728897" and mes.content.lower().startswith("sudo"):
        message_split = mes.content.split(">")
        if len(message_split) < 2:
            return

        target_id = "".join([x for x in message_split[0] if not x.lower() in ["s", "u", "d", "o"]])
        command = ">" + message_split[1]

        mes.content = command

        dmem = mes.guild.get_member(int(target_id))
        if not dmem:
            await mes.channel.send("User with that ID was not found.")
            return

        mes.author = dmem
        await client.process_commands(mes)
        return

    if not mes.content.startswith(">"):
        return

    # Create the user object if it doesnt exist
    user_sql = q(User).filter_by(id=str(mes.author.id)).first()
    if not user_sql:
        user_sql = create_member(mes.author)

    # Create the server object if it doesnt exist
    # server_sql = q(Server).filter_by(id=str(mes.guild.id)).first()
    # if not server_sql:
    #     server_sql = create_server(mes.guild)

    # Create the membership object if it doesnt exist
    membership_sql = q(Membership).filter_by(user_id=str(mes.author.id), server_id=str(mes.guild.id)).first()
    if not membership_sql:
        membership_sql = create_membership(mes.author, mes.guild)

    membership_sql.messages_sent += 1
    user_sql.total_messages += 1

    if time.time() - membership_sql.last_message >= 4:
        if user_sql.xp + 1 >= 10 + (user_sql.level * 10):
            user_sql.xp = 0
            user_sql.level += 1
            await mes.channel.send(f"{mes.author.mention} You are now level **{user_sql.level}**!")
        else:
            user_sql.xp += 1

    session.commit()

    await client.process_commands(mes)
