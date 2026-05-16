"""
Project: TailorTalk AI Drive Agent
Author: Sumit Patel
Note: Java background se Python/FastAPI mein banaya gaya project.
"""

from fastapi import FastAPI
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os, requests, urllib3, json, re

# Local testing mein SSL error na aaye isliye warning off ki hai
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# API Keys aur Folder ID load ho rahi hai .env se
load_dotenv()
app = FastAPI()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
CONF = "credentials.json"
FOLDER_ID = "1qkx58doSeYrcLjHPDysJyVJ36PsSqqlt"

def get_drive_service():
    """
    Google Drive connection setup:
    Service account use kiya hai bina login ke Drive read karne ke liye.
    Added Request refresh to fix JWT Signature errors.
    """
    scope = ['https://www.googleapis.com/auth/drive.readonly']
    
    # Credentials load karna
    creds = service_account.Credentials.from_service_account_file(CONF, scopes=scope)
    
    # JWT Fix: Agar token expire ya invalid lage toh refresh check karo
    try:
        if not creds.valid:
            creds.refresh(Request())
    except Exception as e:
        # Agar refresh fail ho toh purane creds ke saath hi try karega
        print(f"Auth Hint: Token validation check bypass (Normal in first run). Error: {e}")

    return build('drive', 'v3', credentials=creds)

@app.get("/")
def home():
    return {"message": "Agent Server is Running"}

@app.get("/chat")
def chat_with_agent(user_query: str):
    """
    Main logic: User query ko Google Drive query mein convert karna.
    """
    URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    
    # Default values taaki code crash na ho
    query_lower = user_query.lower()
    drive_q = f"name contains '{user_query}'" 
    bot_msg = f"Searching for {user_query}..."

    # --- STEP 1: Quick Keyword Matching ---
    # Common queries ke liye direct filters takki results jaldi aayein.
    if "pdf" in query_lower:
        drive_q = "mimeType = 'application/pdf'"
        bot_msg = "Sure! Saari PDF files dhoond raha hoon."
        
    elif "image" in query_lower or "pic" in query_lower or "photo" in query_lower:
        drive_q = "mimeType contains 'image/'"
        bot_msg = "Mil gayi! Ye rahi aapki photos."
        
    elif "all" in query_lower or "sari" in query_lower or "everything" in query_lower:
        # Sari files dikhane ke liye trashed=false use kiya hai
        drive_q = "trashed = false"
        bot_msg = "Zaroor! Ye rahi aapki saari files."
    
    # --- STEP 2: Intelligent Search using Gemini ---
    # Agar simple keyword nahi hai, toh Gemini AI ka use karke query banayenge.
    else:
        try:
            # Gemini ko instruction de rahe hain JSON format ke liye
            instruction = "Convert this to JSON format: {\"drive_q\": \"query\", \"bot_msg\": \"message\"}. Query for: "
            payload = {"contents": [{"parts": [{"text": f"{instruction} {user_query}"}]}]}
            response = requests.post(URL, json=payload, verify=False, timeout=10)
            res_json = response.json()
            
            if 'candidates' in res_json:
                raw_text = res_json['candidates'][0]['content']['parts'][0]['text'].strip()
                # Regex se {} ke beech ka data nikal rahe hain
                clean_json = re.search(r'\{.*\}', raw_text, re.DOTALL).group()
                ai_data = json.loads(clean_json)
                
                drive_q = ai_data.get("drive_q", drive_q)
                bot_msg = ai_data.get("bot_msg", bot_msg)
        except:
            # Error handling: Agar AI response na de toh keyword search hi chalne do
            pass 

    # --- STEP 3: Fetching Files from Drive ---
    try:
        service = get_drive_service()
        # Drive API call with filters
        results = service.files().list(
            q=f"'{FOLDER_ID}' in parents and ({drive_q}) and trashed=false",
            fields="files(id, name, mimeType, webViewLink)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()
        
        return {
            "status": "success",
            "message": bot_msg,
            "files": results.get('files', []),
            "ai_logic": drive_q 
        }
    except Exception as e:
        # Error hone par message return karega
        return {"status": "error", "message": str(e), "files": []}
