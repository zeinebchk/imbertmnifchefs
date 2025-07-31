from kivy.app import App
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager

from InterfacesChefs.SessionManager import SessionManager
from InterfacesChefs.absence_screen import AbsenceScreen
from InterfacesChefs.doneOF import DoneOF
from InterfacesChefs.launch_screen import LaunchScreen
from InterfacesChefs.login import LoginScreen
from inProgressOF import InProgressOF
Builder.load_file("launch_screen.kv")
Builder.load_file("inProgressOF.kv")
Builder.load_file("doneOF.kv")
Builder.load_file("absence_screen.kv")

class MainScreen(MDScreen):
    def go_to_in_progress_of(self):
        screen_manager = self.ids.screen_manager

        # Vérifie si l'écran est déjà présent
        if not screen_manager.has_screen("inProgressof"):
            screen = InProgressOF(name="inProgressof")
            screen_manager.add_widget(screen)

        screen_manager.current = "inProgressof"

    def go_to_done_of(self):
        screen_manager = self.ids.screen_manager

        # Vérifie si l'écran est déjà présent
        if not screen_manager.has_screen("doneof"):
            screen = DoneOF(name="doneof")
            screen_manager.add_widget(screen)

        screen_manager.current = "doneof"
    def go_to_absence(self):
        screen_manager = self.ids.screen_manager

        # Vérifie si l'écran est déjà présent
        if not screen_manager.has_screen("absence_screen"):
            screen = AbsenceScreen(name="absence_screen")
            screen_manager.add_widget(screen)

        screen_manager.current = "absence_screen"

    def on_logout(self):
        session = SessionManager().get_instance()
        session.set_tokens(None, None, None, None)

        print(session.get_access_token())
        print(session.get_refresh_token())

        # Obtenir le ScreenManager principal
        screen_manager = App.get_running_app().root

        # Ajouter login_screen s’il n’existe pas déjà
        if not screen_manager.has_screen("login_screen"):
            screen = LoginScreen(name="login_screen")
            screen_manager.add_widget(screen)

        # Rediriger vers login_screen
        screen_manager.current = "login_screen"