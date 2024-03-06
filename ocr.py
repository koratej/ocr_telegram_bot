import requests
import json
import telebot

# Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your Telegram bot token
bot = telebot.TeleBot('YOUR_TELEGRAM_BOT_TOKEN')

@bot.message_handler(content_types=['photo', 'text'])
def handle_message(message):
    if message.content_type == 'photo':
        # Get the file ID of the image
        file_id = message.photo[-1].file_id
        # Download the image using the file ID
        file_info = bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
        image_file = requests.get(file_url)
        
        # URL for OCR API
        url = "http://bhasha.iiit.ac.in/pageocr/api"

        # Language specified by the user in the text
        language = None
        
        # Check if the text message contains a language specification
        if message.caption:
            # Extract language from the caption text
            language = message.caption.lower().strip()
            print("Language specified in caption:", language)

        # Set default payload
        payload = {
            'version': 'v4_robust',
            'modality': 'printed',
            'layout_model': 'v2_doctr'
        }
        
        # Update payload language if specified by the user
        if language:
            payload['language'] = language

        # Files to be sent to OCR API
        files = {'image': image_file.content}

        # Request OCR API
        resp = requests.post(url, data=payload, files=files)

        if resp.status_code == 200:
            # Parse JSON response
            response_json = resp.json()

            # Extract only the "text" field
            extracted_text = response_json.get('text', '')

            # Send the extracted text back to the user
            bot.reply_to(message, extracted_text)

        else:
            bot.reply_to(message, "Error occurred during OCR. Please try again later.")

bot.polling()
