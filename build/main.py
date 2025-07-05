from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Line
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from random import choice

Window.size = (600, 800)


class Paddle(Widget):
    def __init__(self, color=(0.2, 0.8, 1), **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(*color)
            self.circle = Ellipse(pos=self.pos, size=self.size)
        self.bind(pos=self.update_shape, size=self.update_shape)

    def update_shape(self, *args):
        self.circle.pos = self.pos
        self.circle.size = self.size


class Puck(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.velocity = Vector(choice([-4, 4]), choice([-3, 3]))
        with self.canvas:
            Color(1, 0.5, 0)
            self.circle = Ellipse(pos=self.pos, size=self.size)
        self.bind(pos=self.update_shape, size=self.update_shape)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

    def update_shape(self, *args):
        self.circle.pos = self.pos
        self.circle.size = self.size


class AirHockeyGame(Screen):
    def __init__(self, single_player=False, **kwargs):
        super().__init__(**kwargs)
        self.single_player = single_player
        self.score1 = 0
        self.score2 = 0

        self.canvas_widget = Widget()
        self.add_widget(self.canvas_widget)

        self.paddle1 = Paddle(size=(60, 60))
        self.paddle2 = Paddle(size=(60, 60), color=(1, 0.3, 0.3))
        self.puck = Puck(size=(30, 30))

        self.label = Label(text="0 - 0", font_size='24sp',
                           size_hint=(None, None),
                           pos=(Window.width / 2 - 50, Window.height - 40),
                           color=(1, 1, 1, 1))

        self.canvas_widget.add_widget(self.paddle1)
        self.canvas_widget.add_widget(self.paddle2)
        self.canvas_widget.add_widget(self.puck)
        self.add_widget(self.label)

        with self.canvas_widget.canvas:
            Color(1, 1, 1)
            self.goal_margin = Window.width * 0.3
            self.goal_top = Line()
            self.goal_bottom = Line()

        Clock.schedule_once(self.start_game)
        Clock.schedule_interval(self.update, 1 / 60)

    def start_game(self, dt):
        self.paddle1.center = (self.width / 2, self.height * 0.1)
        self.paddle2.center = (self.width / 2, self.height * 0.9)
        self.puck.center = self.center
        self.goal_margin = self.width * 0.3

        self.goal_bottom.points = [self.goal_margin, 2, self.width - self.goal_margin, 2]
        self.goal_top.points = [self.goal_margin, self.height - 2, self.width - self.goal_margin, self.height - 2]

    def on_touch_move(self, touch):
        if touch.y < self.height / 2:
            self.paddle1.center = touch.pos
        elif not self.single_player:
            self.paddle2.center = touch.pos

    def update(self, dt):
        self.puck.move()

        if self.puck.x <= 0 or self.puck.right >= self.width:
            self.puck.velocity.x *= -1

        for paddle in (self.paddle1, self.paddle2):
            if self.puck.collide_widget(paddle):
                offset = (Vector(*self.puck.center) - Vector(*paddle.center)).normalize() * 4
                self.puck.velocity = -self.puck.velocity + offset

        if self.single_player:
            if self.puck.center_y > self.height / 2:
                if self.puck.center_x > self.paddle2.center_x:
                    self.paddle2.center_x += min(6, self.puck.center_x - self.paddle2.center_x)
                elif self.puck.center_x < self.paddle2.center_x:
                    self.paddle2.center_x -= min(6, self.paddle2.center_x - self.puck.center_x)

        if self.puck.y <= 0:
            if self.goal_margin <= self.puck.center_x <= self.width - self.goal_margin:
                self.score2 += 1
                self.reset_puck()
        elif self.puck.top >= self.height:
            if self.goal_margin <= self.puck.center_x <= self.width - self.goal_margin:
                self.score1 += 1
                self.reset_puck()

        self.label.text = f"{self.score1} - {self.score2}"

    def reset_puck(self):
        self.puck.center = self.center
        self.puck.velocity = Vector(choice([-4, 4]), choice([-3, 3]))


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        layout.add_widget(Label(text="Air Hockey", font_size='32sp', size_hint=(1, 0.3)))

        ai_button = Button(text="Play vs AI", size_hint=(1, 0.3))
        ai_button.bind(on_press=self.play_ai)
        layout.add_widget(ai_button)

        multi_button = Button(text="Play vs Friend", size_hint=(1, 0.3))
        multi_button.bind(on_press=self.play_multiplayer)
        layout.add_widget(multi_button)

        self.add_widget(layout)

    def play_ai(self, instance):
        self.manager.add_widget(AirHockeyGame(name="game_ai", single_player=True))
        self.manager.current = "game_ai"

    def play_multiplayer(self, instance):
        self.manager.add_widget(AirHockeyGame(name="game_multi", single_player=False))
        self.manager.current = "game_multi"


class AirHockeyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        return sm


if __name__ == '__main__':
    AirHockeyApp().run()
