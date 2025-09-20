import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))
APP_ENV = os.getenv('APP_ENV', 'local')

if APP_ENV == 'production':
    print("Running with production settings")
    from .production import *
else:
    print("Running with local settings")
    from .local import *
