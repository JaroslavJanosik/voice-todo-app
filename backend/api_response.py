from flask import jsonify


def success_response(result=None, status_code=200):
    return jsonify(_build_payload(status_code=status_code, is_success=True, result=result)), status_code


def failure_response(error_messages, status_code=400, result=None):
    return jsonify(
        _build_payload(
            status_code=status_code,
            is_success=False,
            error_messages=error_messages,
            result=result,
        )
    ), status_code


def _build_payload(status_code, is_success, result=None, error_messages=None):
    return {
        "statusCode": status_code,
        "isSuccess": is_success,
        "errorMessages": _normalize_error_messages(error_messages),
        "result": result,
    }


def _normalize_error_messages(error_messages):
    if error_messages is None:
        return []

    if isinstance(error_messages, str):
        return [error_messages]

    return [message for message in error_messages if isinstance(message, str) and message.strip()]
