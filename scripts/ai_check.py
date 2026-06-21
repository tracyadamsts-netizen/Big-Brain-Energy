import ollama

# 1. Sondierung der verfügbaren Modelle
print("--- Sondierung der verfügbaren Modelle ---")
try:
    models = ollama.list()
    for model in models['models']:
        print(f"Modell gefunden: {model['name']}")
except Exception as e:
    print(f"Fehler bei Modell-Sondierung: {e}")

# 2. Test der Embedding-Qualität
print("\n--- Test der Embedding-Qualität ---")
try:
    # Hinweis: 'nomic-embed-text' muss in Ollama geladen sein (ollama pull nomic-embed-text)
    response = ollama.embeddings(model='nomic-embed-text', prompt='Das ist ein Test für die Embedding Qualität.')
    print(f"Embedding Länge: {len(response['embedding'])} Dimensionen")
    print("Erfolg: Embeddings werden korrekt erzeugt.")
except Exception as e:
    print(f"Fehler bei Embedding-Test: {e}")