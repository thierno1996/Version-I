import os
import shutil
from PyPDF2 import PdfReader
from kivy import platform
from kivy.uix.label import Label
from kivymd.app import MDApp
import DataBaseClasses
from DataBaseClasses import SQLiteDatabase
from kivy.uix.popup import Popup
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
# from kivy.resources import resource_find
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.behaviors import FocusBehavior
from kivy.properties import BooleanProperty
from kivy.clock import Clock
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput

database = DataBaseClasses.SQLiteDatabase('SmallStore.db')


# select_method_result = sorted(database.select("product_table", ["product_name"]))


class ScreenThree(MDScreen):
    def __init__(self, **kwargs):
        super(ScreenThree, self).__init__(**kwargs)
        app = MDApp.get_running_app()
        self.database_path = app.get_database_path()
        self.columns = ["product_name", "buying_price", "selling_price", "quantity", "info"]
        self.dialog = None
        self.window = Popup(title="", background_color=(0, 0, 0, .1), separator_color=(0, 0, 0, 0),
                            content=RVForScreenThree(),
                            size_hint_y=None, height="300dp",
                            pos_hint={"center_x": .5})
        self.window.bind(on_dismiss=self.pop_up_clear)

    def pop_up_clear(self, dt):
        self.ids.popup_controller_screen3.text = ""

    def on_enter(self, threshold=5, *args):
        # Clock.schedule_once(self.change_toolbar, .2)
        self.clear_inputs()
        db = SQLiteDatabase(self.database_path)
        columns = ["product_name", "quantity"]
        where_clause = f"CAST(quantity as INTEGER) < {threshold}"
        rows = db.select("product_table", columns, where_clause)
        message = ""
        for row in rows:
            product_name = row[0]
            quantity = row[1]
            if quantity == 0:
                message += f"{product_name} est en rupture de stock\n"
            else:
                message += f"{product_name} a peu de stock({quantity} rest)\n"
        if message:
            popup = Popup(title="  ", content=Label(text=message), background_color=(1, 0, 0, 1),
                          separator_color=(1, 0, 0, 1))
            popup.open()

    def show_alert_dialog(self, name):
        if not self.dialog:
            self.dialog = MDDialog(
                text=f"le prix de vante de {name} est presque le double du prix d'achat \n \n vous voudrez peut-être le mettre à jour",
                buttons=[
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=(1, 0, 0, 1),
                        on_press=self.on_yes_button_pressed
                    ),

                ],
            )
        self.dialog.open()

    def delete_non_barcode_items(self):
        if not self.dialog:
            self.dialog = MDDialog(
                text=f"êtes-vous sûr de vouloir supprimer tous \n les éléments alphabétiques",
                buttons=[
                    MDFlatButton(
                        text="Oui",
                        theme_text_color="Custom",
                        text_color=(1, 0, 0, 1),
                        on_press=self.on_yes_delete

                    ),
                    MDFlatButton(text="Non", theme_text_color="Custom", text_color=(0, 0, 0, 1),
                                 on_press=self.on_yes_button_pressed)
                ],
            )
        self.dialog.open()

    def on_yes_button_pressed(self, instance):
        self.dialog.dismiss()
        self.dialog = None

    def on_yes_delete(self, *args):
        rows = DataBaseClasses.SQLiteDatabase(self.database_path).select("product_table", self.columns)
        for row in rows:
            item = row[0]
            if item[0].isalpha():
                print(item)
                DataBaseClasses.SQLiteDatabase(self.database_path).delete("product_table",
                                                                          f"{self.columns[0]} = '{item}'")
            self.dialog.dismiss()
            self.ids.notification.text = "tous les éléments alphabétiques ont été supprimés"
        self.dialog = None

    def clear_inputs(self):
        for child in self.ids.Screen_three_box_layout.children:
            if isinstance(child, MDTextField):
                child.text = ""
        self.ids.text_input_for_product.text = ""
        self.ids.text_input_for_info.text = "Info"

    def change_toolbar(self, *args):
        toolbar = self.ids.toolbar_for_screen_three
        toolbar.switch_tab("third_screen")

    def on_pre_enter(self, *args):
        Clock.schedule_once(self.change_toolbar, .1)
        self.ids.notification1.text = ""
        self.ids.notification.text = ""

        # self.change_toolbar()

    def upload_button(self):
        # Get the values entered by the user
        new_values = [
            self.ids.text_input_for_product.text.strip(),
            self.ids.text_input_for_buying_price.text.replace(",", "."),
            self.ids.text_input_for_selling_price.text.replace(",", "."),
            self.ids.text_input_for_quantity.text,
            self.ids.text_input_for_info.text
        ]

        # Check if all fields are filled
        if self.ids.text_input_for_product.text == "" or self.ids.text_input_for_selling_price.text == "" or self.ids.text_input_for_quantity.text == "" or self.ids.text_input_for_buying_price.text == "":
            self.ids.notification1.text = "veuillez remplir les champs obligatoire"
            return
        if float(self.ids.text_input_for_buying_price.text.replace(",", ".")) >= float(
                self.ids.text_input_for_selling_price.text.replace(",", ".")):
            self.ids.notification1.text = "le prix d'achat ne peut être supérieur au prix de vente"
            return
        result = float(self.ids.text_input_for_selling_price.text.replace(",", ".")) - float(
            self.ids.text_input_for_buying_price.text.replace(",", "."))
        if result >= float(self.ids.text_input_for_buying_price.text.replace(",", ".")) / 2:
            self.show_alert_dialog(self.ids.text_input_for_product.text.upper())

        # Check if the product already exists in the database
        product_name = new_values[0]
        db = SQLiteDatabase(self.database_path)
        rows = db.select("product_table", "*", f"product_name = '{product_name.upper()}'")

        if len(rows) > 0:
            self.ids.text_input_for_info.color = (1, 0, 0, 1)
            self.ids.notification1.text = f"Le produit '{product_name}' existe déjà dans la base de données"
            return

        # Insert the new product into the database
        db.insert("product_table", new_values)
        self.clear_inputs()

    def update_values(self):
        # Get the values entered by the user
        new_values = [
            self.ids.text_input_for_product.text.strip(),
            self.ids.text_input_for_buying_price.text.replace(",", "."),
            self.ids.text_input_for_selling_price.text.replace(",", "."),
            self.ids.text_input_for_quantity.text,
            self.ids.text_input_for_info.text
        ]

        # Check for null values
        """if None in new_values:
            self.ids.notification1.text = "Une ou plusieurs valeurs manquent"
            return"""

        # Check if all fields are filled
        if self.ids.text_input_for_product.text == "" or self.ids.text_input_for_selling_price.text == "" or self.ids.text_input_for_quantity.text == "" or self.ids.text_input_for_buying_price.text == "":
            self.ids.notification1.text = "veuillez remplir les champs opligatoire"
            return
        if float(self.ids.text_input_for_buying_price.text.replace(",", ".")) >= float(
                self.ids.text_input_for_selling_price.text.replace(",", ".")):
            self.ids.notification1.text = "le prix d'achat ne peut être supérieur au prix de vente"
            return
        result = float(self.ids.text_input_for_selling_price.text.replace(",", ".")) - float(
            self.ids.text_input_for_buying_price.text.replace(",", "."))
        if result >= float(self.ids.text_input_for_buying_price.text.replace(",", ".")) / 2:
            self.show_alert_dialog(self.ids.text_input_for_product.text.upper())

        # Combine the column names and new values into a dictionary
        update_dict = dict(zip(self.columns, new_values))

        # Define the update condition
        condition = f"{self.columns[0]} = '{new_values[0]}'"

        # Update the row in the database
        db = SQLiteDatabase(self.database_path)
        success = db.update("product_table", update_dict, condition)
        if success:
            self.ids.notification1.text = "Mise à jour réussie"
            self.clear_inputs()
        else:
            self.ids.notification1.text = "Mise à jour a échoué"

    def create_qr_file(self):
        import qrcode
        input_text = self.ids.text_input_for_product.text.strip().upper()
        if not input_text.isdigit():
            try:
                qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=3, border=4)
                qr.add_data(input_text)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                img.save(f"{input_text}.png")
                self.ids.notification.text = "Code QR créé avec succès."
            except Exception as e:
                self.ids.notification.text = f"{e}"
        else:
            self.ids.notification.text = "Le texte saisi ne contient que des chiffres. Code QR non créé."

    def insert_pdf_data_to_db(self):
        if platform == "android":
            from androidstorage4kivy import SharedStorage
            from android import autoclass
            Environment = autoclass('android.os.Environment')
            result = SharedStorage().copy_from_shared(os.path.join(Environment.DIRECTORY_DOCUMENTS,
                                                                              'factures', 'products.pdf'))
            print("the path to result", result)
            if result:
                private_file_path = result
                self.ids.notification.text = str(result)
            else:
                private_file_path = "products.pdf"

        else:
            private_file_path = r"C:\Users\Projects\products.pdf"

        db = DataBaseClasses.SQLiteDatabase(self.database_path)
        db.create_table("product_table", ["product_name", "buying_price", "selling_price", "quantity", "info"])
        try:
            with open(private_file_path, 'rb') as f:
                pdf_reader = PdfReader(f)
                content = pdf_reader.pages[5].extract_text()
                first_list = content.split('\n')
                second_list = first_list[5:]
                new_list = [item for item in second_list if item not in ['product_name', 'buying_price', 'selling_price', 'quantity', 'info']]
                list_of_grouped_items = [second_list[i:i + 5] for i in range(0, len(second_list), 5)]
                print(list_of_grouped_items)  # check the contents of list_of_grouped_items
                for data in list_of_grouped_items:
                    try:
                        # check if item already exists in database
                        if not db.select("product_table", "*", f"product_name='{data[0]}'"):
                            # if len(data) < 5:
                            # data.append("Store_checking")
                            # print(data)
                            values = [data[0], data[1], data[2], data[3], data[4]]
                            # check the values to be inserted
                            db.insert("product_table", values)
                    except Exception as e:
                        print(e)
                        continue
                self.ids.notification.text = first_list[0]
        except Exception as e:
            print(e)
            #self.ids.notification.text = str(e)

    def copy_file_to_internal_storage(self):
        from jnius import autoclass, cast
        if platform == 'android':
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Environment = autoclass('android.os.Environment')
            Intent = autoclass('android.content.Intent')
            Settings = autoclass('android.provider.Settings')
            Uri = autoclass('android.net.Uri')

            source_file = '/sdcard/documents/factures/products.pdf'  # Replace with the actual source file path
            destination_folder = './products.pdf'  # Replace with the destination folder path

            # Create the destination folder if it doesn't exist
            os.makedirs(destination_folder, exist_ok=True)

            # Check if the app has permission to access external storage
            if Environment.isExternalStorageManager():
                # Copy the file from source to destination
                shutil.copy(source_file, destination_folder)

                # Check if the file was successfully copied
                if os.path.exists(destination_folder):
                    print("File copied successfully.")
                else:
                    print("File copy failed.")
            else:
                try:
                    activity = PythonActivity.mActivity.getApplicationContext()
                    uri = Uri.parse("package:" + activity.getPackageName())
                    intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION, uri)
                    currentActivity = cast("android.app.Activity", PythonActivity.mActivity)
                    currentActivity.startActivityForResult(intent, 101)
                except:
                    intent = Intent()
                    intent.setAction(Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION)
                    currentActivity = cast("android.app.Activity", PythonActivity.mActivity)
                    currentActivity.startActivityForResult(intent, 101)
            return destination_folder

    # Call the function to copy the file and request permission if needed

    def go_to_screen_two(self):
        self.manager.current = "second_screen"
        self.manager.transition.direction = 'left'

    def go_to_screen_three(self):
        self.manager.current = "third_screen"
        self.manager.transition.direction = 'left'

    def go_to_screen_one(self):
        self.manager.current = "main_screen"
        self.manager.transition.direction = 'left'

    def check_permission(self):
        if platform == 'android':
            from android.permissions import request_permissions, Permission

            def callback(permission, result):
                if all([res for res in result]):
                    result_of_permissions = "J'ai toutes les autorisations"
                    self.ids.notification.text = result_of_permissions
                else:
                    result_of_permissions = "Je n'ai pas obtenu toutes les autorisations"
                    self.ids.notification.text = result_of_permissions

            request_permissions(
                [Permission.CAMERA, Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE],
                callback)


