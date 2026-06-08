from fastapi import FastAPI
from pydantic import BaseModel
import google.genai as genai   # ✅ ispravan import
from dotenv import load_dotenv
import os
import json
import re
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # dozvoli sve domene
    allow_credentials=True,
    allow_methods=["*"],       # uključuje OPTIONS
    allow_headers=["*"],
)

# ============================
# KONFIGURACIJA GEMINI API
# ============================

load_dotenv()
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")   # ✅ čita iz .env
client = genai.Client(api_key=GEMINI_API_KEY)

# =========================
# HEALTHCHECK
# =========================

@app.get("/health")
def health():
    return {"status": "healthy", "service": "gemini-service"}

@app.get("/gemini-health")
def gemini_health():
    return {"status": "healthy", "service": "gemini-service"}

# =========================
# REQUEST MODEL
# =========================

class NewsRequest(BaseModel):
    headline: str
    description: str = ""

# =========================
# GEMINI ANALIZA
# =========================

@app.post("/analyze")
def analyze_news(data: NewsRequest):
    try:
        headline = data.headline.strip()
        description = data.description.strip()

        if headline == "":
            return {"error": "Headline je prazan"}

        full_text = f"{headline}. {description}"

        prompt = f"""
        Analiziraj sljedeću vijest.

        Vijest:
        "{full_text}"

        Vrati ISKLJUČIVO valid JSON sa poljima:
        category, sentiment, key_people, impact, summary_hr
        """

        # ✅ Ispravan poziv prema Gemini SDK-u
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt]   # lista stringova, kao u Colabu
        )

        response_text = response.candidates[0].content.parts[0].text.strip()
        clean_text = re.sub(r'```json|```', '', response_text).strip()
        parsed = json.loads(clean_text)

        parsed["search_url"] = f"https://news.google.com/search?q={headline.replace(' ', '+')}"
        parsed["source"] = "Google News"

        return parsed

    except json.JSONDecodeError:
        return {"error": "Gemini nije vratio valid JSON"}
    except Exception as e:
        return {"error": str(e)}

from fastapi import Query

@app.post("/predict")
def predict_news(
    headline: str = Query(...),
    short_description: str = Query("")
):
    try:

        prompt = f"""
        Klasificiraj sljedeću vijest u jednu kategoriju.

        Naslov:
        {headline}

        Opis:
        {short_description}

        Vrati ISKLJUČIVO naziv kategorije.
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt]
        )

        category = response.candidates[0].content.parts[0].text.strip()

        return {
            "category": category
        }

    except Exception as e:
        return {
            "error": str(e)
        }
