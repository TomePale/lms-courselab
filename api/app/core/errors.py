from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppError(Exception):
    """Pogreška poslovnog pravila: servis je podiže, handler je pretvara u odgovor.

    code je stalan i namijenjen klijentu, message je namijenjen čovjeku.
    """

    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code


async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": exc.message},
    )


async def validation_error_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    # Isti oblik kao AppError, uz popis polja koja nisu prošla provjeru
    errors = []
    for err in exc.errors():
        # loc je npr. ("body", "email") ili ("query", "limit")
        loc = [str(part)
               for part in err["loc"] if part not in ("body", "query")]
        message = err["msg"].removeprefix("Value error, ")
        errors.append({"field": ".".join(loc), "message": message})
    return JSONResponse(
        status_code=422,
        content={
            "code": "validation_error",
            "message": "Neispravni podaci u zahtjevu.",
            "errors": errors,
        },
    )


HTTP_ERROR_CODES = {
    401: "invalid_credentials",
    403: "forbidden",
    404: "not_found",
    405: "method_not_allowed",
}


async def http_exception_handler(
    _request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    # Pogreške koje podiže sam okvir, npr. nepostojeća putanja
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": HTTP_ERROR_CODES.get(exc.status_code, "http_error"),
            "message": str(exc.detail),
        },
        headers=getattr(exc, "headers", None),
    )


# SQLSTATE kod kojim PostgreSQL javlja kršenje UNIQUE ograničenja
UNIQUE_VIOLATION = "23505"


async def integrity_error_handler(
    _request: Request, exc: IntegrityError
) -> JSONResponse:
    # Servis provjerava pravila prije upisa, ali dva istodobna zahtjeva mogu
    # oba proći provjeru. Tada odlučuje baza, a mi umjesto 500 vraćamo 409.
    if getattr(exc.orig, "sqlstate", None) == UNIQUE_VIOLATION:
        return JSONResponse(
            status_code=409,
            content={"code": "duplicate", "message": "Zapis već postoji."},
        )
    # Ostala ograničenja (CHECK, FOREIGN KEY) servis bi trebao uhvatiti ranije;
    # ako ipak dođu do baze, to je sukob s podacima, a ne pad poslužitelja
    return JSONResponse(
        status_code=409,
        content={
            "code": "integrity_error",
            "message": "Podaci krše ograničenje baze.",
        },
    )
