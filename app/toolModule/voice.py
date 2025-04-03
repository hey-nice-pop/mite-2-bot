import discord
from discord.ext import commands
from discord.player import FFmpegPCMAudio
import pyopenjtalk
import numpy as np
import pydub
import tempfile
import os
import re
import emoji

# ギルドIDをキーとして、ボイスクライアントとテキストチャンネルIDのペアを保持する辞書
voice_clients = {}

def setup(bot):
    @bot.tree.command(name='join', description='Voice channelに参加します。')
    async def join(interaction: discord.Interaction):
        guild_id = interaction.guild.id
        user_voice_channel = interaction.user.voice.channel if interaction.user.voice else None

        # BOTが既にボイスチャンネルに参加しているかチェック
        if guild_id in voice_clients:
            client_info = voice_clients[guild_id]
            # 別のボイスチャンネルに移動するリクエストかチェック
            if client_info['vc'] and user_voice_channel != client_info['vc'].channel:
                # BOTを新しいボイスチャンネルに移動
                await client_info['vc'].move_to(user_voice_channel)
                message = 'BOTが移動しました！このスレッドのメッセージを読み上げます！'
            else:
                message = 'BOTは既に参加しています！このスレッドのメッセージを読み上げます！'
            # 新しいテキストチャンネルIDを更新
            voice_clients[guild_id]['text_channel_id'] = interaction.channel_id
        else:
            if user_voice_channel:
                # 新しいボイスチャンネルにBOTを参加させる
                vc = await user_voice_channel.connect()
                voice_clients[guild_id] = {'vc': vc, 'text_channel_id': interaction.channel_id}
                message = 'BOTが参加しました！このスレッドのメッセージを読み上げます！'
            else:
                message = 'あなたはボイスチャンネルにいません！'

        await interaction.response.send_message(message, ephemeral=False)

    @bot.tree.command(name='leave', description='Voice channelから退出します。')
    async def leave(interaction: discord.Interaction):
        client_info = voice_clients.get(interaction.guild.id)
        if client_info:
            await client_info['vc'].disconnect()
            del voice_clients[interaction.guild.id]
            await interaction.response.send_message('BOTが退出しました！')
        else:
            await interaction.response.send_message('BOTがボイスチャンネルにいません。', ephemeral=True)

    @bot.event
    async def on_message(message):
        # ギルド（サーバー）からのメッセージでなければ処理をスキップ
        if message.guild is None:
            return

        client_info = voice_clients.get(message.guild.id)
        if client_info and message.channel.id == client_info['text_channel_id']:
            # メッセージが送信されたテキストチャンネルが、ボイスチャンネルに参加した際のチャンネルと一致する場合のみ読み上げ
            await play_voice(message.content, client_info['vc'])

async def play_voice(text, voice_client):
    if voice_client and voice_client.channel:
        
        # サーバー絵文字を「絵文字」という文字で置き換える
        text = re.sub(r"<a?:[a-zA-Z0-9_]+:[0-9]+>", "絵文字", text)  # サーバー絵文字の置換
        # 一般的なUnicode絵文字を「絵文字」という単語に置き換える
        text = emoji.replace_emoji(text,replace='絵文字')

        # メンションをユーザー名に置換
        mentions = re.findall(r'<@!?(\d+)>', text)
        for user_id in mentions:
            user = await voice_client.guild.fetch_member(int(user_id))
            text = text.replace(f'<@{user_id}>', user.display_name).replace(f'<@!{user_id}>', user.display_name)

        # URLを置換
        text = re.sub(r'https?://\S+', 'URL', text)
        # スポイラーを置換
        text = re.sub(r'\|\|(.*?)\|\|', 'ネタバレ', text)
        # 強調を置換
        text = text.replace('*', '').replace('_', '')

        # 文字数のチェック
        if len(text) > 1000:
            print("メッセージが1000文字を超えているため、読み上げません。")
            return

        # テキストから音声データとサンプリングレートを取得
        wave, sr = pyopenjtalk.tts(text)
        # 音声データの振幅を正規化
        wave_norm = wave / np.max(np.abs(wave))
        # 正規化した音声データをバイト配列に変換
        sound = np.int16(wave_norm * 32767).tobytes()

        # 正規化された音声データをpydub.AudioSegmentオブジェクトに変換
        # サンプリングレート(sr)をpyopenjtalk.ttsから取得した値に設定
        audio = pydub.AudioSegment(sound, sample_width=2, frame_rate=sr, channels=1)

        # 一時ファイルにMP3として保存
        fd, tmpfile_path = tempfile.mkstemp(suffix='.mp3')
        try:
            with os.fdopen(fd, 'wb') as tmpfile:
                audio.export(tmpfile, format="mp3")
            if voice_client.is_connected():
                # 再生が終了したら一時ファイルを削除するコールバック関数
                def after_playing(error):
                    os.remove(tmpfile_path)
                # 音声を再生
                voice_client.play(FFmpegPCMAudio(tmpfile_path), after=after_playing)
            else:
                # ボイスクライアントがボイスチャンネルに接続されていない場合のエラーメッセージ
                print("ボイスクライアントが一時的にボイスチャンネルに接続されていないようです。")
        except Exception as e:
            # エラーが発生した場合、一時ファイルを削除してエラーメッセージをログに記録
            os.remove(tmpfile_path)
            print(f"エラーが発生しました: {e}")
    else:
        # ボイスクライアントまたはチャンネルがNoneの場合のエラーメッセージ
        print("ボイスクライアントまたはチャンネルが存在しません。")

