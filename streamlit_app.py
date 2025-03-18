import streamlit as st
import os
import logging
from google import genai
from google.genai import types
from telegram import Bot
from dotenv import load_dotenv
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import av

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
    st.error("GEMINI_API_KEY environment variable is missing")
    st.stop()

logger.info("Initializing Gemma client")
client = genai.Client(api_key=api_key)
logger.info("Gemma client initialized successfully")

st.title("📸 Telegram Bot Interface")
st.write("Envie-me uma foto, vídeo ou um texto para processar! 😊")

uploaded_file = st.file_uploader("Escolha uma imagem ou vídeo...", type=["jpg", "jpeg", "png", "mp4", "mov"])
text_input = st.text_area("Digite o texto aqui...")

class VideoProcessor(VideoTransformerBase):
    def __init__(self):
        self.client = client

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        # Convert the frame to a format suitable for the API
        img_bytes = av.VideoFrame.from_ndarray(img, format="bgr24").to_image().tobytes()
        # Upload the frame to the API
        uploaded_file = self.client.files.upload(file=img_bytes, mime_type="image/jpeg")
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_uri(
                        file_uri=uploaded_file.uri,
                        mime_type=uploaded_file.mime_type,
                    ),
                    types.Part.from_text(text="Describe this image in Portuguese."),
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
        response_text = ""
        for chunk in self.client.models.generate_content_stream(
            model="gemini-2.0-flash",
            contents=contents,
            config=generate_content_config,
        ):
            if chunk and chunk.text:
                response_text += chunk.text
        return response_text

st.write("Ou use a câmera para enviar um vídeo em tempo real:")

# Improved UI for live video
webrtc_ctx = webrtc_streamer(
    key="example",
    video_processor_factory=VideoProcessor,
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    media_stream_constraints={"video": True, "audio": False},
    async_processing=True,
)

if webrtc_ctx.video_processor:
    st.write("📹 Processando vídeo ao vivo...")
    description = webrtc_ctx.video_processor.transform(webrtc_ctx.video_frame)
    st.write("Descrição: ", description)

if st.button("Processar"):
    if uploaded_file:
        try:
            # Save the uploaded file
            file_path = os.path.join("temp", uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            logger.info(f"Downloaded file to: {file_path}")
            logger.info("Uploading file to Gemini...")
            uploaded_file = client.files.upload(file=file_path)
            logger.info(f"File uploaded successfully with URI: {uploaded_file.uri}")

            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_uri(
                            file_uri=uploaded_file.uri,
                            mime_type=uploaded_file.mime_type,
                        ),
                        types.Part.from_text(text=f"Process this file and text in Portuguese: {text_input}"),
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
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")

            # Display the response
            st.write("📸 Informações processadas:")
            st.write(response_text)
            st.write("Envie mais arquivos e textos! 😊")
            
        except Exception as e:
            logger.error(f"Error processing file and text: {e}")
            st.error("Desculpe, ocorreu um erro ao processar o arquivo e o texto. 😞")
    else:
        st.warning("Por favor, envie um arquivo.")
