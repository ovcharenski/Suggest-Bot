import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN', '8334964606:AAGw0r4NYXZ-fHFoj7MZOvcB0GIEdNeubiE')
ADMIN_CHAT_ID = [int(os.getenv('ADMIN_CHAT_ID', -1001953854909))]