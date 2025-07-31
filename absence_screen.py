from datetime import datetime, date

from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivymd.material_resources import dp
from kivymd.uix.button import MDFlatButton, MDRectangleFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from kivymd.uix.datatables import MDDataTable
from SessionManager import SessionManager
from InterfacesChefs.client import make_request


class AbsenceScreen(MDScreen):
    dialog = None

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self.dialog1 = None
        self.modeles = []
        self.selected_model=""
        self.data_table = None
        self.checked_rows=[]
        Clock.schedule_once(lambda dt: self.create_data_table())
    def get_objectif_for_today(self,ofs):
        obj=""
        jours_fr = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

        # Obtenir le jour de la semaine sous forme d'entier (0 = Lundi, 6 = Dimanche)
        numero_jour = datetime.today().weekday()

        # Utiliser l'index pour obtenir le nom en français
        jour_aujourd_hui = jours_fr[numero_jour]
        match jour_aujourd_hui:
            case "Lundi":
                obj=ofs.get("nbPaireLundi")
            case "Mardi":
                obj=ofs.get("nbPaireMardi")
            case "Mercredi":
                obj=ofs.get("nbPaireMercredi")
            case "Jeudi":
                obj=ofs.get("nbPaireJeudi")
            case "Vendredi":
                obj=ofs.get("nbPaireVendredi")
            case "Samedi":
                obj=ofs.get("nbPaireSamedi")
        self.ids.objectif_id.text=f"votre objectif pour aujourd'hui est de {obj} paires"

    def on_enter(self, *args):
        self.get_absent_workers()
        self.update_table()
        Clock.schedule_once(self.refresh_checkboxes, 0.2)
    def create_data_table(self, dt=None):
        if self.data_table is None:
            self.data_table = MDDataTable(
                size_hint=(1, None),
                height=dp(400),# Hauteur fixe initiale
                check=True,
                column_data=[
                    ("matriule", dp(30)),
                    ("nom", dp(30)),
                    ("prenom", dp(30)),
                    ("absence", dp(30)),
                ],
                row_data=[],
                use_pagination=True,  # Activation de la pagination
                rows_num=10,  # Nombre de lignes par page
                pagination_menu_pos="auto",  # Position automatique du menu
                elevation=2  # Ombre pour meilleur visibilité
            )
            self.data_table.bind(on_check_press=self.checked)
            self.data_table.bind(on_row_press=self.row_checked)
            self.ids.table_container.add_widget(self.data_table)
    def get_absent_workers(self):
        response = make_request("get", "/manage_absence/get_absent_workers")

        if response.json()[1] == 200:
            data=response.json()[0].get("absentWorkers")
            if data:# Utilisez status_code au lieu de response.json()[1]
                self.checked_rows=[i["MATR"] for i in data]

    def checked(self, instance_table, current_row):
        session = SessionManager.get_instance()
        print(instance_table, current_row)
        if current_row[0] in self.checked_rows:
            self.checked_rows.remove(current_row[0])
            # Modifier la ligne pour enlever le marquage
            updated_status = "present"
            data_to_update={
                "matr": current_row[0],
                "absence":0,
            }
        else:
            self.checked_rows.append(current_row[0])
            # Modifier la ligne pour ajouter un marquage
            updated_status = "absent"
            data_to_update = {
                "matr": current_row[0],
                "absence": 1
            }
        # Mettre à jour la ligne dans row_data
        new_row_data = []
        for row in self.data_table.row_data:
            if row[0] == current_row[0]:  # même identifiant
                updated_row = (row[0], row[1], row[2], updated_status)
                new_row_data.append(updated_row)
            else:
                new_row_data.append(row)

        # Rafraîchir la table
        self.data_table.row_data = new_row_data
        self.update_presence_of_worker(data_to_update)
    def update_presence_of_worker(self,data):
        response = make_request("put", "/manage_absence/update_absence_worker",json=data)

        if response.json()[1] == 201:  # Utilisez status_code au lieu de response.json()[1]
            print("succes")


    def row_checked(self, instance_table,instance_row):
         print("aaaaa")
         print(instance_table,instance_row)



    def update_table(self):

        response = make_request("get", "/manage_absence/get_all_workers")

        if response.status_code == 200:  # Utilisez status_code au lieu de response.json()[1]
            try:

                self.response_data = response.json()[0]['workers']
                self.get_objectif_for_today(self.response_data[0])
                if isinstance(self.response_data, list):
                    # Préparation des données
                    row_data = [
                        (
                            str(item.get("MATR", "")),
                            str(item.get("NOM", "")),
                            str(item.get("PRENOM", "")),
                            "present" if int(item.get("ISABSENT", 1)) == 0 else "absent"

                        )
                        for item in self.response_data
                    ]
                    row_data.sort(key=lambda x: 0 if x[3] == "present" else 1,reverse=True)
                    # Mise à jour de la table
                    self.data_table.row_data = row_data
                    Clock.schedule_once(lambda dt: self.refresh_checkboxes(), 0.1)
                    # Ajustement dynamique de la pagination
                    if len(row_data) > 10:
                        self.data_table.page_size = 10  # Lignes par page
                        self.data_table.pagination_menu = True  # Active le menu
                    else:
                        # Ajuste la hauteur si peu de données
                        self.data_table.height = max(
                            len(row_data) * dp(50),  # 50dp par ligne
                            dp(400)  # Hauteur minimale
                        )
            except Exception as e:
                print(f"Error processing data: {e}")
    def show_alert_dialog(self,message,title):
        if not self.dialog1:
            # Créer d'abord le contenu du dialogue
            content = BoxLayout(orientation='vertical', spacing=12, size_hint_y=None)

            # Ajouter le texte
            content.add_widget(MDLabel(
                text=message,
                halign="center",
                theme_text_color="Secondary"
            ))
            # Créer le dialogue
            self.dialog1 = MDDialog(
                title=title,
                type="custom",
                content_cls=content,
                buttons=[
                    MDFlatButton(
                        text="CONFIRMER",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: self.dialog1.dismiss()
                    ),
                ],
                size_hint=(0.8, None)
            )

        self.dialog1.open()

    def filter_table(self, search_text):
        search_text = search_text.lower()

        if not hasattr(self, 'response_data'):
            return

        filtered_rows = [
            (
                str(item.get("MATR", "")),
                str(item.get("NOM", "")),
                str(item.get("PRENOM", "")),
                "present" if str(item.get("ISABSENT", "")) == "0" else "absent",
            )
            for item in self.response_data
            if search_text in str(item.get("NOM", "")).lower()
               or search_text in str(item.get("MATR", "")).lower()
        ]

        self.data_table.row_data = filtered_rows

        if len(filtered_rows) > 10:
            self.data_table.page_size = 10
            self.data_table.pagination_menu = True
        else:
            self.data_table.pagination_menu = False
            self.data_table.page_size = len(filtered_rows)

    def refresh_checkboxes(self, *args):
        try:
            # Inverser children car Kivy les place de bas en haut
            row_widgets = self.data_table.table_data.children[::-1]
            for i, row_widget in enumerate(row_widgets):
                matricule = self.data_table.row_data[i][0]

                # Trouver la case à cocher dans la ligne
                for child in row_widget.children:
                    if hasattr(child, "active"):  # C’est probablement la checkbox
                        child.active = matricule in self.checked_rows
                        break
        except Exception as e:
            print("Erreur dans refresh_checkboxes:", e)



