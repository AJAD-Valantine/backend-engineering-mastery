class ShopException(Exception):
    def __init__(self, message: str, status_code: int = 500, headers: dict | None = None):
        self.message = message
        self.status_code = status_code
        self.headers = headers
        super().__init__(self.message)