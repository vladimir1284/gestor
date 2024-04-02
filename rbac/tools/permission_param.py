class PermissionParam:
    def __init__(self, code: str, name: str = "", app: str = ""):
        self.code = code
        self.name = name
        self.app = app

    @property
    def get_perm(self):
        return f"{self.app}.{self.code}"
