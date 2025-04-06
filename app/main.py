import logging
import discord
from discord.ext import commands
import config
import asyncio

# ログの基本設定（INFOレベル以上を表示）
logging.basicConfig(level=logging.INFO)

# マインスイーパー機能
import gameModule.minesweeper as minesweeper
# news
import toolModule.news as news
# wikipedia
import toolModule.wiki as wiki
# weather
import toolModule.weather as weather
import automodModule.automod as automod

YOUR_BOT_TOKEN = config.BOT_TOKEN

# インテントを有効化
intents = discord.Intents.all()

# Botオブジェクトの生成
bot = commands.Bot(
    command_prefix='/', 
    intents=intents, 
    sync_commands=True,
    activity=discord.Game("mite*2")
)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'ログイン完了: {bot.user}')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # 自動制御（50文字以上の場合、削除と警告を実施）
    moderated = await automod.check_message(message)
    if moderated:
        return  # 自動制御に該当した場合は、以降のコマンド処理をスキップ

    # 他のコマンドも処理
    await bot.process_commands(message)

async def main():
    async with bot:
        # 同期的なモジュールの初期化
        minesweeper.setup(bot)
        news.setup(bot)
        wiki.setup(bot)
        weather.setup(bot)
        # 非同期の reaction モジュールを読み込み
        await bot.load_extension("reactionModule.reaction")
        await bot.start(YOUR_BOT_TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Botが Ctrl+C により停止しました。")