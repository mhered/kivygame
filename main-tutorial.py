#!/usr/bin/env python3

# import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.uix.label import CoreLabel


class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # initialize keyboard input
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        self._keyboard.bind(on_key_up=self._on_key_up)

        # initialize score
        self._score_label = CoreLabel(text="Score: 0", markup=True,
                                      font_size=36, font_color='#FFF000',
                                      font_name='./assets/Slugterra.otf')
        self._score_label.refresh()
        self._score = 0

        self.register_event_type("on_frame")

        # Rendering: add instructions to the canvas attribute of the Widget
        with self.canvas:
            self.player = Rectangle(source='./assets/player.png', pos=(0, 0), size=(100, 100))
            self.enemy = Rectangle(source='./assets/enemy.png', pos=(400, 400), size=(100, 100))
            self._score_instruction = Rectangle(
                texture=self._score_label.texture, pos=(0, Window.height - 50), size=self._score_label.texture.size)
        # init empty sets
        self.keysPressed = set()
        self._entities = set()

        # Scheduler to call refresh regularly (here 0 = at every frame)
        Clock.schedule_interval(self._on_frame, 0)

        # play background music
        self.sound = SoundLoader.load("./assets/thunder.ogg")
        self.sound.play()

    def _on_frame(self, dt):
        self.dispatch("on_frame", dt)

    def on_frame(self, dt):
        pass

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        self._score = value
        self._score_label.text = "Score: " + str(value)
        self._score_label.refresh()
        self._score_instruction.texture = self._score_label.texture
        self._score_instruction.size = self._score_label.texture.size

    def add_entity(self, entity):
        self._entities.add(entity)
        self.canvas.add(entity._instruction)

    def remove_entity(self, entity):
        if entity in self._entities:
            self._entities.remove(entity)
            self.canvas.remove(entity._instruction)

    def collides(sefl, e1, e2):
        # COLLIDES implements basic AABB (axis aligned bounding box) collission detection)
        r1x = e1.pos[0]
        r1y = e1.pos[1]
        r2x = e2.pos[0]
        r2y = e2.pos[0]
        r1w = e1.size[0]
        r1h = e1.size[1]
        r2w = e2.size[0]
        r2h = e2.size[1]

        if r1x < (r2x + r2w) and (r1x + r1w) > r2x and r1y < (r2y + r2h) and (r1y + r1h) > r2y:
            return True
        else:
            return False

    def colliding_entities(self, entity):
        result = set()
        for e in self._entities:
            if self.collides(e, entity):
                result.add(e)
        result

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
        # MOVE_STEP: movement and collision logic

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

        if self.collides(self.player, self.enemy):
            print("Gotcha!")
        else:
            print('ok')


class Entity(object):
    def __init__(self):
        self._pos = (0, 0)
        self._size(50, 50)
        self._source = "dummy.png"
        self._instruction = Rectangle(pos=self._pos, size=self._size)

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        self._pos = value
        self._instruction.pos = self._pos

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value
        self._instruction.size = self._size

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, value):
        self._source = value
        self._instruction.source = self._source


class Bullet(Entity):
    def __init(self, pos, speed=300):
        self._speed = speed
        self.pos = pos
        game.bind(on_frame=self.move_step)

    def stop_callbacks(self):
        game.unbind(on_frame=self.move_step)

    def move_step(self, dt):
        # check for out of bounds/collision
        if self.pos[1] > Window.height:
            self.stop_callbacks()
            game.remove_entity(self)
            return
        for e in game.colliding_entities(self):
            if isinstance(e, Enemy):
                Explosion(self.pos)
                self.stop_callbacks()
                game.remove_entity(self)
                e.stop_callbacks()
                game.remove_entity(e)
                return
        # move
        step_size = self._speed * dt
        new_x = self.pos[0]
        new_y = self.pos[1] + step_size
        self.pos = (new_x, new_y)


class Enemy(Entity):
    def __init(self, pos, speed=100):
        self._speed = speed
        self.pos = pos
        game.bind(on_frame=self.move_step)

    def stop_callbacks(self):
        game.unbind(on_frame=self.move_step)

    def move_step(self, dt):
        # check for out of bounds/collision
        if self.pos[1] < 0:
            self.stop_callbacks()
            game.remove_entity(self)
            game.score -= 10
            return
        for e in game.colliding_entities(self):
            if e == game.player:
                Explosion(self.pos)
                self.stop_callbacks()
                game.remove_entity(self)
                game.score -= 10
                return
        # move
        step_size = self._speed * dt
        new_x = self.pos[0]
        new_y = self.pos[1] + step_size
        self.pos = (new_x, new_y)


class Explosion(Entity):
    def __init__(self, pos):
        self._source = "./assets/explosion2.png"


game = GameWidget()


class MyApp(App):
    def build(self):
        return game


if __name__ == "__main__":
    app = MyApp()
    app.run()
