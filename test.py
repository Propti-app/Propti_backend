import firebase_admin
from firebase_admin import credentials
cred = credentials.Certificate("/full/path/to/your/firebase_key.json")
firebase_admin.initialize_app(cred)
print("✅ Firebase initialized")
