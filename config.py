import os
from dotenv import load_dotenv

load_dotenv()

# Flask
SECRET_KEY = os.getenv('SECRET_KEY', 'supersecretkey')
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

# Email
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_SUBJECT = os.getenv("EMAIL_SUBJECT", "TOPSIS Result")

# APIs
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")