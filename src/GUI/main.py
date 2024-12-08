import os
import json

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from kivy.uix.textinput import TextInput

from modules.THEME import THEME
from modules import lights
from modules import leds
from modules import streamDisplay
from modules import adminPage
from modules import logger
from modules import databaseViewer
from modules import mainPage
from modules.betterButton import BetterButton

class RoomControllerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = 'Room Controller'

        baseDir = os.path.dirname(os.path.abspath(__file__))
        self.settingsFilePath = os.path.join(baseDir, "settings.json")
        with open(self.settingsFilePath, "r") as f:
            self.settings = json.load(f)
        self.ip = self.settings["mqtt"]["ip"]
        self.port = self.settings["mqtt"]["port"]
        self.password = self.settings["GUI"]["password"]
        firstInstall = self.settings["GUI"]["firstInstall"]

        self.lastWidget = None

        # Admin button click tracking
        self.adminClickCounter = 0
        self.adminClickTimer = None

        if firstInstall:
            Clock.schedule_once(self.showInitialSetupPopup, 0.5)
        Clock.schedule_once(lambda dt: self.switchWidget(self.mainGroup), 0.5)

    def buildPermApps(self):
        self.mainGroup = mainPage.UnifiedControl(self.ip, port=self.port, spacing=10, padding=10)
        self.lightsGroup = lights.LightsGroup(self.ip, port=self.port, spacing=10, padding=10)
        self.ledsGroup = leds.LedsGroup(self.ip, port=self.port, spacing=10, padding=10)
        self.logger = logger.Logger(self.ip, self.port, size_hint=(1, 1))

    def build(self):
        mainAnchor = AnchorLayout(anchor_y='top')  # Use AnchorLayout to anchor widgets to the top
        mainLayout = BoxLayout(orientation='horizontal', spacing=10, padding=10)
        mainLayout.background_color = THEME["background"]

        with mainLayout.canvas.before:

            Color(*THEME["background"])               #< Set background color
            self.rect = Rectangle(size=mainLayout.size, pos=mainLayout.pos)
            mainLayout.bind(size=self.updateRect, pos=self.updateRect)

        # Sidebar for selecting which widget to display
        sidebar = BoxLayout(orientation='vertical', size_hint=(0.25, 1), padding=10)

        # Create a vertical BoxLayout inside AnchorLayout to arrange buttons from top to bottom
        buttonBox = BoxLayout(orientation='vertical', spacing=5)
        self.buildPermApps()
        # buttonBox.bind(minimum_height=buttonBox.setter('height'))  # Adjust height based on content

        # Lights button with an icon
        mainButton = BetterButton(text="Main", bkColor=THEME["primarySide"], padding=(0, 20, 0, 20), size_hint_y=1)
        lightsButton = BetterButton(text="Lights", bkColor=THEME["primarySide"], padding=(0, 20, 0, 20), size_hint_y=1)
        ledsButton = BetterButton(text="LEDs", bkColor=THEME["primarySide"], padding=(0, 20, 0, 20), size_hint_y=1)
        adminButton = BetterButton(text="Admin", bkColor=THEME["primarySide"], padding=(0, 20, 0, 20), size_hint_y=1)

        # Bind buttons to switch widgets
        mainButton.bind(on_press=lambda instance: self.switchWidget(self.mainGroup))
        lightsButton.bind(on_press=lambda instance: self.switchWidget(self.lightsGroup))
        ledsButton.bind(on_press=lambda instance: self.switchWidget(self.ledsGroup))
        adminButton.bind(on_press=self.handleAdminButtonClick)

        # Add buttons to button box and add button box to button layout
        buttonBox.add_widget(mainButton)
        buttonBox.add_widget(lightsButton)
        buttonBox.add_widget(ledsButton)
        buttonBox.add_widget(adminButton)
        sidebar.add_widget(buttonBox)

        # Main display area for widget selection
        self.displayArea = BoxLayout(size_hint=(0.8, 1))
        self.displayArea.background_color = THEME["background"]

        # Add sidebar and display area to main layout
        mainLayout.add_widget(sidebar)
        mainLayout.add_widget(self.displayArea)

        # self.switchWidget(self.mainGroup)
        mainAnchor.add_widget(mainLayout)

        return mainAnchor

    def showInitialSetupPopup(self, dt):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        ipInput = TextInput(hint_text="MQTT Broker IP", multiline=False)
        ipInput.text = self.ip
        portInput = TextInput(hint_text="MQTT Broker Port", multiline=False, input_filter="int")
        portInput.text = str(self.port)
        passwordInput = TextInput(hint_text="Admin Password", multiline=False, password=True)
        passwordInput.text = self.password

        content.add_widget(Label(text="Setup MQTT and Admin Password"))
        content.add_widget(ipInput)
        content.add_widget(portInput)
        content.add_widget(passwordInput)

        submitButton = Button(text="Submit", size_hint_x=1, size_hint_min_y=50)
        content.add_widget(submitButton)

        popup = Popup(title="Initial Setup", content=content, size_hint=(0.8, 0.5))
        submitButton.bind(on_press=lambda _: self.saveInitialSettings(ipInput.text, portInput.text, passwordInput.text, popup))
        popup.open()

    def saveInitialSettings(self, ip, port, password, popup):
        # Validate inputs
        if not ip or not port or not password:
            popup.title = "All fields are required!"
            return

        try:
            self.settings["mqtt"]["ip"] = ip
            self.settings["mqtt"]["port"] = int(port)
            self.settings["GUI"]["password"] = password
            self.settings["GUI"]["firstInstall"] = False

            with open(self.settingsFilePath, "w") as f:
                json.dump(self.settings, f, indent=4)

            # Update instance variables
            self.ip = ip
            self.port = int(port)
            self.password = password

            self.buildPermApps()
            self.switchWidget(self.mainGroup)

            popup.dismiss()

        except Exception as e:
            popup.title = f"Error: {e}"

    def handleAdminButtonClick(self, instance):
        self.adminClickCounter += 1

        # Cancel any existing timer
        if self.adminClickTimer:
            self.adminClickTimer.cancel()

        # Schedule a reset if clicks don't complete within 0.5 seconds
        self.adminClickTimer = Clock.schedule_once(self.adminConseqFail, 0.5)

        # Check if the counter has reached 5
        if self.adminClickCounter >= 5:
            self.adminClickTimer.cancel()  # Cancel the reset timer
            self.adminClickCounter = 0    # Reset the counter
            self.switchWidget(self.createAdminPage())  # Bypass login

    def adminConseqFail(self, dt):
        # Reset the counter if time elapsed
        self.adminClickCounter = 0
        self.showPasswordPrompt()

    def createAdminPage(self):
        page = adminPage.AdminPage()
        page.addFunc(lambda: self.showInitialSetupPopup(None), "Update Settings")
        page.addPage(lambda: self.mainGroup, "Main Page")
        page.addPage(lambda: self.lightsGroup, "Lights")
        page.addPage(lambda: self.ledsGroup, "Leds")
        page.addPage(lambda: self.logger, "Logger")
        page.addPage(lambda: streamDisplay.StreamDisplay(self.ip, self.port, size_hint=(1, 1)), "Camera")
        page.addPage(lambda: databaseViewer.DatabaseViewer(self.ip, self.port, size_hint=(1, 1)), "Database Viewer")
        return page

    def showPasswordPrompt(self):
        # Original password prompt logic here...
        passwordInput = TextInput(password=True, multiline=False)
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text="Enter Password"))
        content.add_widget(passwordInput)
        button = Button(text="Submit")
        content.add_widget(button)
        
        popup = Popup(title='Password Required', content=content, size_hint=(0.5, 0.3))
        button.bind(on_press=lambda x: self.validatePassword(passwordInput.text, popup))
        passwordInput.bind(on_text_validate=lambda x: self.validatePassword(passwordInput.text, popup))
        
        popup.open()

    def validatePassword(self, password, popup):
        if password == self.password:
            popup.dismiss()
            self.switchWidget(self.createAdminPage())
        else:
            popup.title = "Invalid Password. Try Again."

    def switchWidget(self, widget):
        # Clear the current widget in the display area and add the new one
        try:
            if self.lastWidget != None:
                self.lastWidget.stop()
        except:
            pass

        self.lastWidget = widget
        self.displayArea.clear_widgets()
        self.displayArea.add_widget(widget)

    def updateRect(self, *args):
        self.rect.size = self.root.size
        self.rect.pos = self.root.pos

    def run(self):
        super().run()

if __name__ == "__main__":
    RoomControllerApp().run()