class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, value=None):
        if not hasattr(self, 'value'):
            self.value = value

s1 = Singleton("First")
s2 = Singleton("Second")

print(s1.value)
print(s2.value)
print(s1 is s2)
