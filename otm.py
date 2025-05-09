# meta developer: @YourTelegramUsername
# scope: hikka_only
# scope: hikka_min 1.6.0

from telethon import events, types
from telethon.tl.types import Message, DocumentAttributeSticker
from .. import loader, utils
from PIL import Image, ImageDraw, ImageFont
import io
import logging
import textwrap

logger = logging.getLogger(__name__)

@loader.tds
class CustomStickerMod(loader.Module):
    """Create custom stickers with text"""

    strings = {
        "name": "CustomSticker",
        "where_text": "<emoji document_id='6041914500272098262'>🚫</emoji> <b>Please provide text for the sticker</b>",
        "processing": "<emoji document_id='6318766236746384900'>⚙️</emoji> <b>Creating sticker...</b>",
        "error": "<emoji document_id='6041914500272098262'>🚫</emoji> <b>Error: {}</b>",
    }

    strings_ru = {
        "where_text": "<emoji document_id='6041914500272098262'>🚫</emoji> <b>Укажите текст для стикера</b>",
        "processing": "<emoji document_id='6318766236746384900'>⚙️</emoji> <b>Создаю стикер...</b>",
        "error": "<emoji document_id='6041914500272098262'>🚫</emoji> <b>Ошибка: {}</b>",
    }

    async def stickercmd(self, message: Message):
        """<text> - Create a sticker with custom text"""
        text = utils.get_args_raw(message)
        reply = await message.get_reply_message()

        if not text and reply:
            text = reply.text
        if not text:
            await message.edit(self.strings("where_text"))
            return

        await message.edit(self.strings("processing"))

        try:
            sticker = await self.create_sticker(text)
            # Отправляем как документ с атрибутами стикера
            await message.respond(
                file=sticker,
                force_document=True,
                attributes=[DocumentAttributeSticker("", None)]
            )
            logger.info("Sticker sent successfully")
        except Exception as e:
            await utils.answer(message, self.strings("error").format(str(e)))
            logger.error(f"Error creating sticker: {e}")
            return

        if message.out:
            await message.delete()

    async def create_sticker(self, text: str):
        width, height = 512, 512
        max_width = 450
        initial_font_size = 40

        # Создаём изображение с белым фоном
        img = Image.new('RGBA', (width, height), (255, 255, 255, 255))  # Белый фон
        draw = ImageDraw.Draw(img)

        # Пробуем загрузить шрифт
        try:
            font = ImageFont.truetype("arial.ttf", initial_font_size)
            logger.info("Loaded arial.ttf")
        except:
            font = ImageFont.load_default()
            logger.warning("Arial.ttf not found, using default font")

        # Обрезаем и переносим текст
        wrapped_text = textwrap.fill(text, width=30)
        text_bbox = draw.textbbox((0, 0), wrapped_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Автомасштабирование шрифта, если текст слишком большой
        font_size = initial_font_size
        while text_width > max_width and font_size > 20:
            font_size -= 2
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            text_bbox = draw.textbbox((0, 0), wrapped_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]

        # Центрируем текст
        x = (width - text_width) / 2
        y = (height - text_height) / 2

        # Рисуем текст чёрным цветом
        draw.text((x, y), wrapped_text, font=font, fill=(0, 0, 0, 255), align="center")
        logger.info(f"Text drawn: '{wrapped_text}', position: ({x}, {y}), size: ({text_width}, {text_height})")

        # Сохраняем изображение
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        logger.info(f"Image saved, size: {buffer.getbuffer().nbytes} bytes")

        return buffer
