import discord
from discord.ext import commands
import config

# マインスイーパー機能
import gameModule.minesweeper as minesweeper
#news
import toolModule.news as news
#wikipedia
import toolModule.wiki as wiki
#weather
import toolModule.weather as weather
#voice
import toolModule.voice as voice

YOUR_BOT_TOKEN = config.BOT_TOKEN

# インテントを有効化
intents = discord.Intents.all()

# Botオブジェクトの生成
bot = commands.Bot(
    command_prefix='/', 
    intents=intents, 
    sync_commands=True,
    activity=discord.Game("見て")
)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'ログイン完了: {bot.user}')


minesweeper.setup(bot)

news.setup(bot)

wiki.setup(bot)

weather.setup(bot)

voice.setup(bot)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # 他のコマンドも処理
    await bot.process_commands(message)

# Discordボットを起動
bot.run(YOUR_BOT_TOKEN)