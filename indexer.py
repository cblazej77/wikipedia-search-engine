import unittest
import apache_beam as beam
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
import hashlib
import json
import sqlite3

# Pomijane słowa
stopwords = ['i', 'oraz', 'w', 'na', 'ze', 'lub', 'the', 'and', 'of']

DATA_PATH = Path(__file__).parent / 'data'
OUTPUT_JSON = Path(__file__).parent / 'indexed_docs.json'

# Zapisywanie do bazy SQLite
def save_to_db(processed_docs, db_path='indexed_docs.db'):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            filename TEXT,
            tfidf TEXT
        )''')
    for doc_id, filename, tfidf in processed_docs:
        c.execute('INSERT OR REPLACE INTO documents VALUES (?, ?, ?)',
                  (doc_id, filename, json.dumps(tfidf)))
    conn.commit()
    conn.close()

# Tworzenie unikalnego ID na podstawie nazwy pliku
def split_file_content_with_id(kv):
    filename, content = kv
    file_id = hashlib.sha1(filename.encode()).hexdigest()
    return {'id': file_id, 'filename': filename, 'content': content}

# Główna metoda indeksująca
def main(data_path=DATA_PATH, output_json=OUTPUT_JSON):
    if data_path.is_dir():
        file_pattern = str(data_path / "*.txt")
    else:
        file_pattern = str(data_path)

    with beam.Pipeline() as pipeline:
        docs = (
            pipeline
            | beam.io.ReadFromTextWithFilename(str(file_pattern))              # odczyt plików wraz z ich nazwami
            | beam.Map(split_file_content_with_id)                          # przekształcenie w słownik
            | beam.Map(lambda x: json.dumps(x))                             # transfer na JSON do zapisu
            | beam.io.WriteToText(str(output_json), shard_name_template='') # zapis wyniku do pliku "indexed_docs.json"
                           )
    
    if not output_json.exists():
        return

    # Otwarcie JSON'a i ładowanie danych do listy słowników
    with open(output_json, 'r', encoding='utf-8') as f:
        docs = [json.loads(line) for line in f]
    
    # Osobne listy dla treści, ścieżek i ID plików
    contents = [d['content'] for d in docs]
    filenames = [d['filename'] for d in docs]
    ids = [d['id'] for d in docs]

    # Utworzenie TF-IDF
    vectorizer = TfidfVectorizer(stop_words=stopwords)
    tfidf_matrix = vectorizer.fit_transform(contents)
    feature_names = vectorizer.get_feature_names_out()

    processed_docs = []
    for idx, doc in enumerate(docs):
        row = tfidf_matrix[idx]

        # Słownik: {słowo: waga}
        tfidf_dict = {feature_names[col]: row[0, col] for col in row.nonzero()[1]}

        # Dodanie przetworzonego dokumentu do listy
        processed_docs.append((doc['id'], doc['filename'], tfidf_dict))

    save_to_db(processed_docs)
    print(f"Saved {len(processed_docs)} documents into database")

    # Wyświetlenie dokumentów z wektorami TF-IDF
    for doc_id, filename, tfidf in processed_docs:
        print(f"ID: {doc_id}\nFilename: {filename}\nTF-IDF: {tfidf}\n")

if __name__ == "__main__":
    main()
