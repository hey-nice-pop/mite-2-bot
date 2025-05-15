import discord
from discord.ext import commands
import config
import traceback

class ReportCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        try:
            if payload.member is None:
                print("payload.member が None のため処理をスキップ (DM等)")
                return
            #botによるリアクションはスキップ
            if payload.member.bot:
                return

            # configから通報用のリアクション名を取得
            TARGET_EMOJI_NAME = config.REPORT_REACTION_NAME
            TARGET_CHANNEL_ID = int(config.REPORT_LOG_CHANNEL_ID)

            if payload.emoji.id is None:
                return
            # カスタム絵文字名が通報かどうかチェック
            if payload.emoji.name != TARGET_EMOJI_NAME:
                return

            target_channel = self.bot.get_channel(TARGET_CHANNEL_ID)
            if target_channel is None:
                print(f"転送先チャンネル(ID: {TARGET_CHANNEL_ID})が見つかりません。")
                return

            channel = self.bot.get_channel(payload.channel_id)
            if channel is None:
                print(f"投稿されたチャンネル(ID: {payload.channel_id})が見つかりません。")
                return

            try:
                message = await channel.fetch_message(payload.message_id)
            except Exception as e:
                print(f"メッセージの取得に失敗しました。channel_id: {payload.channel_id}, message_id: {payload.message_id}")
                traceback.print_exc()
                return

            target_reaction = None
            for react in message.reactions:
                if isinstance(react.emoji, (discord.Emoji, discord.PartialEmoji)):
                    if react.emoji.id == payload.emoji.id and react.emoji.name == TARGET_EMOJI_NAME:
                        target_reaction = react
                        break

            if target_reaction is None:
                print("対象のリアクションがメッセージに存在しません。")
                return

            # すでに他のユーザーによるリアクションがある場合は通報しない
            if target_reaction.count > 1:
                return

            try:
                embed = discord.Embed(
                    title="【通報】不適切な投稿が通報されました",
                    description=message.content,
                    color=0xff0000
                )
                embed.set_author(
                    name=message.author.display_name,
                    icon_url=message.author.avatar.url if message.author.avatar else None
                )
                embed.add_field(name="投稿チャンネル", value=channel.mention, inline=True)
                embed.add_field(name="投稿者", value=message.author.mention, inline=True)
                embed.add_field(name="メッセージリンク", value=f"[Jump to message]({message.jump_url})", inline=False)
                embed.set_footer(text=f"通報者: {payload.member.display_name}")
                embed.timestamp = message.created_at
            except Exception as e:
                print("Embedの作成中にエラーが発生しました")
                traceback.print_exc()
                return

            try:
                await target_channel.send(embed=embed)
            except Exception as e:
                print("Embedの送信中にエラーが発生しました")
                traceback.print_exc()
                return

        except Exception as e:
            print("on_raw_reaction_add リスナー内で予期せぬエラーが発生しました")
            traceback.print_exc()

async def setup(bot):
    try:
        await bot.add_cog(ReportCog(bot))
    except Exception as e:
        print("ReportCogの追加中にエラーが発生しました")
        traceback.print_exc()