#!/usr/bin/env python3

# import kivy
from kivy.app import App
# from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle
from kivy.core.window import Window
from kivy.clock import Clock


class GameWidget(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        self._keyboard.bind(on_key_up=self._on_key_up)

        with self.canvas:
            self.player = Rectangle(source='./player.png', pos=(0, 0), size=(100, 100))

        self.keysPressed = set()

        Clock.schedule_interval(self.move_step, 0)  # refresh every frame

    def _on_keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self.on_key_down)
        self._keyboard.unbind(on_key_up=self.on_key_up)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        self.keysPressed.add(text)

    def _on_key_up(self, keyboard, keycode):
        text = keycode[1]
        if text in self.keysPressed:
            self.keysPressed.remove(text)

    def move_step(self, dt):
        x = self.player.pos[0]
        y = self.player.pos[1]

        step_size = 300 * dt  # inv proportional to cmputer speed

        if "w" in self.keysPressed:
            y += step_size
        if "s" in self.keysPressed:
            y -= step_size
        if "a" in self.keysPressed:
            x -= step_size
        if "d" in self.keysPressed:
            x += step_size

        self.player.pos = (x, y)


class MyApp(App):
    def build(self):
        return GameWidget()
        # return Label(text='Hello world!')


if __name__ == "__main__":
    app = MyApp()
    app.run()
