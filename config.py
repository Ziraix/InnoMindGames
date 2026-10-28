import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / '.env')

BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise RuntimeError('BOT_TOKEN не задан в .env')


ADMINS_ID = {int(x) for x in os.getenv('ADMINS_ID', '').split(',') if x.strip()}
MAIN_GROUP_ID = int(os.getenv('MAIN_GROUP_ID'))
MAIN_THREAD_ID = int(os.getenv('THREAD_ID') or 0) or None
SUB_THREAD_ID = int(os.getenv('SUB_THREAD_ID') or 0) or None