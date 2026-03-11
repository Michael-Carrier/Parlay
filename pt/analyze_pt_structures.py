import spacy
import pandas as pd
import json
import os
import re

# -------------------------------------------------------
# SETUP PATHS
# -------------------------------------------------------
base_path = r"C:\Users\michael\Documents\Parlay\pt"
verb_db_path = os.path.join(base_path, "verb_master_database.txt")
input_json = os.path.join(base_path, "bluey_pt.json")
output_csv = os.path.join(base_path, "bluey_pt_structures.csv")

# -------------------------------------------------------
# LOAD DATA
# -------------------------------------------------------
nlp = spacy.load("pt_core_news_sm")

verb_df = pd.read_csv(verb_db_path, sep='\t')
verb_lookup = {row['Conjugated'].lower(): row for _, row in verb_df.iterrows()}

# -------------------------------------------------------
# HELPERS
# -------------------------------------------------------
QUESTION_WORDS = {'quem', 'que', 'o que', 'qual', 'quando', 'onde', 'como', 'quanto', 'quantos', 'quantas', 'por que', 'por quê'}
PREPOSITIONS   = {'em', 'de', 'para', 'com', 'a', 'até', 'por', 'sobre', 'entre', 'sem', 'após', 'antes', 'no', 'na', 'nos', 'nas', 'do', 'da', 'dos', 'das', 'ao', 'à', 'num', 'numa'}
CONNECTORS     = {'e', 'mas', 'porque', 'porém', 'então', 'ou', 'nem', 'contudo', 'todavia', 'entretanto'}
POSSESSIVES    = {'meu', 'minha', 'meus', 'minhas', 'seu', 'sua', 'seus', 'suas', 'nosso', 'nossa', 'nossos', 'nossas', 'teu', 'tua', 'teus', 'tuas', 'dele', 'dela', 'deles', 'delas'}
PRONOUNS       = {'eu', 'tu', 'ele', 'ela', 'nós', 'vós', 'eles', 'elas', 'você', 'vocês', 'a gente'}
MODALS         = {'poder', 'querer', 'dever', 'precisar', 'conseguir', 'saber'}
SER_ESTAR      = {'sou', 'és', 'é', 'somos', 'são', 'estou', 'estás', 'está', 'estamos', 'estão', 'era', 'estava', 'fui', 'foi', 'fomos', 'foram'}
DIRECTION_WORDS= {'esquerda', 'direita', 'frente', 'trás', 'cima', 'baixo', 'frente', 'atrás', 'reto', 'recto', 'vire', 'siga', 'vira', 'segue'}
COMPARATIVES   = {'mais', 'menos', 'maior', 'menor', 'melhor', 'pior', 'maior', 'menor', 'mais alto', 'mais baixo', 'o mais', 'a mais', 'os mais', 'as mais'}
NUMBERS        = set('zero um uma dois duas três quatro cinco seis sete oito nove dez onze doze treze catorze quinze dezesseis dezessete dezoito dezenove vinte trinta quarenta cinquenta sessenta setenta oitenta noventa cem mil'.split())
PERSONAL_VERBS = {'chamo', 'chamas', 'chama', 'moro', 'moras', 'mora', 'trabalho', 'trabalhas', 'trabalha', 'tenho', 'tens', 'tem', 'sou', 'és', 'é'}

def get_verb_info(word):
    return verb_lookup.get(word.lower())

def tokens(text):
    return [t.lower() for t in text.split()]

def has_token(toks, word):
    return word in toks

def any_token(toks, word_set):
    return any(t in word_set for t in toks)

def is_question(text):
    return text.strip().endswith('?') or tokens(text)[0] in QUESTION_WORDS if tokens(text) else False

