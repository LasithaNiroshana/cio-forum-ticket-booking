from fastapi.responses import JSONResponse


def response_model(data, message):
    return {
        # "data": [data],
        "data": data,
        "code": 200,
        "message": message,
    }


def error_response_model(error="Server error", code=500):
    return JSONResponse(
        status_code=code,
        content={"detail": error}
    )
