import discord
import re
import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve token and API key from environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# YouTube API initialization
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Helper function to format video results
def format_results(results):
    return '\n'.join([f'- {title}: {url}' for title, url in results])

# Function to search YouTube
def search_youtube(query, max_results=3):
    response = youtube.search().list(
        part="snippet", q=query, maxResults=max_results, type="video"
    ).execute()

    return [
        (item['snippet']['title'], f'https://www.youtube.com/watch?v={item["id"]["videoId"]}')
        for item in response.get('items', [])
    ]

# Function to get trending music
def get_trending_music(max_results=3):
    response = youtube.videos().list(
        part="snippet", chart="mostPopular", regionCode="US",
        videoCategoryId="10", maxResults=max_results
    ).execute()

    return [
        (item['snippet']['title'], f'https://www.youtube.com/watch?v={item["id"]}')
        for item in response.get('items', [])
    ]

# Event when bot is ready
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

# Command handling logic using regular expressions
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Cek apakah pesan dimulai dengan '!'
    if not message.content.startswith('!'):
        return  # Abaikan pesan yang tidak dimulai dengan '!'

    # Cek perintah dengan regex
    if re.match(r'^!(hi|halo|hello|hey)$', message.content.lower()):
        await message.channel.send(f'Halo {message.author.name}! Gunakan `!help` untuk bantuan.')

    elif re.match(r'^!help$', message.content.lower()):
        await message.channel.send(help_message)

    elif re.match(r'^!trending$', message.content.lower()):
        results = get_trending_music()
        await message.channel.send(f'Video musik yang sedang trending:\n{format_results(results)}' if results else 'Tidak ada hasil trending.')

    elif re.match(r'^!lagu\s+(.+)', message.content.lower()):
        query = re.match(r'^!lagu\s+(.+)', message.content.lower()).group(1)
        results = search_youtube(query + ' music')
        await message.channel.send(f'Rekomendasi lagu untuk "{query}":\n{format_results(results)}' if results else 'Tidak ada hasil.')

    else:
        await message.channel.send('Perintah tidak dikenali. Gunakan `!help` untuk bantuan.')

# Help message
help_message = (
    "Berikut command yang bisa digunakan:\n"
    "- `!halo` atau `!hi`: Menyapa bot\n"
    "- `!lagu [kata kunci]`: Mencari lagu di YouTube\n"
    "- `!trending`: Menampilkan video musik yang sedang trending\n"
    "- `!help`: Menampilkan daftar perintah"
)

# Run the bot
client.run(DISCORD_TOKEN)
