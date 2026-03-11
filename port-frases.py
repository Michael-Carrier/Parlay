import spacy
import pandas as pd
import json
import os

# 1. LOAD SPACY PORTUGUESE
try:
    nlp = spacy.load("pt_core_news_sm")
except OSError:
    print("Error: Run 'python -m spacy download pt_core_news_sm' first.")
    exit()

# 2. LOAD YOUR BESCHERELLE DATABASE
# This allows us to know if 'vou' is 'ir' or 'estou' is 'estar'
verb_db_path = r'C:\Users\michael\Documents\Parlay\pt\verb_master_database.txt'
verb_df = pd.read_csv(verb_db_path, sep='\t')
# Create a dictionary for fast lookup: {conjugated_word: (infinitive, tense)}
verb_lookup = {row['Conjugated']: (row['Infinitive'], row['Tense']) for _, row in verb_df.iterrows()}

def analyze_pt_patterns(sentence):
    doc = nlp(sentence)
    text_lower = sentence.lower()
    found_matches = []
    
    # helper to check our custom DB
    def get_verb_info(word):
        return verb_lookup.get(word.lower(), (None, None))

    # --- PORTUGUESE CATEGORY RULES ---

    # 1. IMMEDIATE FUTURE (Ir + Infinitive)
    # Pattern: "Vou abrir", "Vamos comer"
    for i, t in enumerate(doc):
        infin, tense = get_verb_info(t.text)
        if infin == "ir" and i + 1 < len(doc):
            next_word = doc[i+1]
            next_infin, next_tense = get_verb_info(next_word.text)
            # If the next word is an infinitive (ends in ar/er/ir)
            if next_word.text.lower().endswith(('ar', 'er', 'ir')):
                found_matches.append({
                    "Category": "Immediate Future",
                    "Pattern": "ir + infinitive",
                    "Highlights": {"aux": [t.text], "main": [next_word.text]}
                })

    # 2. PRESENT CONTINUOUS (Estar + Gerund)
    # Pattern: "Estou falando", "Estamos comendo"
    for i, t in enumerate(doc):
        infin, tense = get_verb_info(t.text)
        if infin == "estar" and i + 1 < len(doc):
            next_word = doc[i+1]
            _, next_tense = get_verb_info(next_word.text)
            if next_tense == "Gerund":
                found_matches.append({
                    "Category": "Present Continuous",
                    "Pattern": "estar + gerund (-ando/-endo)",
                    "Highlights": {"aux": [t.text], "main": [next_word.text]}
                })

    # 3. MODAL VERBS (Poder/Querer/Dever + Infinitive)
    for i, t in enumerate(doc):
        infin, tense = get_verb_info(t.text)
        if infin in ["poder", "querer", "dever"] and i + 1 < len(doc):
            next_word = doc[i+1]
            if next_word.text.lower().endswith(('ar', 'er', 'ir')):
                found_matches.append({
                    "Category": "Modal",
                    "Pattern": f"{infin} + verb",
                    "Highlights": {"modal": [t.text], "verb": [next_word.text]}
                })

    # 4. PAST SIMPLE (Using your 'Past' tag)
    past_verbs = [t.text for t in doc if get_verb_info(t.text)[1] == "Past"]
    if past_verbs:
        found_matches.append({
            "Category": "Past Simple",
            "Pattern": "Subject + verb (past)",
            "Highlights": {"verbs": past_verbs}
        })

    # 5. TER (Possession)
    has_ter = [t.text for t in doc if get_verb_info(t.text)[0] == "ter"]
    if has_ter:
        found_matches.append({
            "Category": "Possession",
            "Pattern": "Ter + noun",
            "Highlights": {"verbs": has_ter}
        })

    # 6. QUESTIONS
    if sentence.strip().endswith("?"):
        found_matches.append({
            "Category": "Questions",
            "Pattern": "Question structure",
            "Highlights": {"special": ["?"]}
        })

    return found_matches

# --- LOAD DATA AND RUN ---
input_json = r'C:\Users\michael\Documents\Parlay\pt\your_book.json' # Update this name
with open(input_json, 'r', encoding='utf-8') as f:
    data = json.load(f)

final_results = []
for item in data:
    sentence = item["text"]
    matches = analyze_pt_patterns(sentence)
    for m in matches:
        final_results.append({
            "Category": m["Category"],
            "Sentence": sentence,
            "Pattern": m["Pattern"],
            "Highlights": json.dumps(m["Highlights"])
        })

df = pd.DataFrame(final_results)
df.to_csv('portuguese_structures.csv', index=False, encoding='utf-8-sig')
print("Finished! Structures exported to portuguese_structures.csv")