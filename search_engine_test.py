import unittest
import hashlib
import json
from pathlib import Path
from unittest.mock import patch, mock_open

from search_engine import cosine_similarity, search, stopwords 

class TestSearcher(unittest.TestCase):

    # Test podobieństwa cosinusowego
    def test_cosine_similarity(self):
        v1, v2, v3 = {'a':1,'b':1}, {'a':1,'b':1}, {'c':1}
        self.assertAlmostEqual(cosine_similarity(v1, v2), 1.0)
        self.assertAlmostEqual(cosine_similarity(v1, v3), 0.0)

    # Testowanie poprawnego wyszukiwania
    @patch("search_engine.load_documents")
    def test_search_basic(self, mock_load):
        mock_load.return_value = [
            ("id1","file1.txt",{'rehabilitacja':0.7}),
            ("id2","file2.txt",{'dieta':0.7})
        ]
        results = search("rehabilitacja")
        self.assertAlmostEqual(results[0][0], "id1")
        self.assertAlmostEqual(results[-1][2], 0.0)

if __name__ == "__main__":
    unittest.main()