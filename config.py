from os import environ, path
from dotenv import load_dotenv


basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))




TESTING = False
DEBUG = False
FLASK_ENV = 'production'

SECRET_KEY = environ.get('SECRET_KEY')

VICIDIAL_API_USER = environ.get('VICIDIAL_API_USER')
VICIDIAL_API_PASS = environ.get('VICIDIAL_API_PASS')
VICIDIAL_API_SOURCE = environ.get('VICIDIAL_API_SOURCE')
VICIDIAL_API_CAMPAIGN = environ.get('VICIDIAL_API_CAMPAIGN')
VICIDIAL_API_URL = environ.get('VICIDIAL_API_URL')

DROPCO_API_URL = environ.get('DROPCO_API_URL')

MYSQL_HOST = environ.get('MYSQL_HOST')
MYSQL_USER = environ.get('MYSQL_USER')
MYSQL_PASSWORD = environ.get('MYSQL_PASSWORD')
MYSQL_DB = environ.get('MYSQL_DB')

SIMPLETEXTING_URL = environ.get('SIMPLETEXTING_URL')
SIMPLETEXTING_TOKEN = environ.get('SIMPLETEXTING_TOKEN')

ALLOWED_EXTENSIONS = {'csv'}

UPLOAD_FOLDER = environ.get('UPLOAD_FOLDER')



DROPCO_API_DELIVERY_URL = environ.get('DROPCO_API_DELIVERY_URL')
DROPCO_API_KEY = environ.get('DROPCO_API_KEY')
DROPCO_VM_AUDIO_URL = environ.get('DROPCO_VM_AUDIO_URL')
DROPCO_XFER_PHONE = environ.get('DROPCO_XFER_PHONE')
DROPCO_TOKENS = {'AFTERNOON': environ.get('DROPCO_AFTERNOON_CAMP_TOKEN'), 'MORNING': environ.get('DROPCO_MORNING_CAMP_TOKEN')}

TEST_DROP_PHONE_LIST = environ.get('TEST_DROP_PHONES').split(",")

