# Web Crawler para Dados Financeiros

Este projeto é um **crawler** desenvolvido em **Python** que utiliza **Selenium** e **BeautifulSoup** para extrair dados financeiros da plataforma [Yahoo Finance Screener](https://finance.yahoo.com/screener/new). Os dados obtidos são armazenados em um arquivo CSV que pode ser baixado por meio de uma interface web construída com **FastAPI**.

## Índice

- [Características](#características)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Variáveis ​​de ambiente](#variáveis)
- [Uso](#uso)
- [Docker](#docker)
- [Testes](#testes)

## Características

- Extração de dados financeiros como **símbolos**, **nomes** e **preços**.
- Interface web com **FastAPI** para facilitar o download de dados.
- Pode ser executado opcionalmente em modo **headless** para servidores.
- Suporte para geração de arquivos **CSV** com os resultados.

## Requisitos

Certifique-se de ter as seguintes ferramentas instaladas:

- **Python 3.12+**
- **Google Chrome** e **ChromeDriver**
- **Docker** (opcional para contêineres)

Dependências do Python especificadas no `requirements.txt`:

- `selenium`
- `beautifulsoup4`
- `fastapi`
- `python-dotenv`

## Instalação

1. Clone este repositório:

   ```bash
   git clone git@github.com:mitdua/crawler_verx.git
   cd web-crawler-financas
   ```

2. Crie um ambiente virtual e ative-o:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
3. Instale as dependências:
    ```
    pip install -r requirements.txt

    ```
## Variáveis

Para executar este projeto, você precisará adicionar as seguintes variáveis ​​de ambiente ao seu arquivo .env,
com o valor "1" para ocultar o navegador usado pelo rastreador, "0" para torná-lo visível

`HIDDENCRAWLER`



## Uso

Execução Local

1. Inicie o servidor FastAPI:

    ```bash
    uvicorn app.app:app --reload
    ```
2. Acesse a aplicação no seu navegador:

    ```bash
    http://localhost:8000
    ```
## Docker
Você pode executar a aplicação usando Docker (recomendado):

1. Execute a aplicação com docker compose:

    ```bash
    docker compose up --build    
    ```
2. Acesse a aplicação no seu navegador:

    ```bash
    http://localhost:8000
    ```

## Testes
Os testes unitários estão no diretório tests. Eles podem ser executados com pytest:

1. Execute o seguinte comando:

    ```bash
    pytest tests/
    ```