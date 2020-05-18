from bot import client, session, dir_path
from bot.models import User, Server, Membership
from bot.imagefunctions import generate_card, generate_leaderboard, second_split
from discord import File
import json
import discord


q = session.query
backgrounds_file = f"{dir_path}/images/backgrounds.png"
backgrounds_file2 = f"{dir_path}/images/backgrounds2.png"
backgrounds_file3 = f"{dir_path}/images/backgrounds3.png"
backgrounds_file4 = f"{dir_path}/images/backgrounds4.png"


@client.command(brief="Show your profile", aliases=["me"], pass_context=True)
async def profile(ctx):
    user_sql = q(User).filter_by(id=str(ctx.author.id)).first()
    server_sql = q(Server).filter_by(id=str(ctx.message.guild.id)).first()
    membership_sql = q(Membership).filter_by(user_id=str(ctx.author.id), server_id=int(ctx.message.guild.id)).first()

    if not user_sql:
        await ctx.send("No data associated with you has been found, this has been recorded and will be investigated.")

    if not user_sql:
        await ctx.send("No data associated with this server has been found, this has been recorded and will be "
                       "investigated.")

    card = generate_card(ctx.author, user_sql, server_sql, membership_sql)
    await ctx.send(file=File(card))


@client.command(brief="Restart the bot.", pass_context=True)
async def restart(ctx):
    if str(ctx.author.id) == "172780337963728897":
        activity = discord.Game(name=f"Offline")
        await client.change_presence(status=discord.Status.do_not_disturb, activity=activity)
        await ctx.send(":repeat: Restarting")
        exit()
    else:
        await ctx.send("You cant do this.")


@client.command(brief="Show card backgrounds.", pass_context=True, aliases=["bgs"])
async def backgrounds(ctx, page: int = 1):
    if page == 1:
        await ctx.send(file=File(backgrounds_file))
    elif page == 2:
        await ctx.send(file=File(backgrounds_file2))
    elif page == 3:
        await ctx.send(file=File(backgrounds_file3))
    elif page == 4:
        await ctx.send(file=File(backgrounds_file4))


@client.command(brief="Change card background, use 0 for default.", pass_context=True, aliases=["setbg", "changebg"])
async def changebackground(ctx, background: int = None):
    if 0 <= background < 37:
        user_sql = session.query(User).filter_by(id=str(ctx.author.id)).first()
        if user_sql:
            user_sql.background_image = background
            session.commit()
            await ctx.send(ctx.author.mention + " Card background changed!")


@client.command(brief="Gets the top 10 levels in the guild.", pass_context=True, aliases=["toplevel", "topl"])
async def toplevels(ctx):
    member_sqls = []
    for member in ctx.guild.members:
        sql_obj = q(User).filter_by(id=str(member.id)).first()
        if sql_obj:
            member_sqls.append([sql_obj.level, member])

    member_sqls.sort(key=lambda x: x[0], reverse=True)
    if len(member_sqls) > 10:
        member_sqls = member_sqls[:10]

    leaderboard = generate_leaderboard(member_sqls, "Top levels in ", ctx.guild)
    await ctx.send(file=File(leaderboard))


@client.command(brief="Gets the top 10 user with the most messages sent.", pass_context=True,
                aliases=["topmessage", "topmes", "topm"])
async def topmessages(ctx):
    membership_sqls = []
    for member in ctx.guild.members:
        sql_obj = q(Membership).filter_by(user_id=str(member.id), server_id=str(ctx.guild.id)).first()
        if sql_obj:
            membership_sqls.append([sql_obj.messages_sent, member])

    membership_sqls.sort(key=lambda x: x[0], reverse=True)
    if len(membership_sqls) > 10:
        membership_sqls = membership_sqls[:10]

    leaderboard = generate_leaderboard(membership_sqls, "Top messages in ", ctx.guild)
    await ctx.send(file=File(leaderboard))


@client.command(brief="Gets the top 10 user with the most voice chat time.", pass_context=True,
                aliases=["topvoice", "topv"])
async def topvoicechat(ctx):
    membership_sqls = []
    for member in ctx.guild.members:
        sql_obj = q(Membership).filter_by(user_id=str(member.id), server_id=str(ctx.guild.id)).first()
        if sql_obj:
            membership_sqls.append([sql_obj.voice_time, member])

    membership_sqls.sort(key=lambda x: x[0], reverse=True)
    if len(membership_sqls) > 10:
        membership_sqls = membership_sqls[:10]

    leaderboard = generate_leaderboard(membership_sqls, "Top voice chat in ", ctx.guild, value_filter=second_split,
                                       offset=85, nslice=15)
    await ctx.send(file=File(leaderboard))

