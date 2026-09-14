class AppException(Exception):
    # Базовое исключение приложения
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class BusinessError(AppException):
    # Нарушение бизнес-логики (400)
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class NotFoundError(AppException):
    # Объект не найден (404)
    def __init__(self, message: str = "Object not found"):
        super().__init__(message, status_code=404)


class UnauthorizedError(AppException):
    # Не авторизован (401)
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status_code=401)


class ForbiddenError(AppException):
    # Недостаточно прав (403)
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, status_code=403)


class ConflictError(AppException):
    # Конфликт данных (409)
    def __init__(self, message: str):
        super().__init__(message, status_code=409)


class ValidationError(AppException):
    # Ошибка валидации (422)
    def __init__(self, message: str):
        super().__init__(message, status_code=422)
