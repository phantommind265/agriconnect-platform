import json
from flask import session

def t(key):
    lang = session.get("lang", "en")
    try:
        with open(f"agriplatform/utils/i18n/{lang}.json", encoding="utf-8") as f:
            data = json.load(f)
        return data.get(key, key)
    except:
        return key
        
