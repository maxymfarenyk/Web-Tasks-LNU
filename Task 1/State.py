from abc import ABC, abstractmethod

# Контекст
class TrafficLight:
    def __init__(self, state):
        self.state = state

    def set_state(self, state):
        self.state = state

    def change(self):
        self.state.handle(self)

# Абстрактний стан
class State(ABC):
    @abstractmethod
    def handle(self, traffic_light):
        pass


# Конкретні стани
class Red(State):
    def handle(self, traffic_light):
        print("Red light - Stop")
        traffic_light.set_state(Green())


class Yellow(State):
    def handle(self, traffic_light):
        print("Yellow light - Get ready")
        traffic_light.set_state(Red())


class Green(State):
    def handle(self, traffic_light):
        print("Green light - Go")
        traffic_light.set_state(Yellow())

traffic_light = TrafficLight(Red())
traffic_light.change()
traffic_light.change()
traffic_light.change()
