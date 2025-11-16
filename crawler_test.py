import unittest
from unittest.mock import patch, mock_open, MagicMock
from crawler import crawl

class TestCrawler(unittest.TestCase):

    @patch("crawler.save_web_content")
    @patch("crawler.webdriver.Firefox")
    def test_crawl_single_iteration(self, mock_firefox, mock_save):
        driver = MagicMock()
        driver.title = "Tytuł"
        driver.page_source = """
            <div id="mw-content-text">
                <a href="/wiki/Test1">Link1</a>
                <a href="/wiki/Test2">Link2</a>
            </div>
        """
        mock_firefox.return_value = driver

        crawl("https://example.com")

        mock_save.assert_called()
        driver.get.assert_called()
        driver.quit.assert_called()

if __name__ == "__main__":
    unittest.main()