class NoSpaceTextField(MDTextField):
    def __init__(self, **kwargs):
        super(NoSpaceTextField, self).__init__(**kwargs)
        app = MDApp.get_running_app()
        self.database_path = app.get_database_path()

    def insert_text(self, substring, from_undo=False):
        # Convert uppercase letters to lowercase
        substring = substring.lower()

        # Filter out non-lowercase letters
        filtered_substring = ''.join(c for c in substring if c.islower() or c.isspace())

        # Call the original insert_text method with the modified substring
        super(NoSpaceTextField, self).insert_text(filtered_substring, from_undo=from_undo)

    def on_text_validate(self):
        app = MDApp.get_running_app().root.get_screen("third_screen")
        root = app
        columns = ["product_name", "buying_price", "selling_price", "quantity", "info"]
        rows = SQLiteDatabase(self.database_path).select("product_table", columns,
                                                         f"{columns[0]} = '{root.ids.text_input_for_product.text}'")
        if len(rows) > 0:
            root.ids.text_input_for_buying_price.text = str(rows[0][1]).replace(".", ",")
            root.ids.text_input_for_selling_price.text = str(rows[0][2]).replace(".", ",")
            root.ids.text_input_for_quantity.text = str(rows[0][3])
            root.ids.text_input_for_info.text = str(rows[0][4])
            root.ids.notification1.text = f"Le produit {root.ids.text_input_for_product.text.upper()} existe déjà " \
                                          f"dans la base de données"
            return


