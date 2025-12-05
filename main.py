from __future__ import annotations

import os
from datetime import datetime

import discord
import pycountry

from discord import app_commands, Spotify
from discord import Embed

from dialogue.conversation import Conversation
from dialogue.message import Message
from dialogue.message import Image
from dialogue.message import File

from gateways.google_api_gateway import GoogleAPIGateway
from gateways.openai_api_gateway import OpenAIGateway

from gateways.brave_search_gateway import BraveSearchGateway
from gateways.weather_api_gateway import WeatherAPIGateway
from gateways.genius_api_gateway import GeniusAPIGateway

BOT_TOKEN = os.getenv("BOT_TOKEN")

ALIASES = ["speeb", "speebot"]
WAKE_UP = ["hi", "hey", "heya", "good *", "whats up", "yo", "hello", "happy *"]

DISCLAIMER = "\n-# SpeebGPT can make mistakes. [Find out more.](<https://github.com/Speeb04/SpeebGPT-Enhanced>)"

PROJECT_URL = "https://github.com/Speeb04/SpeebGPT-Enhanced"

# Logger for conversation history.
# Each entry is in the form of:
#
# {
#     "conversation": Conversation,
#     "message_history": list[int]
# }
#

conversations_history: list[dict[str, Conversation | list[int]]] = []

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.presences = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client=client)

# Gateways for API usage - implements singleton anyway so only one instance should occur.
google_gateway = GoogleAPIGateway()
openai_gateway = OpenAIGateway()

brave_search_gateway = BraveSearchGateway()
weather_gateway = WeatherAPIGateway()
genius_gateway = GeniusAPIGateway()


async def check_for_mention_wakeup(discord_message: discord.Message) -> bool:
    if len(discord_message.content.split()) > 1:
        # remove the non-alphanumeric characters, and make all characters lowercase (somehow, this actually works!)
        check_string = ''.join(char.lower() if char.isalnum() or char == ' ' else '' for char in list(discord_message.content))
        check_list = check_string.split(' ')

        # first case: greeting is one word long
        for alias in ALIASES:
            if alias in check_list[1] and check_list[0] in WAKE_UP:
                return True

        # second case: greeting is two words long
        if len(discord_message.content.split()) > 2:
            for alias in ALIASES:
                if alias in check_list[2] and (' '.join((check_list[0], check_list[1])) in WAKE_UP or
                                               check_list[0] == "good" or check_list[0] == "happy"):
                    return True

    # second case: via mention
    if f"<@{client.user.id}>" in discord_message.content:
        # time to create a new conversation
        discord_message.content = discord_message.content.replace(f"<@{client.user.id}>", ALIASES[0])
        return True

    # Everything else:
    return False


async def check_for_reply_wakeup(discord_message: discord.Message) -> bool:
    if discord_message.reference is None:
        return False

    get_reference_message = await discord_message.channel.fetch_message(discord_message.reference.message_id)

    if get_reference_message.author.id == client.user.id:
        return True

    return False


async def get_conversation(discord_message: discord.Message) -> Conversation:
    global conversations_history

    for conversation in conversations_history:
        if discord_message.id in conversation["message_history"]:
            return conversation["conversation"]

    raise ValueError("No conversation found")


async def create_conversation(discord_message: discord.Message) -> Conversation:
    # Creates a conversation object, adds to conversation_history, then
    # returns the newly created conversation.

    global conversations_history

    # Create new conversation
    new_conversation = Conversation()
    conversations_history.append({
        "conversation": new_conversation,
        "message_history": [discord_message.id],
    })

    return new_conversation


SUPPORTED_IMAGES = ["png", "jpg", "jpeg", "webp", "gif"]
SUPPORTED_FILES = ["pdf"]


async def create_message(discord_message: discord.Message, role: str) -> Message:
    text_content = discord_message.content

    images = []
    files = []

    for attachment in discord_message.attachments:
        if attachment.content_type.startswith("image"):
            for image_type in SUPPORTED_IMAGES:
                if attachment.content_type.lstrip("image/") == image_type:
                    images.append(Image(attachment.url))
                    break

        elif attachment.content_type == "application/pdf":
            files.append(File(attachment.filename, await attachment.read()))

    new_message = Message(role, text_content, images, files)

    return new_message


