from datetime import datetime, date

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


class DoneOF(MDScreen):
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
        aujourd_hui = date.today()
        self.ids.date_id.text = aujourd_hui.strftime("%d/%m/%Y")
        self.update_table()

    def create_data_table(self, dt=None):
        if self.data_table is None:
            self.data_table = MDDataTable(
                size_hint=(1, None),
                height=dp(400),# Hauteur fixe initiale
                check=True,
                column_data=[
                    ("numOF", dp(30)),
                    ("Pointure", dp(30)),
                    ("Quantite", dp(30)),
                    ("Etat", dp(30)),
                    ("SAIS", dp(30)),
                    ("Date lancement", dp(30)),
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
    def checked(self, instance_table,current_row):
        session = SessionManager.get_instance()
        print(instance_table,current_row)
        print(current_row)
        data = {
            "numOF": current_row[0],
            "chaine": session.get_role()
        }
        if data in self.checked_rows:
            self.checked_rows.remove(data)
        else:
            self.checked_rows.append(data)
    def row_checked(self, instance_table,instance_row):
        print(instance_table,instance_row)

    def update_table(self):
        self.data_table.row_data=[]
        data={
            "date":self.ids.date_id.text,
        }
        response = make_request("get", "/manage_ofs/get_ofs_termine_by_chaine_and_doneDate",json=data)

        if response.status_code == 200:  # Utilisez status_code au lieu de response.json()[1]
            try:
                response_data = response.json()[0]['ofs']
                print(response_data)
                if response_data:
                    if isinstance(response_data, list):
                        # Préparation des données
                        row_data = [
                            (
                                str(item.get("numCommandeOF", "")),
                                str(item.get("Pointure", "")),
                                str(item.get("Quantite", "")),
                                str(item.get("etat", "")),
                                str(item.get("SAIS", "")),
                                str(item.get("dateLancement_of_chaine","")),
                            )
                            for item in response_data
                        ]

                        # Mise à jour de la table
                        self.data_table.row_data = row_data

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
                else:
                    print(self.ids.date_id.text)
                    self.show_alert_dialog("Vous n'avez pas de of terminéé pour cette date","Malheureusement")
                    return
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
    def show_date_picker(self):

        aujourd_hui = date.today()

        date_dialog=MDDatePicker(year=aujourd_hui.year,month=aujourd_hui.month,day=aujourd_hui.day)
        date_dialog.bind(on_save=self.on_saveDate,on_cancel=self.on_cancelDate)
        date_dialog.open()
    def on_saveDate(self,instance,value,date_range):
        print(instance,value,date_range)
        self.ids.date_id.text = value.strftime("%d/%m/%Y")
        self.update_table()

    def on_cancelDate(self,instance,value):
        pass