class DigitTextField(MDTextField):
    def insert_text(self, substring, from_undo=False):
        allowed_chars = "1234567890.,"
        digits = [char for char in substring if char in allowed_chars]
        return super().insert_text("".join(digits), from_undo=from_undo)


class Quantity(MDTextField):
    def insert_text(self, substring, from_undo=False):
        allowed_chars = "1234567890"
        digits = [char for char in substring if char in allowed_chars]
        return super().insert_text("".join(digits), from_undo=from_undo)


class RVForScreenThree(RecycleView):
    def __init__(self, **kwargs):
        super(RVForScreenThree, self).__init__(**kwargs)
        app = MDApp.get_running_app()
        self.database_path = app.get_database_path()
        self.data = []

    def update_data(self, text=''):
        data_base_file = DataBaseClasses.SQLiteDatabase(self.database_path)
        result = sorted(data_base_file.select("product_table", ["product_name"]))
        original_data = [x[0] for x in result]
        filtered_data = [item for item in original_data if item[:len(text)].lower() == text.lower()]
        self.data = [{'text': str(x)} for x in filtered_data]
        self.refresh_from_data()


class SelectableRecycleBoxLayout3(FocusBehavior, LayoutSelectionBehavior,
                                  RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''

    def clear_selection(self, *args):
        ''' Deselects all the currently selected nodes.
        '''
        deselect = self.deselect_node
        nodes = self.selected_nodes
        for node in nodes[:]:
            deselect(node)


class SelectableLabel3(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableLabel3, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableLabel3, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        app = MDApp.get_running_app().root.get_screen("third_screen")
        root = app
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if self.selected:
            text = rv.data[index]["text"]
            root.ids.text_input_for_product.text = text
            root.ids.text_input_for_product.focus = True
            root.ids.popup_controller_screen3.text = ""
            root.window.content.ids.controller.clear_selection()
            root.window.dismiss()
