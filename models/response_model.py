from fastapi import HTTPException


def response_model(data, message):
    return {
        # "data": [data],
        "data": data,
        "code": 200,
        "message": message,
    }


def error_response_model(error="Server error", code=500):
    raise HTTPException(status_code=code, detail=error)
