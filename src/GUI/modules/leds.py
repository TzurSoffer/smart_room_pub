import modules.mqttCommunication as communication
from modules.THEME import THEME

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.colorpicker import ColorPicker

from modules.betterButton import BetterButton

class Leds:
    def __init__(self, ip, port, topic="smartRoom/ardu/output"):
        self.ip = ip
        self.port = port
        self.topic = topic

    def publish(self, topic, msg):
        try:
            com = communication.COM(self.ip, self.port)
            com.connect()
            com.publish(topic, msg)
            com.disconnect()
        except:
            pass

    def ledsOff(self):
        self.publish(self.topic, "wsLedsOff")

    def ledsColor(self, color):
        color_str = f"{color[0]},{color[1]},{color[2]}"
        self.publish(self.topic, f"wsSetConfig {color_str}")

class LedsGroup(BoxLayout):
    def __init__(self, ip, port=1883, topic="smartRoom/ardu/output", **kwargs):
        super().__init__(**kwargs)
        self.background_color = THEME["background"]
        self.orientation = 'vertical'
        self.leds = Leds(ip, port, topic)
        self.currentColor = None

        self.label_leds = Label(text="LED Strip", font_size=24, bold=True, color=(0.1, 0.6, 0.8, 1), size_hint_y=None, height=40)
        self.add_widget(self.label_leds)

        self.leds_brightnessSlider = Slider(min=0, max=100, value=100, size_hint_y=0.5)

        self.leds_brightnessSlider.bind(on_touch_up=lambda instance, x: self.onSliderChange())
        self.add_widget(self.leds_brightnessSlider)

        self.btn_color_choose = BetterButton(text="Choose Color", size_hint_y=0.5)
        self.btn_color_choose.bind(on_press=self.choose_color)
        self.add_widget(self.btn_color_choose)

        self.create_color_buttons()

        self.btn_led_off = BetterButton(text="Off", size_hint_y=None)
        self.btn_led_off.bind(on_press=lambda instance: self.set_led_color((0,0,0,1)))
        self.add_widget(self.btn_led_off)

    def create_color_buttons(self):
        colorsGrid = GridLayout()
        colorsGrid.rows=2
        colorsGrid.size_hint_y=1
        colors = [("White", (1, 1, 1, 1)),
                  ("Red", (1, 0, 0, 1)),
                  ("Green", (0, 1, 0, 1)),
                  ("Blue", (0, 0, 1, 1))]
        for text, color in colors:
            btn = BetterButton(text=text, bkColor=color, textColor=THEME["textColor2"], size_hint_y=1)
            btn.bind(on_press=lambda instance, c=color: self.set_led_color(c))
            colorsGrid.add_widget(btn)
        self.add_widget(colorsGrid)

    def choose_color(self, instance):
        color_picker = ColorPicker()
        color_picker.bind(color=lambda instance, value: self.set_led_color(value))
        popup = Popup(title='Choose Color', content=color_picker, size_hint=(0.9, 0.9))
        popup.open()

    def on_color(self, instance, color):
        color_int = (int(color[0] * 255), int(color[1] * 255), int(color[2] * 255))
        self.set_led_color(color_int)
    
    def onSliderChange(self):
        self.brightness = self.leds_brightnessSlider.value / 100
        if self.currentColor != None:
            self.set_led_color(self.currentColor)

    def set_led_color(self, color):
        self.currentColor = color
        color = (int(color[0] * 255), int(color[1] * 255), int(color[2] * 255))
        color = tuple(int(c * self.brightness) for c in color)
        self.leds.ledsColor(color)

    def stop(self):
        pass
