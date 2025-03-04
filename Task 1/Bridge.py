from abc import ABC, abstractmethod

# Абстракція кольору
class Color(ABC):
    @abstractmethod
    def fill(self):
        pass

class Red(Color):
    def fill(self):
        return "Red"

class Blue(Color):
    def fill(self):
        return "Blue"

# Абстракція фігури
class Shape(ABC):
    def __init__(self, color: Color):
        self.color = color

    @abstractmethod
    def draw(self):
        pass


class Circle(Shape):
    def draw(self):
        return f"Drawing a {self.color.fill()} Circle"


class Square(Shape):
    def draw(self):
        return f"Drawing a {self.color.fill()} Square"

red_circle = Circle(Red())
blue_square = Square(Blue())

print(red_circle.draw())
print(blue_square.draw())