import os
import csv
from time import sleep
from tempfile import NamedTemporaryFile

from dotenv import load_dotenv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options

from app.schemas import Resposta

load_dotenv()

region_default = "//*[@id='screener-criteria']/div[2]/div[1]/div[1]/div[1]/div/div[2]/ul/li[1]/button"
button_add = (
    "//*[@id='screener-criteria']/div[2]/div[1]/div[1]/div[1]/div/div[2]/ul/li/button"
)
find_region = "//*[@id='dropdown-menu']/div/div[1]/div/input"
find_stock = "//*[@id='screener-criteria']/div[2]/div[1]/div[3]/button[1]"
table = "//*[@id='scr-res-table']/div[1]/table/tbody"
next = "//*[@id='scr-res-table']/div[2]/button[3]"

options = Options()
options.page_load_strategy = "none"

hidden_crawler = os.getenv("HIDDENCRAWLER")

if hidden_crawler and int(hidden_crawler) == 1:
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument('--no-sandbox')
    options.add_argument('--remote-debugging-port=9222')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1600,1000')

class WebCrawler:
    """
        Classe para realizar web scraping em páginas financeiras usando Selenium.

        Esta classe implementa métodos para iniciar um driver, carregar uma página,
        interagir com elementos da página e extrair dados estruturados.

        Parâmetros:
            region (str): Nome da região que será usada durante a navegação e extração de dados.
    """

    def __init__(self, region) -> None:
        """
            Inicializa a instância do WebCrawler com a URL base.

            Parâmetros:
                region (str): Região a ser usada para filtrar dados.
        """
        self.url = "https://finance.yahoo.com/screener/new"
        self.driver = None

    def start_driver(self):
        """
            Inicia o driver do Selenium com as configurações predefinidas.
        """
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_window_size(1600, 1000)

    def load_page(self):
        """
            Carrega a página inicial especificada na URL.
        """
        self.driver.get(self.url)
        sleep(5)

    def get_element_by_xpath(self, xpath: str, click: bool = False, time: int = 2):
        """
            Localiza um elemento da página usando um XPATH específico.

            Parâmetros:
                xpath (str): XPATH do elemento a ser localizado.
                click (bool): Indica se o elemento deve ser clicado. Padrão é False.
                time (int): Tempo de espera antes de clicar no elemento. Padrão é 2 segundos.

            Retorna:
                WebElement: O elemento encontrado.

            Lança:
                Exception: Se o elemento não for encontrado após várias tentativas.
        """

        for _ in range(10):
            element = None
            try:
                element = WebDriverWait(self.driver, time).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
            except NoSuchElementException:
                continue
            except TimeoutException:
                continue

        if not element:
            raise Exception(f"Element with XPATH: {xpath} not found")

        if click:
            sleep(time)
            element.click()

        return element

    def get_page_source(self):
        """
            Obtém o código-fonte HTML da página atual.

            Retorna:
                str: Código-fonte HTML da página.
        """
        return self.driver.page_source

    def parse_data(self, html):
        """
            Analisa o HTML e extrai dados de uma tabela.

            Parâmetros:
                html (str): Código-fonte HTML da página.

            Retorna:
                list: Lista de dicionários com os dados extraídos da tabela.
                    Cada dicionário contém 'Symbol', 'Name' e 'Price'.
        """

        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("tbody")
        data = []

        for row in table.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) > 2:
                symbol = cols[0].text.strip()
                name = cols[1].text.strip()
                price = cols[2].text.strip()
                data.append({"Symbol": symbol, "Name": name, "Price": price})
        return data

    def element_is_disabled(self, element):
        """
            Verifica se um elemento está desativado.

            Parâmetros:
                element (WebElement): Elemento a ser verificado.

            Retorna:
                bool: True se o elemento estiver desativado, caso contrário False.
        """
        return bool(element.get_attribute("disabled"))


def get_data_by_region(region) -> Resposta:
    """
        Extrai dados de uma região específica utilizando um web crawler.

        Esta função utiliza um web crawler para navegar em uma página web, extrair dados 
        relacionados à região especificada e gerar um arquivo CSV com os dados coletados.

        Parâmetros:
            region (str): Nome da região para a qual os dados devem ser coletados.

        Retorna:
            Resposta: Um objeto contendo o caminho do arquivo CSV gerado (atributo `success`) 
                    ou uma mensagem de erro (atributo `erro`).

        Lança:
            Exception: Em caso de qualquer erro durante a execução do web crawler ou a geração do CSV.
    """

    try:
        crawler = WebCrawler(region)
        crawler.start_driver()
        crawler.load_page()
        crawler.get_element_by_xpath(xpath=region_default, click=True)
        crawler.get_element_by_xpath(xpath=button_add, click=True)
        find_region_input = crawler.get_element_by_xpath(xpath=find_region)
        find_region_input.send_keys(region)
        crawler.get_element_by_xpath(
            xpath=f"//span[contains(text(), '{region}')]", click=True
        )
        crawler.get_element_by_xpath(xpath=find_stock, click=True, time=3)

        data = []

        while True:
            sleep(3)
            html = crawler.get_page_source()
            data.extend(crawler.parse_data(html=html))
            next_button = crawler.get_element_by_xpath(xpath=next, time=4)
            if crawler.element_is_disabled(element=next_button):
                break
            next_button.click()

        csv_file = generate_csv(data=data)
        if csv_file.erro:
            raise Exception(csv_file.erro)

        return Resposta(success=csv_file.success)

    except Exception as e:
        return Resposta(erro=f"(get_data_by_region) -> {e}")


def generate_csv(data) -> Resposta:
    """
        Gera um arquivo CSV a partir de uma lista de dicionários.

        Esta função cria um arquivo CSV temporário com base nos dados fornecidos. 
        Cada dicionário na lista representa uma linha no arquivo, e as chaves dos dicionários 
        são usadas como cabeçalhos das colunas.

        Parâmetros:
            data (list): Lista de dicionários contendo os dados a serem escritos no arquivo CSV.

        Retorna:
            Resposta: Um objeto contendo o caminho do arquivo CSV gerado (atributo `success`) 
                    ou uma mensagem de erro (atributo `erro`).

        Lança:
            ValueError: Se a lista `data` estiver vazia.
            Exception: Em caso de qualquer outro erro durante o processo de geração do CSV.
    """

    try:
        if not data:
            raise Exception("The list data is empty")

        temp_file = NamedTemporaryFile(
            delete=False, mode="w", newline="", encoding="utf-8", suffix=".csv"
        )

        headers = data[0].keys()

        with temp_file as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)

        return Resposta(success=temp_file.name)
    except Exception as e:
        return Resposta(erro=f"(generate_csv) -> {e}")
