import unittest
import hashlib
import json
from pathlib import Path
from unittest.mock import patch, mock_open

from indexer import split_file_content_with_id, main, stopwords 

class TestIndexer(unittest.TestCase):

    # Test nadawania unikalnego ID dla dokumentu
    def test_split_file_content_with_id(self):
        input_kv = ("example.txt", "rehabilitacja pacjent ćwiczenia")
        result = split_file_content_with_id(input_kv)
        
        expected_id = hashlib.sha1("example.txt".encode()).hexdigest()
        self.assertEqual(result['id'], expected_id)
        self.assertEqual(result['filename'], "example.txt")
        self.assertEqual(result['content'], "rehabilitacja pacjent ćwiczenia")
        self.assertIsInstance(result, dict)

    # Test głównej funkcji
    # Testowanie czy pliki są wczytywane i czy przetwarzanie zwraca listę dokumentów
    @patch("builtins.open", new_callable=mock_open, read_data='{"id":"abc","filename":"file.txt","content":"rehabilitacja"}\n')
    @patch("apache_beam.Pipeline")  
    def test_main_pipeline(self, mock_pipeline, mock_file):
        try:
            main()
        except Exception as e:
            self.fail(f"main() raised Exception unexpectedly: {e}")

        mock_file.assert_called_with(Path(__file__).parent / "indexed_docs.json", 'r', encoding='utf-8')

if __name__ == "__main__":
    unittest.main()