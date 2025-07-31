import socketio
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window

from kivymd.app import MDApp

from login import LoginScreen
from mainscreen import MainScreen

# Taille pour test
Window.size = (900, 600)

sio = socketio.Client()
class MainApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        sio.connect("http://127.0.0.1:5001")

        # Chargement des fichiers .kv
        Builder.load_file("loginscreen.kv")
        Builder.load_file("mainscreen.kv")

        @sio.on("of_lance")
        def of_lance_handler(data):
            print("offff recuuuuuu")
        # Chargement du screenmanager défini dans main.kv

        @sio.on("workers_absence")
        def of_lance_handler(data):
            print("workerrrrrr recuuuuuu")

        # Chargement du screenmanager défini dans main.kv
        return Builder.load_file("main.kv")

if __name__ == "__main__":
    MainApp().run()