async def message_response_pipeline(discord_message: discord.Message,
                                    message: Message, conversation: Conversation):
    # First, adds the message to the conversation
    # returns a message in the form of Message, with bot response.

    # Add message to conversation
    conversation.add_message(message)

    # Get flags
    flag = google_gateway.get_flags(message.text_content)

    match flag:
        case "--web":
            await create_search_response(discord_message, message, conversation)
            return

        case "--weather":
            await create_weather_response(discord_message, message, conversation)
            return

        case "--song":
            await create_song_response(discord_message, message, conversation)
            return

        case "--artist":
            await create_artist_response(discord_message, message, conversation)
            return

        case _:
            await create_general_response(discord_message, conversation)


def add_user_information(discord_message: discord.Message) -> str:
    activity_str = ""
    user = discord_message.author
    if user.activity is None:
        return ""

    for activity in user.activities:
        if isinstance(activity, Spotify):
            activity_str += f"The user is currently listening to: {activity.title} by {activity.artist}."
        else:
            try:
                activity_str += f"The user is playing {activity.name}. It has the following details: {activity.details}-{activity.state} \n"
            except Exception:
                pass

    return activity_str


def get_history_list(conversation: Conversation) -> list:
    for past_conversation in conversations_history:
        if past_conversation["conversation"] == conversation:
            return past_conversation["message_history"]

    raise ValueError("No conversation found")


async def create_search_response(discord_message: discord.Message,
                                 message: Message, conversation: Conversation):
    seo_optimized = google_gateway.search_engine_optimization(message.text_content)
    search_results = brave_search_gateway.concise_search(seo_optimized)

    summarize_results = ""
    for i in range(len(search_results)):
        summarize_results += (f"Source {i}:\ntitle: {search_results[i]['title']}\n"
                              f"description: {search_results[i]['description']}\n\n")

    system_message = Message("system", f"below are some search results to help answer the user's query:\n{summarize_results}")
    conversation.add_message(system_message)

    message_history = conversation.to_list_dict()
    response = openai_gateway.generate_response(message_history)

    assistant_message = Message("assistant", response)
    conversation.add_message(assistant_message)

    embed = generate_search_embed(seo_optimized, search_results)

    sent_message = await discord_message.channel.send(response + DISCLAIMER, embed=embed)

    message_history_list = get_history_list(conversation)
    message_history_list.append(sent_message.id)


def generate_search_embed(search_term: str, search_results: list[dict[str, str]]) -> Embed:
    embed = Embed(title=f"Searched for: {search_term}", description="via search.brave.com", color=0xfab9ff)
    embed.set_author(name=client.user.name, url=PROJECT_URL, icon_url=client.user.avatar.url)
    for result in search_results:
        embed.add_field(name=f"{result['hostname']}: {result['title']}", value=result['url'], inline=False)
    embed.set_footer(text="I am a bot, and this action was performed automatically.")
    embed.timestamp = datetime.now()

    return embed


def weather_summary_string(weather_response: dict) -> str:
    return f"""
    weather description: {weather_response['description']}
    current temperature: {weather_response['temp']}°C
    minimum temperature: {weather_response['temp_min']}°C
    maximum temperature: {weather_response['temp_max']}°C
    feels-like temperature: {weather_response['feels_like']}°C

    sunrise time: {weather_response['sunrise_time']}
    sunset time: {weather_response['sunset_time']}

    wind speed: {weather_response['wind_speed']}km/h
    wind direction: {weather_response['wind_direction']}

    visibility: {weather_response['visibility']}
    """


