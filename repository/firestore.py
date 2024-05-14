import firebase_admin
from firebase_admin import firestore, credentials
from firebase_admin.firestore import firestore as fs

from shared.globals.objects import FIREBASE_CREDS

firebase_admin.initialize_app(credentials.Certificate(FIREBASE_CREDS))

db: fs.Client = firestore.client()
