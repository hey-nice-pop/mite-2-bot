# automodModule/automod.py
import discord
import re
import config

DELEATED_LOG_CHANNEL_ID = int(config.DELEATED_LOG_CHANNEL_ID)  # 削除ログのチャンネルID

async def check_message(message: discord.Message) -> bool:
    """
    メッセージ内の URL 部分を除いた文字数が50文字以上の場合、
    まず同じチャンネルにEmbed形式の警告メッセージを送信し、その後元のメッセージを削除します。
    さらに、削除されたメッセージ内容を削除ログチャンネルにカードUI（Embed）で転送します。
    
    ※ URL 部分はカウントに含まれません。
    ただし、以下の場合は自動制御をスキップします:
      - 送信者が管理者権限を持っている場合
    警告処理を行った場合は True を返します。
    """
    # ギルド内で管理者権限を持つユーザーの場合はスキップ
    #if message.guild is not None and message.author.guild_permissions.administrator:
    #    return False

    # URLを除去して残りの文字列を取得（URLは "http://" または "https://" 以降の連続する非空白文字）
    effective_content = re.sub(r'https?://\S+', '', message.content).strip()

    if len(effective_content) >= 140:
        try:
            await message.delete()
            print(f"Deleted long message from {message.author}")
        except discord.DiscordException as e:
            print("メッセージ削除に失敗しました:", e)
            return False

        # 警告メッセージ送信（送信後10秒で自動削除）
        try:
            warning_embed = discord.Embed(
                title="警告",
                description=f"{message.author.mention} URL を除いた50文字以上のメッセージは送信できません。",
                color=discord.Color.red()
            )
            warning_embed.set_footer(text="このメッセージは10秒後に削除されます")
            await message.channel.send(embed=warning_embed, delete_after=10)
        except discord.DiscordException as e:
            print("警告メッセージ送信に失敗しました:", e)

        # 削除ログチャンネルへ削除されたメッセージ内容をEmbed形式で転送
        try:
            if message.guild is not None:
                log_channel = message.guild.get_channel(DELEATED_LOG_CHANNEL_ID)
                if log_channel is None:
                    log_channel = await message.guild.fetch_channel(DELEATED_LOG_CHANNEL_ID)
                if log_channel is not None:
                    log_embed = discord.Embed(
                        title="削除ログ",
                        description="以下のメッセージが URL を除いた文字数が50文字以上により自動削除されました。",
                        color=discord.Color.dark_gray()
                    )
                    log_embed.add_field(name="送信者", value=message.author.mention, inline=True)
                    log_embed.add_field(name="チャンネル", value=message.channel.mention, inline=True)
                    
                    # メッセージ内容が長すぎる場合は省略（1024文字以内に収める）
                    msg_content = message.content if message.content else "なし"
                    if len(msg_content) > 1024:
                        msg_content = msg_content[:1021] + "..."
                    log_embed.add_field(name="メッセージ内容", value=msg_content, inline=False)
                    log_embed.timestamp = message.created_at
                    await log_channel.send(embed=log_embed)
                else:
                    print("削除ログチャンネルが見つかりません")
            else:
                print("DMのメッセージはログに転送しません")
        except discord.DiscordException as e:
            print("削除ログ送信に失敗しました:", e)
        return True

    return False