async def create_weather_response(discord_message: discord.Message,
                            message: Message, conversation: Conversation):
    get_location = google_gateway.attain_location_information(message.text_content)
    city, country = get_location.split(', ')
    weather_results = weather_gateway.weather_lookup(f"{city},{country}")

    weather_summary = weather_summary_string(weather_results)

    system_message = Message("system", f"Below is the weather info for {weather_results['city']} in json format. "
                                       f"The units are in metric. Use it to answer the user's prompt and help them address their needs. "
                                      f"Round numbers.\n" + weather_summary)
    conversation.add_message(system_message)

    message_history = conversation.to_list_dict()
    response = openai_gateway.generate_response(message_history)

    assistant_message = Message("assistant", response)
    conversation.add_message(assistant_message)

    embed = generate_weather_embed(weather_results)

    sent_message = await discord_message.channel.send(response + DISCLAIMER, embed=embed)

    message_history_list = get_history_list(conversation)
    message_history_list.append(sent_message.id)


def generate_weather_embed(weather_response: dict) -> Embed:
    icon_url = f"https://openweathermap.org/img/wn/{weather_response['icon']}@4x.png"
    country = pycountry.countries.get(alpha_2=weather_response['country'])
    embed = Embed(title=f"Weather Forecast in {weather_response['city']}, {country.name}",
                  url="https://openweathermap.org/",
                  description="Via openweathermap.org", color=0xfab9ff)
    embed.set_thumbnail(url=icon_url)
    embed.set_author(name=client.user.name, url=PROJECT_URL, icon_url=client.user.avatar.url)

    weather_description = ' '.join(
        word.capitalize() for word in weather_response['description'].split(' '))

    if weather_response['rain'] != 0:
        rain_description = f"It will rain {weather_response['rain']['1h']}mm/h 🌧️"
    elif weather_response['snow'] != 0:
        rain_description = f"It will snow {weather_response['snow']['1h']}mm/h 🌧️"
    else:
        rain_description = "There is no rain outside currently ☀️"

    embed.add_field(name=weather_description,
                    value=f"Wind of {weather_response['wind_speed']}km/h from the {weather_response['wind_direction']}.",
                    inline=True)
    embed.add_field(
        name=f"Currently, {round(weather_response['temp'])}°C",
        value=rain_description, inline=True)

    embed.add_field(name="More Temperature Info 🌡️",
                    value=f"Today, {weather_response['city']} will have a high of {round(weather_response['temp_max'])}"
                          f"°'C' and a low of {round(weather_response['temp_min'])} °C. \nOutside, it feels like "
                          f"{round(weather_response['feels_like'])}°C",
                    inline=False)

    embed.add_field(name="Sunrise/Sunset ☀️🌙",
                    value=f"Today, sunrise will be at {weather_response['sunrise_time']}, "
                          f"and sunset will be at {weather_response['sunset_time']}.",
                    inline=True)
    embed.set_footer(text="I am a bot, and this action was performed automatically.")
    embed.timestamp = datetime.now()

    return embed


async def create_song_response(discord_message: discord.Message,
                                 message: Message, conversation: Conversation):
    user_info = add_user_information(discord_message)
    if user_info == "":
        song_details = google_gateway.attain_song_information(message.text_content)
    else:
        song_details = google_gateway.attain_song_information(f"(The user is playing: {user_info})\n" + message.text_content)
    song_name, song_artists = song_details.split('\n')
    song_artists = song_artists.split(',')
    for i in range(len(song_artists)):
        song_artists[i] = song_artists[i].strip("\"")

    song_info = genius_gateway.get_song_info(song_name, song_artists[0])

    system_message = Message("system", f"below is some information to help answer the user's query:\n{
    song_info['description']}")

    conversation.add_message(system_message)

    message_history = conversation.to_list_dict()
    response = openai_gateway.generate_response(message_history)

    assistant_message = Message("assistant", response)
    conversation.add_message(assistant_message)

    embed = await generate_song_embed(song_info)

    sent_message = await discord_message.channel.send(response + DISCLAIMER, embed=embed)

    message_history_list = get_history_list(conversation)
    message_history_list.append(sent_message.id)


