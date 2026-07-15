"""
====================================================================================
  appify_social_api

  Date          : 7/12/2026 11:29 PM
  Author        : rahir
  Description:
    ----------

====================================================================================
Last Update    :
Last Modifier  :
"""


# app/utils/response.py
from typing import Any, Optional
from fastapi.responses import JSONResponse

def success_response(data: Any = None, status_code: int = 200) -> JSONResponse:

    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "data": data,
            "error": None
        }
    )

def error_response(message: str, error_code: str, status_code: int = 400, details: Any = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": error_code,
                "message": message,
                "details": details
            }
        }
    )