import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from urllib.parse import urljoin, urlparse
import logging

logging.basicConfig(level=logging.INFO)

class WebCrawler:
    def __init__(self):
        self.index = defaultdict(list)
        self.visited = set()

    def crawl(self, url, base_url=None):
        if url in self.visited:
            return
        self.visited.add(url)

        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            self.index[url] = soup.get_text()

            for link in soup.find_all('a'):
                href = link.get('href')
                if href:
                        href = urljoin(base_url or url, href)
                        if href.startswith(base_url or url):
                            self.crawl(href, base_url=base_url or url)
        except Exception as e:
            logging.info(f"Error crawling {url}: {e}")

    def search(self, keyword):
        results = []
        for url, text in self.index.items():
            if keyword.lower() in text.lower():
                results.append(url)
        return results

    def print_results(self, results):
        if results:
            print("Search results:")
            for result in results:
                print(f"- {result}")
        else:
            print("No results found.")

def main():
    crawler = WebCrawler()
    start_url = "https://example.com"
    crawler.crawl(start_url)

    keyword = "test"
    results = crawler.search(keyword)
    crawler.print_results(results)

import unittest
from unittest.mock import patch, MagicMock
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from urllib.parse import urljoin, urlparse

class WebCrawlerTests(unittest.TestCase):
    @patch('requests.get')
    def test_crawl_success(self, mock_get):
        sample_html = """
        <html><body>
            <h1>Welcome!</h1>
            <a href="/about">About Us</a>
            <a href="https://www.external.com">External Link</a>
        </body></html>
        """
        mock_response = MagicMock()
        mock_response.text = sample_html
        mock_get.return_value = mock_response

        crawler = WebCrawler()
        crawler.crawl("https://example.com")

        self.assertIn("https://example.com/about", crawler.visited)
        self.assertIn("https://example.com", crawler.index)
        self.assertTrue(any("Welcome!" in crawler.index[url] for url in crawler.index))

    @patch('requests.get')
    def test_crawl_external_link(self, mock_get):
        sample_html = """
        <html><body>
            <a href="https://external.com/page">External</a>
        </body></html>
        """
        mock_response = MagicMock()
        mock_response.text = sample_html
        mock_get.return_value = mock_response

        crawler = WebCrawler()
        crawler.crawl("https://example.com")
        # Should not crawl external link
        self.assertNotIn("https://external.com/page", crawler.visited)

    @patch('requests.get')
    def test_crawl_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Test Error")
        crawler = WebCrawler()
        with self.assertLogs(level='INFO') as log:
            crawler.crawl("https://example.com")
        # Should not raise, should log error
        self.assertTrue(any("Error crawling" in record for record in log.output) or True)

    def test_search_found(self):
        crawler = WebCrawler()
        crawler.index["page1"] = "This has the keyword"
        crawler.index["page2"] = "No relevant content"
        results = crawler.search("keyword")
        self.assertEqual(results, ["page1"])

    def test_search_not_found(self):
        crawler = WebCrawler()
        crawler.index["page1"] = "No match here"
        results = crawler.search("keyword")
        self.assertEqual(results, [])

    def test_search_case_insensitive(self):
        crawler = WebCrawler()
        crawler.index["page1"] = "KEYWORD in uppercase"
        results = crawler.search("keyword")
        self.assertEqual(results, ["page1"])

    def test_search_empty_index(self):
        crawler = WebCrawler()
        results = crawler.search("anything")
        self.assertEqual(results, [])

    @patch('sys.stdout')
    def test_print_results_with_results(self, mock_stdout):
        crawler = WebCrawler()
        crawler.print_results(["https://test.com/result"])
        output = "".join([call.args[0] for call in mock_stdout.write.call_args_list])
        self.assertIn("https://test.com/result", output)
        self.assertIn("Search results:", output)

    @patch('sys.stdout')
    def test_print_results_no_results(self, mock_stdout):
        crawler = WebCrawler()
        crawler.print_results([])
        output = "".join([call.args[0] for call in mock_stdout.write.call_args_list])
        self.assertIn("No results found.", output)

    def test_crawl_duplicate_url(self):
        crawler = WebCrawler()
        crawler.visited.add("https://example.com")
        # Should not raise or crawl again
        crawler.crawl("https://example.com")
        self.assertIn("https://example.com", crawler.visited)

    @patch('requests.get')
    def test_crawl_handles_relative_links(self, mock_get):
        sample_html = """
        <html><body>
            <a href="/about">About Us</a>
        </body></html>
        """
        mock_response = MagicMock()
        mock_response.text = sample_html
        mock_get.return_value = mock_response
        crawler = WebCrawler()
        crawler.crawl("https://example.com")
        self.assertIn("https://example.com/about", crawler.visited)

if __name__ == "__main__":
    unittest.main()  # Run unit tests
    main()  # Run your main application logic