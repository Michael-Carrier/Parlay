import pandas as pd
import os

# 1. SETUP PATHS
base_path = r"C:\Users\michael\Documents\Parlay\pt"
output_file = os.path.join(base_path, "verb_master_database.txt")

# 2. MASTER LIST
verbs_to_process = [
    "abrir", "acampar", "aceitar", "achar", "acordar", "agradecer", "aguardar", "ajudar", "alugar", 
    "amar", "andar", "apanhar", "apetecer", "aprender", "aquecer", "arrumar", "aspirar", "assar", 
    "assinar", "aterrar", "banhar", "bater", "beber", "brilhar", "buscar", "cair", "cantar", "casar", 
    "chamar", "chegar", "chover", "cobrir", "colher", "começar", "comer", "comportar", 
    "comprar", "congelar", "conhecer", "consertar", "continuar", "conversar", "correr", "cortar", 
    "cozer", "cozinhar", "crescer", "cumprimentar", "dançar", "dar", "deixar", "descansar", 
    "descartar", "descobrir", "descrever", "desejar", "desenhar", "detestar", "dever", "doer", 
    "dormir", "emprestar", "empurrar", "ensinar", "entrar", "enviar", "escolher", "escovar", 
    "escrever", "esgotar", "esperar", "esquecer", "estudar", "esvaziar", "evitar", "examinar", 
    "falar", "faltar", "fazer", "fechar", "ficar", "funcionar", "ganhar", "gastar", "gostar", 
    "grelhar", "gritar", "ir", "jantar", "jogar", "lanchar", "lavar", "lembrar", "ler", "levar", 
    "ligar", "limpar", "mandar", "meter", "morar", "mostrar", "mudar", "nadar", "navegar", "nevar", 
    "oferecer", "olhar", "organizar", "ouvir", "pagar", "parar", "partilhar", "partir", "passar", 
    "pedir", "perceber", "perder", "perguntar", "pesar", "pescar", "pintar", "pôr", "poupar", 
    "praticar", "precisar", "preencher", "premir", "preparar", "procurar", "proibir", "puxar", 
    "querer", "receber", "remar", "repetir", "reservar", "responder", "rir", "saber", "sair", 
    "saltar", "secar", "servir", "soletrar", "sorrir", "subir", "telefonar", "tentar", "ter", 
    "tocar", "tomar", "trabalhar", "trancar", "tratar", "trazer", "treinar", "trocar", "usar", 
    "varrer", "ver", "viajar", "vir", "visitar", "viver", "voar", "voltar", "ser", "estar", "poder"
]

# 3. CONJUGATION ENGINE (Rules & Irregulars)
def conjugate_portuguese(verb):
    forms = []
    persons = ["1st", "2nd", "3rd", "1st", "2nd", "3rd"]
    numbers = ["Singular", "Singular", "Singular", "Plural", "Plural", "Plural"]
    
    # Irregular "Deep History" Data
    irregular_data = {
        "ser": {
            "Pres": ["sou", "és", "é", "somos", "sois", "são"],
            "Past": ["fui", "foste", "foi", "fomos", "fostes", "foram"],
            "Ger": "sendo"
        },
        "ir": {
            "Pres": ["vou", "vais", "vai", "vamos", "ides", "vão"],
            "Past": ["fui", "foste", "foi", "fomos", "fostes", "foram"],
            "Ger": "indo"
        },
        "ter": {
            "Pres": ["tenho", "tens", "tem", "temos", "tendes", "têm"],
            "Past": ["tive", "tiveste", "teve", "tivemos", "tivestes", "tiveram"],
            "Ger": "tendo"
        },
        "estar": {
            "Pres": ["estou", "estás", "está", "estamos", "estais", "estão"],
            "Past": ["estive", "estiveste", "esteve", "estivemos", "estivestes", "estiveram"],
            "Ger": "estando"
        },
        "poder": {
            "Pres": ["posso", "podes", "pode", "podemos", "podeis", "podem"],
            "Past": ["pude", "pudeste", "pôde", "pudemos", "pudestes", "puderam"],
            "Ger": "podendo"
        },
        "fazer": {
            "Pres": ["faço", "fazes", "faz", "fazemos", "fazeis", "fazem"],
            "Past": ["fiz", "fizeste", "fez", "fizemos", "fizestes", "fizeram"],
            "Ger": "fazendo"
        }
    }

    if verb in irregular_data:
        d = irregular_data[verb]
        for i in range(6):
            forms.append([d["Pres"][i], verb, "Present", persons[i], numbers[i]])
            forms.append([d["Past"][i], verb, "Past", persons[i], numbers[i]])
        forms.append([d["Ger"], verb, "Gerund", "N/A", "N/A"])
        return forms

    # Regular Logic
    stem = verb[:-2]
    end = verb[-2:]
    
    rules = {
        "ar": {
            "Pres": ["o", "as", "a", "amos", "ais", "am"],
            "Past": ["ei", "aste", "ou", "ámos", "astes", "aram"],
            "Ger": "ando"
        },
        "er": {
            "Pres": ["o", "es", "e", "emos", "eis", "em"],
            "Past": ["i", "este", "eu", "emos", "estes", "eram"],
            "Ger": "endo"
        },
        "ir": {
            "Pres": ["o", "es", "e", "imos", "is", "em"],
            "Past": ["i", "iste", "iu", "imos", "istes", "iram"],
            "Ger": "indo"
        }
    }

    if end in rules:
        r = rules[end]
        for i in range(6):
            forms.append([stem + r["Pres"][i], verb, "Present", persons[i], numbers[i]])
            forms.append([stem + r["Past"][i], verb, "Past", persons[i], numbers[i]])
        forms.append([stem + r["Ger"], verb, "Gerund", "N/A", "N/A"])
        
    return forms

# 4. PROCESS
all_results = []
for v in verbs_to_process:
    all_results.extend(conjugate_portuguese(v))

# 5. EXPORT
df = pd.DataFrame(all_results, columns=['Conjugated', 'Infinitive', 'Tense', 'Person', 'Number'])
df.to_csv(output_file, sep='\t', index=False, encoding='utf-8')
print(f"SUCCESS! {len(all_results)} forms exported to {output_file}")