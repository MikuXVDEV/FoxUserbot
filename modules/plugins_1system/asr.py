import io
import requests

from pydub import AudioSegment
from pyrogram.types import Message
from pyrogram import Client, filters

from prefix import my_prefix
from configurator import my_proxy, my_url_asr
from requirements_installer import install_library
from modules.plugins_1system.settings.main_settings import module_list, file_list


install_library('pydub')

class ASR:
    def __init__(self, audio_bytes):
        self.audio_bytes = audio_bytes

    async def recognition(self) -> dict:
        audio = AudioSegment.from_file(self.audio_bytes, format="ogg")
        wav_bytes = io.BytesIO()
        audio.export(wav_bytes, format="wav")
        wav_bytes.seek(0)

        files = {'audio_file': wav_bytes.getvalue()}
        response = requests.post(
            url=my_url_asr(),
            files=files,
            proxies={'http': my_proxy()}
        )
        response.raise_for_status()

        result = response.json()
        print(f'result: {result} {response}')
        return result


@Client.on_message(filters.command("asr", prefixes=my_prefix()) & filters.reply & filters.me)
async def recognition(client: Client, message: Message) -> None:
    reply = message.reply_to_message

    if not reply or not reply.voice:
        await message.edit("❌ Ответь на голосовое сообщение.")
        return

    await message.edit("🔄 Транскрибирую аудио...")

    from tempfile import NamedTemporaryFile
    import io

    with NamedTemporaryFile(suffix=".ogg") as tmp_file:
        await client.download_media(reply.voice, file_name=tmp_file.name)

        with open(tmp_file.name, "rb") as f:
            voice_bytes = io.BytesIO(f.read())

    voice_bytes.seek(0)

    asr = ASR(voice_bytes)
    try:
        result = await asr.recognition()
        text = result.get("text", "❌ Не удалось распознать речь.")
    except Exception as e:
        text = f"⚠️ Ошибка распознавания: {e}"

    await message.edit(f"📝 Результат:\n<blockquote>{text}</blockquote>")


module_list['ASR'] = f'{my_prefix()}ASR'
file_list['ASR'] = 'asr.py'
