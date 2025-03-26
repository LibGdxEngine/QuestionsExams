from rest_framework.exceptions import APIException


class YouHaveAlreadyRatedException(APIException):
    status_code = 400
    default_detail = "You have already rated this article"
