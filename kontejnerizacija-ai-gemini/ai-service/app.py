from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pickle
import re
import spacy
from spacy.lang.en.stop_words import STOP_WORDS

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# load modeli
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

with open("vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

with open("label_encoder.pkl", "rb") as f:
    label_encoder = pickle.load(f)

# spacy
nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    doc = nlp(text)
    tokens = [
        token.lemma_ for token in doc
        if token.lemma_ not in STOP_WORDS
        and len(token.lemma_) > 2
    ]
    return " ".join(tokens)

@app.get("/")
def root():
    return {"message": "News Classifier API radi!", "student": "Mario Lucic"}

@app.get("/health")
def health():
    return {"status": "ok", "service": "news-classifier"}

@app.get("/ai-health")
def ai_health():
    return {"status": "ok", "service": "ai-service"}


@app.post("/predict")
def predict(headline: str, short_description: str):
    text_full = headline + " " + short_description
    processed = clean_text(text_full)
    X = vectorizer.transform([processed])
    pred = model.predict(X)[0]
    category = label_encoder.inverse_transform([pred])[0]
    return {"category": category}
