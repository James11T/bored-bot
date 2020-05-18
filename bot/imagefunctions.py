import json
import requests
import io
import math
from bot import dir_path
from discord import Spotify, Game, Activity
import time
from PIL import Image, ImageDraw, ImageFont

print(dir_path)
arial = f"{dir_path}/arial.ttf"
barial = f"{dir_path}/arialbd.ttf"

lower_font = lambda font_size: ImageFont.truetype(arial, font_size)
upper_font = lambda font_size: ImageFont.truetype(barial, font_size)

fonts = {"name": upper_font(56), "level": lower_font(50), "title": lower_font(40), "big": lower_font(32),
         "perc": lower_font(28), "xp": lower_font(18), "tt": lower_font(20), "tot_mes": lower_font(22)}

layouts = ["/Layout4.png"] + [f"/Layouts/wp{i}.png" for i in range(1, 37)]


def load_url_image(url):
    image_http = requests.get(url)
    if image_http.status_code == 200:
        image_obj = Image.open(io.BytesIO(image_http.content))
        return image_obj
    else:
        return None


def second_split(seconds, separator=", "):
    if seconds == 0:
        return "0s"
    mins, sec = divmod(seconds, 60)
    hrs, mins = divmod(mins, 60)
    days, hrs = divmod(hrs, 24)
    totmes = ""
    if days > 0:
        totmes += str(days) + "d"
        if hrs > 0 or mins > 0:
            totmes += separator
    if hrs > 0:
        totmes += str(hrs) + "h"
        if mins > 0:
            totmes += separator
    if mins > 0:
        totmes += str(mins) + "m"
    return totmes


def apply_transparency_mask(base_image, alpha_chan):
    base_image.convert("RGBA")
    br, bg, bb, ba = base_image.split()
    output_image = Image.merge("RGBA", [br, bg, bb, alpha_chan])
    return output_image


