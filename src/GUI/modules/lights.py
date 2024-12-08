import modules.mqttCommunication as communication
from modules.THEME import THEME

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.clock import Clock
from kivy.uix.slider import Slider

from modules.betterButton import BetterButton

class Lights:
    def __init__(self, ip, port, topic="smartRoom/generic/output"):
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

    def lightsOn(self):
        self.publish(self.topic, "lightsOn")

    def lightsOff(self):
        self.publish(self.topic, "lightsOff")

    def lightsUp(self):
        self.publish(self.topic, "lightsUp")

    def lightsDown(self):
        self.publish(self.topic, "lightsDown")

    def lightsSet(self, value):
        self.publish(self.topic, f"lightsSet {value}")

class LightsGroup(BoxLayout):
    def __init__(self, ip, port=1883, topic="smartRoom/generic/output", **kwargs):
        super().__init__(**kwargs)
        self.background_color = THEME["background"]
        self.orientation = 'vertical'
        self.lights = Lights(ip, port, topic)
        self.up_event = None
        self.down_event = None
        self.brightness = 1
        self.brightnessSliderDown = None

        # AnchorLayout to ensure content starts from the top
        top_layout = AnchorLayout(anchor_y='top')

        # BoxLayout for lights buttons, arranged vertically
        button_box = BoxLayout(orientation='vertical', spacing=10)
        button_box.bind(minimum_height=button_box.setter('height'))  # Adjust height based on content

        self.brightnessSlider = Slider(min=0, max=100, value=100, size_hint_y=1)
        self.brightnessSlider.bind(on_touch_down=self.start_onSliderChange)
        self.brightnessSlider.bind(on_touch_up=lambda instance, x: self.stop_onSliderChange())

        # On button
        self.btn_lights_on = BetterButton(text="On", padding=(0, 20, 0, 20), size_hint_y=0.7)
        # self.btn_lights_on.bind(on_press=lambda instance: self.lights.lightsOn())
        self.btn_lights_on.bind(on_press=lambda instance: self.sliderSet(100))

        # Off button
        self.btn_lights_off = BetterButton(text="Off", padding=(0, 20, 0, 20), size_hint_y=0.7)
        self.btn_lights_off.bind(on_press=lambda instance: self.sliderSet(0))

        button_box.add_widget(self.btn_lights_on)
        button_box.add_widget(self.brightnessSlider)
        button_box.add_widget(self.btn_lights_off)

        # Add the button_box to the top_layout and add it to the main layout
        top_layout.add_widget(button_box)
        self.add_widget(top_layout)

    def start_onSliderChange(self, slider, touch):
        self.stop_onSliderChange()
        if slider.collide_point(*touch.pos):
            Clock.schedule_once(lambda dt: self.lights.lightsSet(int(self.brightnessSlider.value)))
            self.brightnessSliderDown = Clock.schedule_interval(lambda dt: self.lights.lightsSet(int(self.brightnessSlider.value)), 0.1)

    def stop_onSliderChange(self):
        if self.brightnessSliderDown != None:
            self.brightnessSliderDown.cancel()
            self.brightnessSliderDown = None

    def sliderSet(self, value):
        self.brightnessSlider.value = int(value)
        self.lights.lightsSet(int(self.brightnessSlider.value))

    def stop(self):
        self.stop_onSliderChange()
