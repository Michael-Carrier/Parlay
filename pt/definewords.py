import spacy

# 1. Load the Portuguese model
# Make sure to run: python -m spacy download pt_core_news_sm
try:
    nlp = spacy.load("pt_core_news_sm")
except:
    print("Error: Please run 'python -m spacy download pt_core_news_sm' first.")
    exit()

# 2. Define your input and output files
input_file = r"C:\Users\michael\Documents\Parlay\pt\words.txt"
output_file = "categorized_vocab.txt"

def get_category(word):
    doc = nlp(word)
    # Return the POS tag of the primary word
    if len(doc) > 0:
        return doc[0].pos_
    return "UNKNOWN"

processed_data = []

# 3. Read and Parse
with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        original_line = line.strip()
        if not original_line:
            continue
            
        # Handle the "word / word" format from your list
        # We analyze the first word to get the category
        base_word = original_line.split('/')[0].strip()
        category = get_category(base_word)
        
        processed_data.append(f"{original_line}\t{category}")

# 4. Export to TXT
with open(output_file, "w", encoding="utf-8") as f:
    f.write("Word/Phrase\tCategory\n") # Header
    f.writelines("\n".join(processed_data))

print(f"Done! {len(processed_data)} items exported to {output_file}")