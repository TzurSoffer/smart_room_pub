from modules.THEME import THEME
from kivy.graphics import Color, RoundedRectangle
from kivy.properties import NumericProperty
from kivy.uix.button import Button

class BetterButton(Button):
    font_size_factor = NumericProperty(0.3)  # Factor to control font size relative to button height
    def __init__(self, bkColor=THEME["primary"], pressColor=THEME["secondary"], textColor=THEME["textColor"], size_hint_y=None, size_hint_x=1, **kwargs):
        super().__init__(**kwargs)
        self.normal_color = bkColor
        self.press_color = pressColor
        self.background_color = (0, 0, 0, 0)           # Transparent background
        self.background_normal = ""                    # Disable default background image
        self.color = textColor                         # Text color
        self.font_size = 18                            # Font size
        self.size_hint_y = size_hint_y                 # Allow height to be flexible
        self.size_hint_x = size_hint_x                 # Full width of the parent
        self.padding = (15, 10)                        # Padding for comfortable spacing

        # Set rounded background color
        with self.canvas.before:
            Color(*self.normal_color)
            self.rounded_rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[15])

        # Bind size and position for updating graphics
        self.bind(size=self.update_graphics, pos=self.update_graphics)
        
        # Bind on_press and on_release for color change
        self.bind(on_press=self.on_press, on_release=self.on_release)

        # Bind font size to button height
        self.bind(height=self.update_font_size)

    def update_font_size(self, *args):
        self.font_size = min(self.height * self.font_size_factor, self.width*self.font_size_factor)

    def update_graphics(self, *args):
        self.rounded_rect.size = self.size
        self.rounded_rect.pos = self.pos

    def on_press(self, *args):
        # Change to press color when pressed
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.press_color)
            self.rounded_rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[15])

    def on_release(self, *args):
        # Revert to normal color when released
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.normal_color)
            self.rounded_rect = RoundedRectangle(size=self.size, pos=self.pos)