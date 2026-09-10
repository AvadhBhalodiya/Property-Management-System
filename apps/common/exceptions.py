from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return None

    data = response.data

    if isinstance(data, dict) and "detail" in data:
        message = str(data["detail"])
        errors = {}
    elif isinstance(data, list):
        message = "Validation failed"
        errors = {"non_field_errors": data}
    else:
        message = "Validation failed"
        errors = data

    response.data = {"success": False, "message": message, "errors": errors}
    return response
