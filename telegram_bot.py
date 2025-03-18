import os
import base64
import logging
from google import genai
from google.genai import types
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from dotenv import load_dotenv
from io import BytesIO

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize the Gemma client
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    logger.error("GEMINI_API_KEY environment variable is missing")
    raise ValueError("GEMINI_API_KEY environment variable is missing")

logger.info("Initializing Gemma client")
client = genai.Client(api_key=api_key)
logger.info("Gemma client initialized successfully")

async def start(update: Update, context: CallbackContext) -> None:
    logger.info("Received /start command")
    await update.message.reply_text('Envie-me uma foto e um texto para processar!')

async def handle_all_messages(update: Update, context: CallbackContext) -> None:
    logger.info("Received a message")
    if update.message.photo and update.message.caption:
        logger.info("Message contains photo and caption")
        try:
            photo_file = await update.message.photo[-1].get_file()
            photo_path = await photo_file.download_to_drive()
            text = update.message.caption

            logger.info(f"Downloaded image to: {photo_path}")
            logger.info("Uploading image to Gemini...")
            uploaded_file = client.files.upload(file=photo_path)
            logger.info(f"Image uploaded successfully with URI: {uploaded_file.uri}")

            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_uri(
                            file_uri=uploaded_file.uri,
                            mime_type=uploaded_file.mime_type,
                        ),
                        types.Part.from_text(text=f"Process this image and text in Portuguese: {text}"),
                    ],
                ),
            ]
            
            generate_content_config = types.GenerateContentConfig(
                temperature=1,
                top_p=0.95,
                top_k=40,
                max_output_tokens=8192,
                response_mime_type="text/plain",
            )

            logger.info("Sending request to Gemini...")
            response_text = ""
            for chunk in client.models.generate_content_stream(
                model="gemini-2.0-flash",
                contents=contents,
                config=generate_content_config,
            ):
                if chunk and chunk.text:
                    response_text += chunk.text
            logger.info("Response processed successfully")

            # Clean up the downloaded file
            if os.path.exists(photo_path):
                os.remove(photo_path)
                logger.info(f"Cleaned up temporary file: {photo_path}")

            # Send the response back to the user
            await update.message.reply_text("📸 Informações processadas:")
            await update.message.reply_text(response_text)
            await update.message.reply_text("Envie mais fotos e textos! 😊")
            
        except Exception as e:
            logger.error(f"Error processing image and text: {e}")
            logger.error(f"Exception type: {type(e)}")
            logger.error(f"Exception details: {str(e)}")
            await update.message.reply_text("Desculpe, ocorreu um erro ao processar a imagem e o texto. 😞")

    elif update.message.text:
        logger.info("Message contains text only")
        logger.info("Sending text to Gemma for processing")
        # Process the text with Gemma
        try:
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=f"Process this text in Portuguese: {update.message.text}"),
                    ],
                ),
            ]
            generate_content_config = types.GenerateContentConfig(
                temperature=1,
                top_p=0.95,
                top_k=64,
                max_output_tokens=8192,
                response_mime_type="text/plain",
            )
            response_text = ""
            for chunk in client.models.generate_content_stream(
                model="gemini-2.0-flash",
                contents=contents,
                config=generate_content_config,
            ):
                if chunk and chunk.text:
                    response_text += chunk.text
            logger.info("Received response from Gemma")

            # Send the response back to the user
            await update.message.reply_text("📝 Texto processado:")
            await update.message.reply_text(response_text)
            await update.message.reply_text("Envie mais textos! 😊")
        except Exception as e:
            logger.error(f"Error processing text: {e}")
            await update.message.reply_text("Desculpe, ocorreu um erro ao processar o texto. 😞")
    else:
        logger.info("Message does not contain text or photo with caption")
        await update.message.reply_text("Envie uma foto com texto ou apenas um texto. 📸📝")

async def stop(update: Update, context: CallbackContext) -> None:
    """Stops the bot."""
    logger.info("Received /stop command")
    await update.message.reply_text('Bot parando...')
    context.application.stop()

def main() -> None:
    logger.info("Starting bot")
    application = Application.builder().token(os.environ.get("TELEGRAM_BOT_TOKEN")).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(MessageHandler(filters.ALL, handle_all_messages))

    application.run_polling()

if __name__ == '__main__':
    main()
