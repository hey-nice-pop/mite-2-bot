# automodModule/automod.py
import discord
import re

async def check_message(message: discord.Message) -> bool:
    """
    メッセージが50文字以上の場合は削除し、同じチャンネルにカード形式の警告メッセージを送信する。
    ただし、メッセージにURLが含まれている場合は、50文字以上でも削除を行いません。
    警告処理を行った場合は True を返します。
    """
    # URLが含まれている場合は自動制御をスキップ
    if re.search(r'https?://', message.content):
        return False

    if len(message.content) >= 50:
        try:
            await message.delete()
            print(f"Deleted long message from {message.author}")
        except discord.DiscordException as e:
            print("メッセージ削除に失敗しました:", e)
            return False

        try:
            # Embed（カード形式）の警告メッセージを作成
            embed = discord.Embed(
                title="Erorr",
                description=f"{message.author.mention} 50文字以上のメッセージは送信できません。",
                color=discord.Color.red()
            )
            embed.set_footer(text="このメッセージは10秒後に自動で削除されます")
            
            # delete_after=10 で10秒後に自動削除
            await message.channel.send(embed=embed, delete_after=10)
        except discord.DiscordException as e:
            print("警告メッセージ送信に失敗しました:", e)
        return True
    return False