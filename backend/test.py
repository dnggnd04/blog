from dotenv import load_dotenv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(os.path.join(BASE_DIR, 'app\.env'))
load_dotenv(os.path.join(BASE_DIR, 'app\.env'))

print(os.getenv("DATABASE_URL"))
