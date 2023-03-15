from django.utils.translation import gettext as _
from rest_framework.response import Response

from common import app_logger

logger = app_logger.createLogger("app")


HTTP_REST_MESSAGES = {
    "200": _("Success"),
    "400": _("Failed"),
    "401": _("Authentication Failed"),
    "426": _("Version Mismatch"),
    "429": _("Too many requests"),
    "500": _("Internal server error"),
}


def build_response(
    status,
    message,
    data=dict(),
    errors=dict(),
    errors_code=None,
    headers=None,
):
    try:
        if status != 200:
            # empty dict or a string?
            if isinstance(errors, str):
                # standardise errors
                errors = {"non_field_errors": [str(_(errors))]}

            if errors is None or isinstance(errors, dict) and len(errors) == 0:
                errors = {"non_field_errors": [str(_(message))]}

            if (
                isinstance(errors, dict)
                and errors.get("non_field_errors", [""])[0] in []
            ):
                # errors_code = common.errors.ERRORCODE[errors["non_field_errors"][0]]
                logger.error(
                    "Response: %s %s %s %s",
                    str(status),
                    str(message),
                    str(errors),
                    str(errors_code),
                )
                try:
                    for key, values in errors.items():
                        error = [value[:] for value in values]
                    error[:] = [_(x) for x in error]
                    errors = dict(zip(list(errors.keys()), error))
                except Exception as e:
                    pass
                    logger.error(f"Exception : {str(e)}")
            else:
                # errors_code = common.errors.ERRORCODE.get(
                #     str(errors), common.errors.DEFAULT_ERRORCODE
                # )
                logger.error(
                    "Response: %s %s %s %s",
                    str(status),
                    str(message),
                    str(errors),
                    str(errors_code),
                )
                try:
                    if isinstance(errors, dict):
                        # for key, values in errors.items():
                        #     error = [value[:] for value in values]
                        # error[:] = [_(x) for x in error]
                        errors = dict(zip(list(errors.keys()), errors.values()))
                except Exception as e:
                    pass
                    logger.error(f"Exception : {str(e)}")

        logger.debug(
            "Response: 200 OK %s %s %s %s",
            str(status),
            str(message),
            str(errors),
            str(errors_code),
        )
        message = (
            message if isinstance(message, bool) or message is None else _(message)
        )
        return Response(
            {
                "status_code": status,
                "message": message,
                "data": data,
                "errors": errors,
                "errors_code": errors_code,
            },
            status=status,
            headers=headers,
        )
    except Exception as e:
        logger.error(f"Exception : {str(e)}")
        message = (
            message if isinstance(message, bool) or message is None else _(message)
        )
        return Response(
            {
                "status_code": status,
                "message": message,
                "data": data,
                "errors": errors,
                "errors_code": errors_code,
            },
            status=status,
            headers=headers,
        )
