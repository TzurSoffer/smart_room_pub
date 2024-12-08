from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from modules.betterButton import BetterButton

class AdminPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rows = 2  # One row for top bar, one row for display area
        self.lastWidget = None

        # Top bar with back button
        self.topBar = BoxLayout(size_hint_y=0.1)
        self.backButton = BetterButton(bkColor=(0.5, 0.5, 0.5), text="Back", size_hint_x=None, size_hint_y=0.9, width=100)  # Smaller back button
        self.backButton.bind(on_press=self.on_back_button)
        self.topBar.add_widget(self.backButton)
        self.add_widget(self.topBar)

        # Display area to hold the grid of buttons
        self.displayArea = BoxLayout(size_hint_y=0.9)
        self.add_widget(self.displayArea)

        # Initialize aminPage as a GridLayout for button organization
        self.aminPage = GridLayout(cols=3, spacing=10, padding=10)
        self.displayArea.add_widget(self.aminPage)

    def on_back_button(self, instance):
        self.updateDisplayArea(self.aminPage)

    def addPage(self, callback, buttonText, buttonClass=BetterButton):
        self.addFunc(lambda : self.updateDisplayArea(callback()), buttonText, buttonClass)

    def addFunc(self, callback, buttonText, buttonClass=BetterButton):
        button = buttonClass(text=buttonText)
        button.bind(on_press=lambda instance: callback())
        self.aminPage.add_widget(button)  # Add buttons to the grid layout

    def updateDisplayArea(self, widget):
        if self.lastWidget != None:
            try:
                self.lastWidget.stop()
            except:
                pass
        self.lastWidget = widget

        self.displayArea.clear_widgets()
        self.displayArea.add_widget(widget)

    def stop(self):
        pass
