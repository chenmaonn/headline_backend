"""模拟用户注册"""


class InMemoryUserRepository:
    def __init__(self) -> None:
        """初始化虚拟用户表"""
        self._users = []

    # def create(self, name: str, email: str)
