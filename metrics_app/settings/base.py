import os
import datetime

BASE_DIR = os.environ['SC_DIR']

CLIENT_SECRET = os.path.join(BASE_DIR, 'credentials/client_secrets.json')
STORAGE_FILE = os.path.join(BASE_DIR, 'credentials/sc_storage.dat')

SCOPE = 'https://www.googleapis.com/auth/webmasters.readonly'
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
CLIENT_URL = 'http://ee.co.uk/'

EXPORT_FOLDER = 'exports'
EXPORT_PATH = os.path.join(BASE_DIR, EXPORT_FOLDER)
if not os.path.exists(EXPORT_PATH):
    os.makedirs(EXPORT_PATH)

CSV_FILE = 'ee.co.uk_Search_Console_Data.csv'
CSV_PATH = os.path.join(EXPORT_PATH, CSV_FILE)

# dates should be in the format of YYYY-MM-DD
START_DATE = '2015-01-01'
END_DATE = datetime.date.today().strftime('%Y-%m-%d')

IGNORE = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c',
          'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
          'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '!',
          '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-',
          '.', '/', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']',
          '^', '_', '`', '{', '|', '}', '~', ' ', '\t', '\n', '\r',
          '\x0b', '\x0c']
