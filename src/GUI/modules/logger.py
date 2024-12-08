from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.uix.textinput import TextInput

import modules.mqttCommunication as communication

class Logger(ScrollView):
    def __init__(self, ip, port=1883, logTopic="smartRoom/logger", **kwargs):
        super().__init__(**kwargs)
        
        self.text_area = TextInput(size_hint=(1, None), height=2000, multiline=True, readonly=True, font_size=14, background_color=(0, 0, 0, 0), foreground_color=(1, 1, 1, 1))
        self.add_widget(self.text_area)

        try:
            self.com = communication.COM(ip, port)
            self.com.connect()
            self.com.subscribe(logTopic)
            self.com.changeOnPacket(self._onPacket)
            self.com.loop_start()
        except:
            pass

    def _onPacket(self, msg, topic):
        self.append_text(msg)

    def append_text(self, text):
        # This ensures the text update happens in the main thread
        Clock.schedule_once(lambda dt: self._update_text(text))

    def _update_text(self, text):
        self.text_area.text += text + "\n"
        self.text_area.scroll_y = 1

    def stop(self):
        pass
        # self.com.loop_stop()
