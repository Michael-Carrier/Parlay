import spacy
import pandas as pd
import json
import os

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Error: Download the model: python -m spacy download en_core_web_sm")
    exit()

def analyze_custom_patterns(sentence):
    doc = nlp(sentence)
    text_lower = sentence.lower()
    found_matches = []

    # --- CATEGORY RULES WITH TARGETED HIGHLIGHTS ---

    # 1. AGE
    if "years old" in text_lower:
        # Find the number near 'years old'
        nums = [t.text for t in doc if t.pos_ == "NUM"]
        found_matches.append({
            "Category": "Age", 
            "Pattern": "Verb + number + years old",
            "Highlights": {"numbers": nums, "special": ["years", "old", "years old"]}
        })

    # 2. PRICES
    has_currency = any(c in text_lower for c in ["pound", "£", "dollar", "$", "euro"])
    if has_currency:
        nums = [t.text for t in doc if t.pos_ == "NUM"]
        found_matches.append({
            "Category": "Prices", 
            "Pattern": "Noun + verb + number + currency",
            "Highlights": {"numbers": nums, "special": ["pound", "£", "dollar", "$", "euro", "cost", "costs"]}
        })

    # 3. I'D LIKE
    if "would like" in text_lower or "i'd like" in text_lower:
        found_matches.append({
            "Category": "I'd like", 
            "Pattern": "Pronoun + would + like",
            "Highlights": {"verbs": ["like"], "special": ["would", "I'd", "id"]}
        })

    # 4. GOING TO
    if "going to" in text_lower:
        # Find the verb after 'going to'
        relevant_verbs = []
        for i, t in enumerate(doc):
            if t.text.lower() == "to" and i > 0 and doc[i-1].text.lower() == "going":
                if i+1 < len(doc) and doc[i+1].pos_ == "VERB":
                    relevant_verbs.append(doc[i+1].text)
        found_matches.append({
            "Category": "Going to", 
            "Pattern": "be + going + to + verb",
            "Highlights": {"verbs": relevant_verbs, "special": ["going", "to"]}
        })

    # 5. CAN/COULD
    modal_words = [t.text for t in doc if t.lemma_ in ["can", "could"]]
    if modal_words:
        relevant_verbs = []
        for t in doc:
            if t.head.text in modal_words and t.pos_ == "VERB":
                relevant_verbs.append(t.text)
        found_matches.append({
            "Category": "Can/Could", 
            "Pattern": "pronouns + can/could + verb",
            "Highlights": {"verbs": relevant_verbs, "special": modal_words}
        })

    # 6. VERB + ING (Preference)
    pref_verbs = ["like", "love", "hate", "enjoy"]
    for i, t in enumerate(doc):
        if t.lemma_ in pref_verbs and i+1 < len(doc) and doc[i+1].tag_ == "VBG":
            found_matches.append({
                "Category": "Verb + -ing", 
                "Pattern": f"{t.lemma_} + verb-ing",
                "Highlights": {"verbs": [t.text, doc[i+1].text]}
            })

    # 7. PAST SIMPLE
    if not found_matches: # Only if it's not a more specific pattern
        past_verbs = [t.text for t in doc if t.tag_ == "VBD"]
        if past_verbs:
            found_matches.append({
                "Category": "Past simple", 
                "Pattern": "Pronouns + verb (past)",
                "Highlights": {"verbs": past_verbs}
            })

    # 8. NUMBERS
    if not any(m["Category"] in ["Age", "Prices"] for m in found_matches):
        nums = [t.text for t in doc if t.pos_ == "NUM"]
        if nums:
            found_matches.append({
                "Category": "Numbers", 
                "Pattern": "Noun + verb + number + noun",
                "Highlights": {"numbers": nums}
            })

    # 9. THERE IS / THERE ARE
    if "there is" in text_lower or "there are" in text_lower or "there's" in text_lower:
        found_matches.append({
            "Category": "There is/There are",
            "Pattern": "There is/are + noun",
            "Highlights": {"special": ["there", "is", "are", "there's"]}
        })

    # 10. PRESENT SIMPLE
    if not found_matches:
        present_verbs = [t.text for t in doc if t.tag_ == "VBZ" or t.tag_ == "VBP"]
        if present_verbs:
            found_matches.append({
                "Category": "Present simple",
                "Pattern": "Subject + verb (present)",
                "Highlights": {"verbs": present_verbs}
            })

    # 11. PRESENT CONTINUOUS
    ing_verbs = [t.text for t in doc if t.tag_ == "VBG"]
    be_verbs = [t.text for t in doc if t.lemma_ == "be"]
    if ing_verbs and be_verbs:
        found_matches.append({
            "Category": "Present continuous",
            "Pattern": "be + verb-ing",
            "Highlights": {"verbs": ing_verbs, "special": be_verbs}
        })

    # 12. TO BE
    be_tokens = [t.text for t in doc if t.lemma_ == "be"]
    if be_tokens and not any(m["Category"] == "Present continuous" for m in found_matches):
        found_matches.append({
            "Category": "To be",
            "Pattern": "Subject + to be",
            "Highlights": {"special": be_tokens}
        })

    # 13. HAVE GOT
    if "have got" in text_lower or "has got" in text_lower or "'ve got" in text_lower:
        found_matches.append({
            "Category": "Have got",
            "Pattern": "have/has got + noun",
            "Highlights": {"special": ["have", "has", "got", "'ve"]}
        })

    # 14. IMPERATIVES
    if doc[0].tag_ == "VB" and doc[0].dep_ == "ROOT":
        found_matches.append({
            "Category": "Imperatives",
            "Pattern": "Verb + (object)",
            "Highlights": {"verbs": [doc[0].text]}
        })

    # 15. QUESTIONS
    if sentence.strip().endswith("?"):
        question_words = [t.text for t in doc if t.tag_ == "WDT" or t.tag_ == "WP" or t.tag_ == "WRB"]
        aux_verbs = [t.text for t in doc if t.dep_ == "aux"]
        found_matches.append({
            "Category": "Questions",
            "Pattern": "Question word + aux + subject + verb",
            "Highlights": {"special": question_words + aux_verbs}
        })

    # 16. CONNECTING WORDS
    connecting = [t.text for t in doc if t.text.lower() in ["and", "but", "because"]]
    if connecting:
        found_matches.append({
            "Category": "Connecting words",
            "Pattern": "clause + and/but/because + clause",
            "Highlights": {"special": connecting}
        })

    # 17. ADVERBS OF FREQUENCY
    freq_words = ["always", "sometimes", "never", "usually", "often", "rarely"]
    found_freq = [t.text for t in doc if t.text.lower() in freq_words]
    if found_freq:
        found_matches.append({
            "Category": "Adverbs of frequency",
            "Pattern": "Subject + adverb + verb",
            "Highlights": {"special": found_freq}
        })

    # 18. COMPARATIVES / SUPERLATIVES
    comp_tokens = [t.text for t in doc if t.tag_ == "JJR" or t.tag_ == "JJS"]
    than_tokens = [t.text for t in doc if t.text.lower() == "than"]
    if comp_tokens:
        found_matches.append({
            "Category": "Comparatives/Superlatives",
            "Pattern": "adjective + -er/est + than",
            "Highlights": {"special": comp_tokens + than_tokens}
        })

    # 19. PREPOSITIONS OF PLACE/TIME
    place_preps = ["in", "on", "at", "near", "behind", "next to", "opposite", "between"]
    found_preps = [t.text for t in doc if t.text.lower() in place_preps and t.dep_ == "prep"]
    if found_preps:
        found_matches.append({
            "Category": "Prepositions",
            "Pattern": "noun + preposition + noun",
            "Highlights": {"special": found_preps}
        })

    # 20. PERSONAL INFORMATION
    personal_triggers = ["my name is", "i am from", "i live in", "i work in", "i have"]
    if any(p in text_lower for p in personal_triggers):
        found_matches.append({
            "Category": "Personal information",
            "Pattern": "I + verb + personal detail",
            "Highlights": {"special": ["name", "from", "live", "work"]}
        })

    # 21. TELLING THE TIME
    time_triggers = ["o'clock", "quarter to", "quarter past", "half past", "a.m", "p.m"]
    if any(t in text_lower for t in time_triggers):
        nums = [t.text for t in doc if t.pos_ == "NUM"]
        found_matches.append({
            "Category": "Telling the time",
            "Pattern": "time expression",
            "Highlights": {"numbers": nums, "special": ["o'clock", "quarter", "half", "past", "to"]}
        })

    # 22. DIRECTIONS
    direction_words = ["left", "right", "straight", "ahead", "turn", "end", "corner"]
    found_dirs = [t.text for t in doc if t.text.lower() in direction_words]
    if found_dirs:
        found_matches.append({
            "Category": "Directions",
            "Pattern": "verb + direction",
            "Highlights": {"special": found_dirs}
        })

    # 23. POSSESSIVES
    possessive_tokens = [t.text for t in doc if t.tag_ == "PRP$" or t.dep_ == "poss"]
    if possessive_tokens:
        found_matches.append({
            "Category": "Possessives",
            "Pattern": "possessive + noun",
            "Highlights": {"special": possessive_tokens}
        })


    return found_matches

# --- LOAD AND PROCESS ---
with open(r'C:\Users\michael\Documents\Parlay\en\bluey1_en.json', 'r', encoding='utf-8') as f:
    alice_data = json.load(f)

structure_matches = []

for item in alice_data:
    sentence = item["text"]
    matches = analyze_custom_patterns(sentence)
    for m in matches:
        structure_matches.append({
            "Category": m["Category"],
            "Sentence": sentence,
            "Pattern": m["Pattern"],
            "Highlights": json.dumps(m["Highlights"])
        })

df_results = pd.DataFrame(structure_matches)
df_results.to_csv('blueen1.csv', index=False)