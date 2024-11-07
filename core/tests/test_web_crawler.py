import pytest
from selenium.webdriver.remote.webelement import WebElement
from unittest.mock import MagicMock

from app.crawler import WebCrawler

@pytest.fixture
def crawler():
    return WebCrawler(region="TestRegion")

def test_start_driver(crawler):
    crawler.start_driver = MagicMock() 
    crawler.start_driver()
    crawler.start_driver.assert_called_once()

def test_get_element_by_xpath(crawler):
    crawler.driver = MagicMock() 
    mocked_element = MagicMock(spec=WebElement)
    crawler.driver.find_element.return_value = mocked_element

    element = crawler.get_element_by_xpath("//mocked_xpath")
    assert element == mocked_element

def test_parse_data_valid_html():
    html = """
    <table>
        <tbody>
            <tr><td>AAPL</td><td>Apple Inc.</td><td>150.00</td></tr>
        </tbody>
    </table>
    """
    crawler = WebCrawler("Test")
    data = crawler.parse_data(html)
    assert len(data) == 1
    assert data[0]["Symbol"] == "AAPL"
    assert data[0]["Price"] == "150.00"

def test_element_is_disabled(crawler):
    mocked_element = MagicMock(spec=WebElement)
    mocked_element.get_attribute.return_value = "true"
    assert crawler.element_is_disabled(mocked_element)
