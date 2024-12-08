import time
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.uix.slider import Slider
from kivy.clock import Clock
from modules.betterButton import BetterButton
from modules import lights
from modules import leds
from modules.THEME import THEME

class UnifiedControl(BoxLayout):
    def __init__(self, ip, port=1883, lightsFloor=25, leds_topic="smartRoom/ardu/output", lights_topic="smartRoom/generic/output", **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.background_color = THEME["background"]

        # Topics and MQTT setup
        self.leds = leds.Leds(ip, port=port, topic=leds_topic)
        self.lights = lights.Lights(ip, port=port, topic=lights_topic)
        self.threshold = 60  # Slider threshold to switch between LEDs and lights
        self.lightsFloor = lightsFloor  # Brightness for lights when switching from leds
        self.current_mode = "leds"  # Can be 'leds' or 'lights'

        self.update_event = None

        # Header label
        # self.header_label = Label(text="Unified Control", font_size=24, bold=True, color=(0.1, 0.6, 0.8, 1), size_hint_y=None, height=40)
        # self.add_widget(self.header_label)

        # Brightness slider
        self.brightness_slider = BetterSlider(threshold=self.threshold, min=0, max=100, value=100, size_hint_y=0.2)
        self.brightness_slider.bind(on_touch_down=self.start_updates)
        self.brightness_slider.bind(on_touch_up=self.stop_updates)

        # On button
        self.on_button = BetterButton(text="On", size_hint_y=0.3, padding=(10,10))
        self.on_button.bind(on_press=self.turn_on)

        # Off button
        self.off_button = BetterButton(text="Off", size_hint_y=0.3, padding=(10,10))
        self.off_button.bind(on_press=self.turn_off)
        
        self.add_widget(self.on_button)
        self.add_widget(self.brightness_slider)
        self.add_widget(self.off_button)

    def update_brightness(self, *args):
        """Handle slider changes and switch modes if the threshold is crossed."""
        value = self.brightness_slider.value

        if value <= self.threshold and self.current_mode != "leds":
            self.current_mode = "leds"

        elif value > self.threshold and self.current_mode != "lights":
            self.current_mode = "lights"

        # Send brightness commands based on the current mode
        if self.current_mode == "leds":
            color = [int(value*2.55*(100/self.threshold))]*3  #< Scale to 0-255 for LEDs
            self.leds.ledsColor(color)
            self.lights.lightsOff()
        elif self.current_mode == "lights":
            brightness = int((value-self.threshold)*(100/(100-self.threshold))+self.lightsFloor)
            self.lights.lightsSet(brightness)
            time.sleep(0.15)
            self.leds.ledsOff()

    def start_updates(self, slider, touch):
        """Start periodic updates when the slider is adjusted."""
        if slider.collide_point(*touch.pos):
            self.stop_updates()  # Ensure no overlapping updates
            self.update_event = Clock.schedule_once(self.update_brightness)
            self.update_event = Clock.schedule_interval(self.update_brightness, 0.1)

    def stop_updates(self, *args):
        """Stop periodic updates when the slider adjustment ends."""
        if self.update_event:
            self.update_event.cancel()
            self.update_event = None

    def turn_on(self, instance):
        """Turn on the lights or LEDs depending on the current mode."""
        self.brightness_slider.value = 100
        self.lights.lightsOn()
        self.leds.ledsOff()

    def turn_off(self, instance):
        """Turn off both LEDs and lights."""
        self.brightness_slider.value = 0
        self.lights.lightsOff()
        self.leds.ledsOff()

class BetterSlider(Slider):
    """Slider with dynamic color changes based on the threshold."""

    def __init__(self, threshold, **kwargs):
        super().__init__(**kwargs)
        self.threshold = threshold
        self.track_color = (1, 1, 1, 1)  # Default track color (white)
        self.red_color = (1, 0, 0, 1)   # Red for below threshold
        self.white_color = (1, 1, 1, 1) # White for above threshold

        self.background_width = 0
        self.cursor_size = (0, 0)

        # Redraw the slider initially
        self.bind(value=self.update_canvas)
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def on_touch_move(self, touch):
        """Update track color dynamically as slider moves."""
        super().on_touch_move(touch)
        self.update_canvas()

    def on_touch_up(self, touch):
        """Redraw the canvas when touch ends."""
        super().on_touch_up(touch)
        self.update_canvas()

    def update_canvas(self, *args):
        """Redraw the slider with the appropriate color."""
        with self.canvas.after:
            self.canvas.after.clear()  # Clear previous drawings
            Color(*self.red_color)
            Rectangle(pos=(self.pos[0]+15, self.pos[1]+self.height/2-5), size=(self.width*self.threshold/100-15, 10))
            Color(*self.white_color)
            Rectangle(pos=(self.pos[0]+(self.width*self.threshold/100), self.pos[1]+self.height/2-5), size=(self.width*(1-self.threshold/100)-15, 10))

            Color(1, 1, 1, 1) # White color for the center part
            knob_x = self.pos[0] + self.width * (self.value - self.min) / (self.max - self.min) - 15
            knob_y = self.pos[1] + self.height / 2 - 15
            Ellipse(pos=(knob_x, knob_y), size=(30, 30))