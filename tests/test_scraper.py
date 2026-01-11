import unittest
from unittest.mock import MagicMock, patch
from src.scraper import BookScraper

class TestBookScraper(unittest.TestCase):

    def setUp(self):
        self.scraper = BookScraper()

    @patch('src.scraper.requests.Session.get')
    def test_fetch_page_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html></html>"
        mock_get.return_value = mock_response

        content = self.scraper.fetch_page("http://test.com")
        self.assertIsNotNone(content)

    def test_parse_books(self):
        # Sample HTML snippet mimicking the target site
        html_content = """
        <article class="product_pod">
            <h3><a href="catalogue/a-light-in-the-attic_1000/index.html" title="A Light in the Attic">A Light in the ...</a></h3>
            <p class="price_color">£51.77</p>
            <p class="star-rating Three"></p>
            <p class="instock availability">
                <i class="icon-ok"></i>
                In stock
            </p>
        </article>
        """
        data = self.scraper.parse_books(html_content)
        self.assertEqual(len(data), 1)
        book = data[0]
        self.assertEqual(book['title'], "A Light in the Attic")
        self.assertEqual(book['price'], 51.77)
        self.assertEqual(book['rating'], 3)
        self.assertIn("In stock", book['availability'])
        
        # Data Quality Check: Price should be positive
        self.assertTrue(book['price'] > 0, "Price should be a positive number")

if __name__ == '__main__':
    unittest.main()
