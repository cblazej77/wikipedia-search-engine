import sqlite3
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

# Pomijane słowa
stopwords = ['i', 'oraz', 'w', 'na', 'ze', 'lub', 'the', 'and', 'of']

# Ładowanie dokumentów z bazy danych SQLite
def load_documents(db_path='indexed_docs.db'):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT id, filename, tfidf FROM documents")
    docs = c.fetchall()
    conn.close()
    return [(doc_id, filename, json.loads(tfidf_json)) for doc_id, filename, tfidf_json in docs]

# Podobieństwo cosinusowe 2 wektorów
def cosine_similarity(vec1, vec2):
    all_keys = set(vec1.keys()) | set(vec2.keys())
    v1 = np.array([vec1.get(k, 0.0) for k in all_keys])
    v2 = np.array([vec2.get(k, 0.0) for k in all_keys])

    # Jeśli wektor zerowy to p-stwo = 0
    if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0:
        return 0.0
    
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

# Główna metoda wyszukiwarki
def search(query):
    documents = load_documents()

    # Rozbicie zapytania na słowa z wykluczeniem stopwords
    query_tokens = [t for t in query.lower().split() if t not in stopwords]
    if not query_tokens:
        return []

    # Konwersja zapytania na wektor TF-IDF
    query_text = " ".join(query_tokens)
    doc_contents = [" ".join(d[2].keys()) for d in documents] 

    vectorizer = TfidfVectorizer(vocabulary=set(word for doc in documents for word in doc[2].keys()))
    vectorizer.fit(doc_contents)                        # uczenie modelu na podstawie słów w dokumencie
    query_vector = vectorizer.transform([query_text])   # konwersja zapytania na wektor TF-IDF
    feature_names = vectorizer.get_feature_names_out()
    query_dict = {feature_names[i]: query_vector[0, i] for i in range(len(feature_names)) if query_vector[0, i] > 0}

    # Porównanie wszystkich dokumentów z query_dict
    results = []
    for doc_id, filename, tfidf_dict in documents:
        sim = cosine_similarity(query_dict, tfidf_dict)
        results.append((doc_id, filename, sim))

    results.sort(key=lambda x: x[2], reverse=True)
    return results

if __name__ == "__main__":
    while True:
        query = input("Podaj zapytanie do wyszukania ('x' aby zakończyć):\n> ")
        if query == "x":
            break
        results = search(query)[:10]
        print(f"Results: '{query}'\n")
        for doc_id, filename, sim in results:
            print(f"ID: {doc_id}, Filename: {filename}, Similarity: {sim:.3f}")