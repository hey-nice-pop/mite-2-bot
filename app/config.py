from dotenv import load_dotenv
load_dotenv()

import os

BOT_TOKEN = os.getenv('BOT_TOKEN')#bottoken
DELEATED_LOG_CHANNEL_ID = os.getenv('DELEATED_LOG_CHANNEL_ID')
REPORT_LOG_CHANNEL_ID = os.getenv('REPORT_LOG_CHANNEL_ID')
REPORT_REACTION_NAME = os.getenv('REPORT_REACTION_NAME')