def generate_card(dmem, dmem_sql, dser_sql, dmem_dser_link):
    img = Image.open(dir_path + "/images" + layouts[dmem_sql.background_image])
    pfp_url = dmem.avatar_url_as(format="png", size=256)
    pfp_image = load_url_image(pfp_url).convert("RGBA")
    floor = Image.open(dir_path + "/images/Floor.png").convert("RGBA")

    resized = pfp_image.resize((218, 218))

    floor.paste(resized, mask=resized)

    transparency_mask = Image.open(dir_path + "/images/TransparencyMask.png").convert("RGBA")
    output_image = apply_transparency_mask(floor, transparency_mask.getchannel("A"))

    draw = ImageDraw.Draw(img)

    if dmem.color.value == 0:
        name_color = (255, 255, 255)
    else:
        name_color = dmem.color.to_rgb()

    draw.text((235, 14), dmem.display_name, fill=name_color, font=fonts["name"])
    draw.text((240, 90), "Level " + str(dmem_sql.level), fill=(255, 255, 255), font=fonts["level"])

    img.paste(output_image, mask=output_image)

    xp_perc = dmem_sql.xp / (10 + dmem_sql.level * 4)
    xp_length = math.floor(xp_perc * 196)
    xpbase = Image.open(dir_path + "/images/XPBar.png").convert("RGBA")
    xpd = ImageDraw.Draw(xpbase)
    xpd.rectangle([0, 0, xp_length, 52], fill=(140, 173, 130, 255))

    xp_transparency_mask = Image.open(dir_path + "/images/XPBarTransparencyMask.png").convert("RGBA")
    output_image2 = apply_transparency_mask(xpbase, xp_transparency_mask.getchannel("A")).convert("RGBA")
    oid = ImageDraw.Draw(output_image2)

    perc_str = str(math.floor(xp_perc * 100)) + "%"

    oid.text((130, 10), perc_str, font=fonts["perc"], fill=(101, 101, 101, 255))

    xp_text = f"XP: {dmem_sql.xp} / {10 + dmem_sql.level * 4}"

    w, h = draw.textsize(xp_text, font=fonts["xp"])
    x_cord = math.floor(109 - w/2)
    draw.text((x_cord, 345), xp_text, font=fonts["xp"], fill=(229, 229, 229, 255))

    totmes = "Total Voice Chat Time:"
    w, h = draw.textsize(totmes, font=fonts["tt"])
    x_cord = math.floor(109 - w / 2)
    draw.text((x_cord, 415), totmes, font=fonts["tt"], fill=(229, 229, 229, 255))

    tottmes = second_split(dmem_sql.total_seconds, separator=", ")
    w, h = draw.textsize(tottmes, font=fonts["tot_mes"])
    x_cord = math.floor(109 - w / 2)
    draw.text((x_cord, 438), tottmes, font=fonts["tot_mes"], fill=(229, 229, 229, 255))

    totmes = "Total messages: " + str(dmem_sql.total_messages)
    w, h = draw.textsize(totmes, font=fonts["tot_mes"])
    x_cord = math.floor(109 - w / 2)
    draw.text((x_cord, 375), totmes, font=fonts["tot_mes"], fill=(229, 229, 229, 255))

    totmesser = f"Total messages to {dmem.guild.name}: {dmem_dser_link.messages_sent}"
    draw.text((240, 160), totmesser, font=fonts["big"], fill=(255, 255, 255))

    totvoicser = f"Total voice chat time in {dmem.guild.name}: " + second_split(dmem_dser_link.voice_time,
                                                                                separator=", ")
    draw.text((240, 210), totvoicser, font=fonts["big"], fill=(255, 255, 255))

    totmesser = f"Joined {dmem.guild.name}: " + str(dmem.joined_at.strftime("%d/%m/%Y, %H:%M:%S"))
    draw.text((240, 270), totmesser, font=fonts["big"], fill=(255, 255, 255))

    playing = "Nothing"
    listening_to = "Nothing"
    if dmem.activities:
        for activity in dmem.activities:
            if type(activity) == Game:
                if activity.start:
                    playing = (activity.name + " for " +
                               second_split(math.floor(time.time() - activity.start.timestamp()),
                                            separator=", "))
                else:
                    playing = activity.name
            elif type(activity) == Spotify:
                listening_to = f"{activity.title} by {activity.artist}"
            elif type(activity) == Activity and playing == "Nothing":
                if "start" in activity.timestamps:
                    try:
                        playing = (activity.name + " for " +
                                   second_split(math.floor(time.time() - activity.timestamps["start"]),
                                                separator=", "))
                    except KeyError:
                        playing = "Nothing"

    draw.text((240, 320), "Playing: " + playing, font=fonts["big"], fill=(255, 255, 255))
    draw.text((240, 370), "Listening to: " + listening_to, font=fonts["big"], fill=(255, 255, 255))

    discrim = f"#{dmem.discriminator}"
    draw.text((925, 9), discrim, font=fonts["tot_mes"], fill=(86, 86, 86))

    img.paste(output_image2, mask=output_image2, box=(11, 288))

    img.save(dir_path + "/outputimages/card_" + dmem.name + ".png", "PNG")
    return dir_path + "/outputimages/card_" + dmem.name + ".png"


def generate_leaderboard(scores, title, guild, value_filter=(lambda x: x), offset=0, nslice=18):
    server_image_url = guild.icon_url_as(format="png", size=256)
    server_icon = load_url_image(server_image_url).convert("RGBA")

    back_image = Image.open(dir_path + "/images/LeaderboardLayout.png").convert("RGBA")
    draw = ImageDraw.Draw(back_image)

    for index, values in enumerate(scores):
        name_text = str(values[1].name)
        if len(name_text) > nslice:
            name_text = name_text[0:nslice - 3] + "..."

        draw.text((280, 160 + (40 * index)), name_text, font=fonts["perc"], fill=(255, 255, 255))
        draw.text((600 - offset, 160 + (40 * index)), str(value_filter(values[0])), font=fonts["perc"],
                  fill=(255, 255, 255))

    draw.text((235, 14), guild.name, fill=(255, 255, 255), font=fonts["name"])
    draw.text((240, 95), title + guild.name, fill=(255, 255, 255), font=fonts["title"])

    floor = Image.open(dir_path + "/images/Floor.png").convert("RGBA")
    resized = server_icon.resize((218, 218))
    floor.paste(resized, mask=resized)

    tm = Image.open(dir_path + "/images/TransparencyMask.png").convert("RGBA")
    output_image = apply_transparency_mask(floor, tm.getchannel("A"))
    back_image.paste(output_image, mask=output_image)
    back_image.save(dir_path + "/outputimages/" + guild.name + "_leaderboard.png", "PNG")
    return dir_path + "/outputimages/" + guild.name + "_leaderboard.png"
