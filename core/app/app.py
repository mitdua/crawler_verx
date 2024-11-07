import os
from pathlib import Path
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, HTMLResponse, Response, FileResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.crawler import get_data_by_region

app = FastAPI(docs_url=None, redoc_url=None)

      
static_dir = Path(f"{Path(__file__).resolve().parent.parent}/static/")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

template_dir = Path(f"{Path(__file__).resolve().parent.parent}/template/")
templates = Jinja2Templates(directory=template_dir)


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
        Manipulador personalizado para exceções HTTP do Starlette.

        Este manipulador trata exceções HTTP levantadas durante o ciclo de vida da aplicação. 
        Em caso de erro 404 (não encontrado), uma página HTML personalizada é retornada. 
        Para outros códigos de erro, uma resposta JSON com detalhes da exceção é gerada.

        Parâmetros:
            request (Request): Objeto de requisição atual.
            exc (StarletteHTTPException): Exceção HTTP levantada durante o processamento da requisição.

        Retorna:
            TemplateResponse: Página HTML para erros 404.
            JSONResponse: Resposta JSON com detalhes da exceção para outros códigos de status.
    """

    if exc.status_code == 404:
        return templates.TemplateResponse(
            request=request,
            name="404.html",
            status_code=HTTPStatus.NOT_FOUND,
        )
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
        Rota principal da aplicação.

        Renderiza a página inicial utilizando um template HTML.

        Parâmetros:
            request (Request): Objeto de requisição atual.

        Retorna:
            TemplateResponse: Resposta contendo a renderização do template 'index.html' com o status HTTP 200.
    """

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        status_code=HTTPStatus.OK,
    )


@app.get("/get_data/{region}", status_code=HTTPStatus.OK)
async def get_data_crawler(region: str):
    """
        Endpoint para obter dados específicos de uma região.

        Este endpoint processa uma solicitação para recuperar dados com base na região informada. 
        Os dados são retornados em formato CSV, ou uma mensagem de erro é exibida em caso de falha.

        Parâmetros:
            region (str): Nome da região para a qual os dados devem ser recuperados.

        Retorna:
            FileResponse: Arquivo CSV contendo os dados solicitados, com o tipo de mídia "text/csv".
            Response: Mensagem de erro em caso de falha, com status HTTP 400 (Bad Request).
    """

    try:
        data = get_data_by_region(region=region)

        if data.erro:
            raise Exception(data.erro)

        return FileResponse(
            path=data.success, media_type="text/csv", filename=f"{region}.csv"
        )

    except Exception as e:        
        return Response(
            content=f"{e}",
            status_code=HTTPStatus.BAD_REQUEST,
        )
