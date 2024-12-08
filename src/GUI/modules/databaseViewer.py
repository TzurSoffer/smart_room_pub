from kivy.uix.treeview import TreeView, TreeViewLabel
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock

import time
import datetime
import threading

import modules.mqttCommunication as communication

class DatabaseViewer(BoxLayout):
    def __init__(self, ip, port=1883, databaseTopic="smartRoom/database/#", **kwargs):
        super().__init__(**kwargs)
        self.run = True
        self.databaseNodes = {}

        self.mainTree = TreeView(
                        size_hint=(1, 1),
                        root_options=dict(text='DataBase Values'),
                        hide_root=False,
                        indent_level=10)

        self.widget = self.add_widget(self.mainTree)

        try:
            self.com = communication.COM(ip, port)
            self.com.connect()
            self.com.subscribe(databaseTopic)
            self.com.changeOnPacket(self._onPacket)
            threading.Thread(target=self.mqttLoop_thread).start()
        except:
            pass
    
    def mqttLoop_thread(self):
        while self.run:
            self.com.loop()
            time.sleep(.05)
        self.com.disconnect()

    def _onPacket(self, msg, topic):
        if topic == "smartRoom/database/input" or topic == "smartRoom/database/getData":
            return()
        Clock.schedule_once(lambda dt: self.updateViewer(topic.split("/")[-1], str(msg["data"])))

    def updateViewer(self, name, value):
        settings = {"value": value, "updateTime": datetime.datetime.strftime(datetime.datetime.now(), "%H:%M:%S")}
        isOpen = False
        if name in list(self.databaseNodes.keys()):
            isOpen = self.databaseNodes[name].is_open
            self.mainTree.remove_node(self.databaseNodes[name])

        valueShortened = settings["value"][:10]
        node = TreeViewLabel(text=f"{name}: {valueShortened}", is_open=isOpen)
        node = self.mainTree.add_node(node)
        for innerName, innerValue in settings.items():
            self.mainTree.add_node(TreeViewLabel(text=f"{innerName}: {innerValue[:99]}", is_open=False), parent=node)
        self.databaseNodes[name] = node

    def stop(self):
        self.run = False