# -------------------------------------------------------
# PATTERN ANALYSIS
# -------------------------------------------------------
def analyze_patterns(text):
    toks = tokens(text)
    doc = nlp(text)
    matches = []

    # Helper to add match
    def add(category, pattern, highlights=None):
        matches.append({
            "Category": category,
            "Pattern": pattern,
            "Highlights": highlights or {}
        })

    # --- Subject + verb (present) ---
    for t in doc:
        info = get_verb_info(t.text)
        if info is not None and str(info.get('Tense')) == 'Present':
            add("Present simple", "Subject + verb (present)", {"verbs": [t.text]})
            break

    # --- Pronouns + verb (past) ---
    for t in doc:
        info = get_verb_info(t.text)
        if info is not None and str(info.get('Tense')) == 'Past':
            add("Past simple", "Pronouns + verb (past)", {"verbs": [t.text]})
            break

    # --- Subject + to be (ser/estar) ---
    if any_token(toks, SER_ESTAR):
        matched = [t for t in toks if t in SER_ESTAR]
        add("To be (ser/estar)", "Subject + ser/estar + noun/adjective", {"special": matched})

    # --- be + verb-ing (gerund) ---
    for t in doc:
        info = get_verb_info(t.text)
        if info is not None and str(info.get('Tense')) == 'Gerund':
            # Check if preceded by estar
            prev_toks = toks[:toks.index(t.text.lower())] if t.text.lower() in toks else []
            if any(p in SER_ESTAR for p in prev_toks):
                add("Present continuous", "estar + verb-ing", {"verbs": [t.text]})
            else:
                add("Gerund", "be + verb-ing", {"verbs": [t.text]})
            break

    # --- ir + infinitive (immediate future) ---
    ir_forms = {'vou', 'vais', 'vai', 'vamos', 'vão'}
    for i, t in enumerate(doc):
        if t.text.lower() in ir_forms and i + 1 < len(doc):
            next_info = get_verb_info(doc[i+1].text)
            if next_info is not None and doc[i+1].text.lower().endswith(('ar', 'er', 'ir')):
                add("Immediate future", "ir + infinitive", {"special": [t.text, doc[i+1].text]})
                break

    # --- Modals (poder/querer/dever + verb) ---
    for i, t in enumerate(doc):
        info = get_verb_info(t.text)
        if info is not None and str(info.get('Infinitive')) in MODALS:
            if i + 1 < len(doc) and doc[i+1].text.lower().endswith(('ar', 'er', 'ir')):
                add("Modal verbs", f"pronouns + {info['Infinitive']} + verb", {"special": [t.text]})
                break

    # --- Negation (não + verb) ---
    for i, t in enumerate(doc):
        if t.text.lower() == 'não' and i + 1 < len(doc):
            next_info = get_verb_info(doc[i+1].text)
            if next_info is not None:
                add("Negation", "não + verb", {"special": ["não", doc[i+1].text]})
                break

    # --- Questions ---
    if is_question(text):
        q_words = [t for t in toks if t in QUESTION_WORDS]
        add("Questions", "Question word + aux + subject + verb", {"special": q_words or ["?"]})

    # --- Possessives ---
    poss_found = [t for t in toks if t in POSSESSIVES]
    if poss_found:
        add("Possessives", "possessive + noun", {"special": poss_found})

    # --- Prepositions ---
    prep_found = [t for t in toks if t in PREPOSITIONS]
    if prep_found:
        add("Prepositions", "noun + preposition + noun", {"special": prep_found})

    # --- Connectors (clause + and/but/because + clause) ---
    conn_found = [t for t in toks if t in CONNECTORS]
    if conn_found:
        add("Connecting words", "clause + and/but/because + clause", {"special": conn_found})

    # --- Numbers ---
    num_found = [t for t in toks if t in NUMBERS or t.isdigit()]
    if num_found:
        add("Numbers", "noun + verb + number + noun", {"special": num_found})

    # --- Directions ---
    dir_found = [t for t in toks if t in DIRECTION_WORDS]
    if dir_found:
        add("Directions", "verb + direction", {"special": dir_found})

    # --- Comparatives ---
    comp_found = [t for t in toks if t in COMPARATIVES]
    if comp_found:
        # Check for 'do que' / 'que' after comparative
        if 'que' in toks or 'do' in toks:
            add("Comparatives", "adjective + mais/menos + que", {"special": comp_found})

    # --- há / existe (there is/there are) ---
    if any(t in {'há', 'existe', 'existem', 'tem', 'têm'} for t in toks):
        matched = [t for t in toks if t in {'há', 'existe', 'existem'}]
        if matched:
            add("There is/There are", "há/existe + noun", {"special": matched})

    # --- Personal information (I + verb + personal detail) ---
    if toks and toks[0] in {'eu', 'me', 'meu', 'minha'} or any(t in PERSONAL_VERBS for t in toks[:3]):
        personal = [t for t in toks if t in PERSONAL_VERBS]
        if personal:
            add("Personal information", "I + verb + personal detail", {"special": personal})

    # --- Subject + adverb + verb ---
    adverbs = {'sempre', 'nunca', 'às vezes', 'frequentemente', 'raramente', 'já', 'ainda', 'também', 'só', 'apenas'}
    adv_found = [t for t in toks if t in adverbs]
    if adv_found:
        add("Adverbs of frequency", "Subject + adverb + verb", {"special": adv_found})

    return matches

# -------------------------------------------------------
# EXECUTE
# -------------------------------------------------------
with open(input_json, 'r', encoding='utf-8') as f:
    data = json.load(f)

results = []
for item in data:
    sentence = item["text"]
    found = analyze_patterns(sentence)
    for m in found:
        results.append({
            "Category": m["Category"],
            "Sentence": sentence,
            "Pattern": m["Pattern"],
            "Highlights": json.dumps(m["Highlights"], ensure_ascii=False)
        })

df = pd.DataFrame(results)
df = df.drop_duplicates(subset=['Category', 'Sentence'])
df.to_csv(output_csv, index=False, encoding='utf-8-sig')
print(f"Done! Found {len(df)} pattern matches across {df['Category'].nunique()} categories.")
print(df['Category'].value_counts().to_string())