async def generate_song_embed(song_info: dict) -> Embed:
    description = song_info['description'].split('\n')[0]
    if len(description) > 1024:
        description = description[0:1000] + '...'
    embed = Embed(title=song_info['title'], url=song_info['url'],
                  description="via genius.com", color=0xfab9ff)
    embed.set_author(name=client.user.name, url=PROJECT_URL, icon_url=client.user.avatar.url)
    embed.set_thumbnail(url=song_info['icon_url'])
    embed.add_field(name="Description", value=description, inline=False)
    embed.add_field(name="Album", value=song_info['album'], inline=True)
    embed.add_field(name="Artist(s)", value=song_info['artists'], inline=True)
    embed.add_field(name="Release Date", value=song_info['release_date'], inline=True)
    embed.set_footer(text="I am a bot, and this action was performed automatically.")
    embed.timestamp = datetime.now()

    return embed


async def create_artist_response(discord_message: discord.Message,
                                 message: Message, conversation: Conversation):
    user_info = add_user_information(discord_message)
    if user_info == "":
        artist_details = google_gateway.attain_artist_information(message.text_content)
    else:
        artist_details = google_gateway.attain_artist_information(f"(The user is playing: {user_info})\n" + message.text_content)

    artist_info = genius_gateway.get_artist_info(artist_details)

    system_message = Message("system", f"below is some information to help answer the user's query:\n{
    artist_info['description']}")

    conversation.add_message(system_message)

    message_history = conversation.to_list_dict()
    response = openai_gateway.generate_response(message_history)

    assistant_message = Message("assistant", response)
    conversation.add_message(assistant_message)

    embed = await generate_artist_embed(artist_info)

    sent_message = await discord_message.channel.send(response + DISCLAIMER, embed=embed)

    message_history_list = get_history_list(conversation)
    message_history_list.append(sent_message.id)


async def generate_artist_embed(artist_info: dict) -> Embed:
    description = artist_info['description'].split('\n')[0]
    if len(description) > 1024:
        description = description[0:1000] + '...'

    embed = Embed(title=artist_info['name'], url=artist_info['url'],
                  description="via genius.com", color=0xfab9ff)
    embed.set_author(name=client.user.name, url=PROJECT_URL, icon_url=client.user.avatar.url)
    embed.set_thumbnail(url=artist_info['icon_url'])
    embed.add_field(name="Description", value=description, inline=False)
    embed.add_field(name="Instagram", value=f"https://www.instagram.com/{artist_info['instagram']}",
                    inline=False)
    embed.add_field(name="X (formerly known as Twitter)",
                    value=f"https://x.com/{artist_info['twitter']}",
                    inline=False)
    embed.set_footer(text="I am a bot, and this action was performed automatically.")
    embed.timestamp = datetime.now()

    return embed


async def create_general_response(discord_message: discord.Message, conversation: Conversation):
    message_history = conversation.to_list_dict()
    response = openai_gateway.generate_response(message_history)

    assistant_message = Message("assistant", response)
    conversation.add_message(assistant_message)

    sent_message = await discord_message.channel.send(response + DISCLAIMER)

    message_history_list = get_history_list(conversation)
    message_history_list.append(sent_message.id)


@client.event
async def on_message(discord_message: discord.Message):
    global conversations_history

    # Ignore messages from bot itself
    if discord_message.author == client.user:
        return

    if await check_for_reply_wakeup(discord_message):
        try:
            conversation = await get_conversation(discord_message)
        except ValueError:
            conversation = await create_conversation(discord_message)

    elif await check_for_mention_wakeup(discord_message):
        conversation = await create_conversation(discord_message)

    else:
        return

    # At this point either we have received a conversation, or one has been created.
    async with discord_message.channel.typing():
        new_message = await create_message(discord_message, "user")
        await message_response_pipeline(discord_message, new_message, conversation)


@client.event
async def on_ready():
    await tree.sync()
    print("Bot is ready.\n-----")

    game = discord.CustomActivity("Ready to chat 💭")
    await client.change_presence(status=discord.Status.idle, activity=game)


if __name__ == "__main__":
    # Speeb v2.0 Client ID
    client.run(os.environ["DISCORD_TOKEN"])
