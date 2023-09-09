import os
from kivy import platform
from kivy.properties import BooleanProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
import DataBaseClasses
from kivymd.app import MDApp
from kivy.clock import Clock
import datetime

if platform == 'android':
    from android.storage import primary_external_storage_path

    path = os.path.join(primary_external_storage_path(), "Documents")
    try:
        directory = "MonMagasin"
        dir_path = os.path.join(path, directory)
        os.makedirs(dir_path)
    except Exception as e:
        print("the following error: ", e)

database = DataBaseClasses.SQLiteDatabase('SmallStore.db')
# info_about_products = [x[0] for x in sorted(database.select("product_table", ["product_name"]))]
# info_about_sales = sorted(database.select("sales_history", ["product_name", "sold_amount", "date"]),
# key=lambda x: x[0][0].isalpha(), reverse=True)

selected_items = []


class ScreenTwo(MDScreen):

    def __init__(self, **kwargs):
        super(ScreenTwo, self).__init__(**kwargs)
        app = MDApp.get_running_app()
        self.database_path = app.get_database_path()
        self.columns = ["product_name", "buying_price", "selling_price", "quantity", "info"]

        self.window = Popup(title="",
                            pos_hint={"center_y": 0.4},
                            content=RVForScreenTwo(),
                            background_color=(0, 0, 0, 0), separator_color=(0, 0, 0, 0))
        self.today = datetime.date.today().strftime('%d-%m-%Y')
        self.ids.time_variable.text = self.today

    def create_qr_file(self, list_of_items):
        import qrcode
        for item in list_of_items:
            if not item.isdigit():
                try:
                    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=3,
                                       border=4)
                    qr.add_data(item)
                    qr.make(fit=True)
                    img = qr.make_image(fill_color="black", back_color="white")
                    img.save(f"{item}.png")
                except Exception:
                    pass

    def display_products(self):

        products_display = sorted(DataBaseClasses.SQLiteDatabase(self.database_path).select("product_table", ["product_name"]), key=lambda x: x[0][0].isalpha(),
                                  reverse=True)
        view_table = self.ids.rv_for_screen_two
        view_table.data = [{'text': str(x[0])} for x in products_display]

    def search_for_match(self):
        rv = self.ids.rv_for_screen_two
        text = self.ids.match_items.text
        rv.update_data(text)

    def go_to_screen_two(self):
        self.manager.current = "second_screen"
        self.manager.transition.direction = 'right'

    def go_to_screen_three(self):
        self.manager.current = "third_screen"
        self.manager.transition.direction = 'right'

    def change_toolbar(self, *args):
        toolbar = self.ids.toolbar_for_screen_two
        toolbar.switch_tab("second_screen")

        """action_item = toolbar.ids.right_actions.children
        action_item[0].text_color = (0, 0, 0, .4)
        action_item[2].text_color = (0, 0, 0, .4)"""

    def on_pre_enter(self, *args):
        # Clock.schedule_once(self.change_toolbar, .1)
        self.change_toolbar()
        # self.ids.information.text = ""
        self.ids.selection.text = ""
        self.ids.total_for_today.text = ""
        self.ids.counter.text = ""

    def go_to_screen_one(self):
        self.manager.current = "main_screen"
        self.manager.transition.direction = 'right'

    def on_leave(self, *args):
        self.ids.rv_for_screen_two.data = []
        self.ids.selection.text = ""
        # self.ids.time_variable.text = ""

    def write_qrs_to_pdf(self, *args):
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.utils import ImageReader
        import shutil
        name = self.ids.categories.text
        selected_images = [x + ".png" for x in selected_items]

        if len(selected_images) <= 12:
            try:
                with open(name + ".pdf", "wb") as pdf:
                    c = canvas.Canvas(pdf, pagesize=letter)
                    img_x = 20
                    img_y = 20
                    img_width = 87
                    img_height = 87
                    row_width = img_width * 3  # Total width of the row
                    space_width = row_width - img_width  # Total space width between images
                    num_spaces = 2  # Number of spaces between images
                    space_size = space_width // num_spaces  # Size of each space
                    counter = 0
                    for image in selected_images:
                        if counter == 3:
                            img_y += img_height + 40 + space_size  # Add space after row
                            img_x = 20
                            counter = 0
                        img = ImageReader(image)
                        item_name = image.split(".")[0].lower()[:13]  # Extract the item name from the file name
                        c.drawString(img_x, img_y + img_height + 5, item_name)  # Add the item name above the QR code
                        c.drawImage(img, x=img_x, y=img_y, width=img_width, height=img_height)
                        img_x += img_width + space_size  # Add space between images
                        counter += 1
                    c.save()
                    selected_items.clear()
                    self.ids.selected_items.text = ""
                    self.ids.controller2.clear_selection()
            except OSError as e:
                # self.ids.controller2.clear_selection()
                print(e)
                self.ids.selection.text = f"Veuillez réessayer après 30 secondes !!"  # French message
                self.create_qr_file(selected_items)
                selected_items.clear()
                return
        else:
            try:
                with open(name + ".pdf", 'wb') as pdf:
                    c = canvas.Canvas(pdf, pagesize=letter)
                    img_x = 20
                    img_y = 20
                    img_width = 87
                    img_height = 87
                    counter = 0
                    for image in selected_images:
                        if counter == 6:
                            img_y += img_height + 40
                            img_x = 20
                            counter = 0
                        img = ImageReader(image)
                        item_name = image.split(".")[0].lower()[:13]  # Extract the item name from the file name
                        c.drawString(img_x, img_y + img_height + 5, item_name)  # Add the item name above the QR code
                        c.drawImage(img, x=img_x, y=img_y, width=img_width, height=img_height)
                        img_x += img_width + 5
                        counter += 1
                    c.save()
                    selected_items.clear()
                    self.ids.selected_items.text = ""
                    self.ids.controller2.clear_selection()

            except OSError as e:
                print(e)
                self.ids.selection.text = f"Veuillez réessayer après 30 secondes !!"
                self.create_qr_file(selected_items)
                selected_items.clear()
                return
        try:
            src_path = name + ".pdf"
            if platform == 'android':
                dst_path = dir_path
            else:
                dst_path = r"C:\Users\Projects"
            shutil.copy(src_path, dst_path)
            # self.ids.selection.text = f"le fichier {name}.pdf a été généré avec succès! \n vous le trouvez à "
            # \"Dossier Téléchargement/MonMagasin"
            os.remove(src_path)
            self.open_pdf_with_default_pdf(src_path)
        except Exception:
            pass
            """src_path = name + ".pdf"
            print(e)
            self.ids.selection.text = str(e)
            if platform == "android":
                try:
                    from androidstorage4kivy import SharedStorage
                    SharedStorage().copy_to_shared(f'./{src_path}')
                    self.ids.selection.text = f"le fichier {name}.pdf a été généré avec succès! \n vous le trouvez à " \
                                              "Dossier Documents/Store_I"
                except Exception as e:
                    self.ids.selection.text = str(e)"""

    def write_table_to_pdf(self, pdf_file_name):
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        import shutil
        # self.get_total_sales()
        data = DataBaseClasses.SQLiteDatabase(self.database_path).select("sales_history", ["product_name", "sold_amount", "DateAndMinutes"],
                               f"date = '{self.ids.time_variable.text}'")
        if data:
            # Set the cell width and height
            cell_width = 100
            cell_height = 20

            # Calculate the maximum number of rows that can fit on a page
            page_width, page_height = letter
            max_rows = int((page_height - 100) / cell_height)

            # Create the PDF file
            pdf = canvas.Canvas(pdf_file_name, pagesize=letter)

            # Set the font and font size
            pdf.setFont("Helvetica", 10)

            # Set the starting point for the table
            x = 50
            y = 750

            # Draw the table headers
            headers = ["product_name", "order_amount", "order_date"]
            for i in range(len(headers)):
                pdf.drawString(x + (i * cell_width), y, headers[i])

            # Draw the table data
            row_count = 0
            for row in data:
                # Check if we've reached the maximum number of rows for this page
                if row_count >= max_rows:
                    pdf.showPage()  # start a new page
                    y = 750  # reset y to top of page
                    row_count = 0  # reset row count to 0

                    # Draw the table headers on the new page
                    for i in range(len(headers)):
                        pdf.drawString(x + (i * cell_width), y, headers[i])

                # Draw the table data row
                y -= cell_height
                row_count += 1
                for i in range(len(row)):
                    if i == 0:  # check if the column is for product name
                        product_name = str(row[i]).lower()  # take only the first 13 characters of the product name
                        pdf.drawString(x + (i * cell_width), y, product_name)
                    else:
                        pdf.drawString(x + (i * cell_width), y, str(row[i]))

            # Save the PDF file
            pdf.save()

        try:
            src_path = "ventes.pdf"
            if platform == 'android':
                dst_path = dir_path
            else:
                dst_path = r"C:\Users\Projects\bin"
            shutil.copy(src_path, dst_path)
            # self.ids.selection.text = f"le fichier VENTES.pdf a été généré avec succès! \n vous le trouvez à
            # Dossier Téléchargement/MonMagasin \n"
            os.remove(src_path)
            self.open_pdf_with_default_pdf(pdf_file_name)
            # self.get_total_sales()

        except Exception as e:
            print(e)
            # self.ids.selection.text = "supprimez le fichier sales.pdf \n dans le dossier monmagasin s'il existe \n
            # et " \ "réessayez! \n"
            self.ids.selection.text = str(e)
            if platform == "android":
                try:
                    from androidstorage4kivy import SharedStorage
                    SharedStorage().copy_to_shared('./ventes.pdf')
                    #self.ids.selection.text = f"le fichier VENTES.pdf a été généré avec succès! \n vous le trouvez à " \
                                              #"Dossier Documents/Store_I"
                except Exception as e:
                    self.ids.selection.text = f"after android : {e}"

    def get_total_sales(self):
        date = self.ids.time_variable.text
        total_sales = 0
        total_profit = 0
        try:
            for row in DataBaseClasses.SQLiteDatabase(self.database_path).select("sales_total_history", "*", f"date='{date}'"):
                sold_amount = float(row[1])
                total_sales += sold_amount
                profit_from_amount = float(row[2])
                total_profit += profit_from_amount
                print(profit_from_amount)
            num = total_sales - total_profit
            total = str("{: ,}".format(int(total_sales)))
            num_ = str("{: ,}".format(int(num)))
            print(total)
            self.ids.total_for_today.text = f" le total des ventes aujourd'hui est de : {str(total)} CFA \n benefice " \
                                            f"total = {num_} CFA"
        except Exception as e:
            self.ids.total_for_today.text = str(e)

    def write_products_to_pdf(self, pdf_file_name):
        self.ids.selection.text = "Please wait... don't close screen"
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        import shutil

        data = sorted(DataBaseClasses.SQLiteDatabase(self.database_path).select("product_table", self.columns))
        if data:
            # Create the PDF file
            pdf = canvas.Canvas(pdf_file_name, pagesize=letter)

            # Set the font and font size
            pdf.setFont("Helvetica", 10)

            # Set the starting point for the table
            x = 50
            y = 750

            # Set the cell width and height
            cell_width = 100
            cell_height = 20

            # Draw the table headers
            headers = self.columns
            for i in range(len(headers)):
                pdf.drawString(x + (i * cell_width), y, headers[i])

            # Draw the table data
            for row in data:
                y -= cell_height
                if y < 50:  # Check if current y position is below the threshold
                    pdf.showPage()  # Create a new page
                    y = 750  # Reset y position to top of page
                    for i in range(len(headers)):
                        pdf.drawString(x + (i * cell_width), y, headers[i])  # Draw table headers on new page
                    y -= cell_height  # Decrement y position to start drawing data on new page
                for i in range(len(row)):
                    if i == 0:  # check if the column is for product name
                        product_name = str(row[i]).lower()  # take only the first 13 characters of the product name
                        pdf.drawString(x + (i * cell_width), y, product_name)
                    else:
                        pdf.drawString(x + (i * cell_width), y, str(row[i]))

            # Save the PDF file
            pdf.save()

        try:
            src_path = pdf_file_name
            if platform == 'android':
                dst_path = dir_path
            else:
                dst_path = r"C:\Users\Projects"
            shutil.copy(src_path, dst_path)
            os.remove(src_path)
            self.open_pdf_with_default_pdf(pdf_file_name)
            # self.ids.selection.text = "le fichier PRODUITS.pdf a été généré avec succès! \n vous le trouvez à " \
            # "Dossier Téléchargement/MonMagasin"
        except Exception as e:
            print(e)
            """if platform == "android":
                try:
                    from androidstorage4kivy import SharedStorage
                    from android_permissions import AndroidPermissions
                    SharedStorage().copy_to_shared('./produits.pdf')
                    self.ids.selection.text = f"le fichier PRODUITS.pdf a été généré avec succès! \n vous le trouvez à " \
                                              "Dossier Documents/Store_I"
                    self.open_pdf_with_default_pdf(pdf_file_name)
                except Exception as e:
                    self.ids.selection.text = f"after android : {e}"""

    def open_pdf_with_default_pdf(self, name):
        print(name)
        if platform == 'android':
            from jnius import autoclass
            try:
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                FileProvider = autoclass('androidx.core.content.FileProvider')  # Updated import
                pdf_path = os.path.join(dir_path, name)
                File = autoclass('java.io.File')

                # Create an intent to open the PDF file
                context = PythonActivity.mActivity.getApplicationContext()  # Added context variable
                authority = "{}.fileprovider".format(context.getPackageName())
                content_uri = FileProvider.getUriForFile(context, authority, File(pdf_path))
                intent = Intent()
                intent.setAction(Intent.ACTION_VIEW)
                intent.setDataAndType(content_uri, "application/pdf")
                intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)

                # Verify if there is an app that can handle the intent
                package_manager = context.getPackageManager()
                if intent.resolveActivity(package_manager):
                    # Start the activity
                    current_activity = PythonActivity.mActivity
                    current_activity.startActivity(intent)
                    # root.ids.person.text = ""
                else:
                    print("No app found to handle the intent.")
            except Exception:
                return
                # root.ids.facture_notif.text = "indiquez d'abord le nom du client"

        else:
            try:
                # Open the PDF file using the default app on non-Android platforms
                pdf_path = name
                os.startfile(pdf_path)
                print("name opened")
            except Exception as e:
                print("Error opening PDF file:", str(e))


class CustomBoxLayoutScreen2(BoxLayout):
    def __init__(self, **kwargs):
        super(CustomBoxLayoutScreen2, self).__init__(**kwargs)


class CustomTextField(MDTextField):
    def __init__(self, **kwargs):
        super(CustomTextField, self).__init__(**kwargs)


class RVForScreenTwo(RecycleView):
    def __init__(self, **kwargs):
        super(RVForScreenTwo, self).__init__(**kwargs)
        app = MDApp.get_running_app()
        self.database_path = app.get_database_path()

    def update_data(self, text=''):
        data_base_file = DataBaseClasses.SQLiteDatabase(self.database_path)
        result = sorted(data_base_file.select("product_table", ["product_name"]))
        original_data = [x[0] for x in result]
        filtered_data = [item for item in original_data if item[:len(text)].lower() == text.lower()]
        self.data = [{'text': str(x)} for x in filtered_data]
        self.refresh_from_data()


class SelectableRecycleBoxLayout2(FocusBehavior, LayoutSelectionBehavior,
                                  RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''

    def clear_selection(self, *args):
        ''' Deselects all the currently selected nodes.
        '''
        deselect = self.deselect_node
        nodes = self.selected_nodes
        for node in nodes[:]:
            deselect(node)


class SelectableLabelScreen2(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableLabelScreen2, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableLabelScreen2, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        app = MDApp.get_running_app().root.get_screen("second_screen")
        root = app
        self.selected = is_selected
        if self.selected:
            selected_option = rv.data[index]["text"]
            root.ids.selection.color = (0, 0, 0, 1)
            # root.ids.information.text = ""
            root.ids.selection.text = ""
            root.ids.total_for_today.text = ""
            """root.ids.selection.text = "le QRS maximum que vous pouvez insérer dans une page est de 36 \n au cas où " \
                                      "vous auriez plus de 36 QRS " \
                                      "\n essayez de le diviser en groupe \n de 36 éléments ** n'oubliez pas de " \
                                      "copier le qr " \
                                      "fichiers dans le dossier Téléchargement --- > MonMagasin \n parce que après chaque " \
                                      "impression, le fichier " \
                                      "existant sera " \
                                      "outrepasser"""""

            if is_selected and len(
                    selected_items) <= 36 and selected_option not in selected_items and not selected_option.isdigit():
                selected_items.append(selected_option)
                root.ids.selected_items.text = "".join([item + "\n" for item in selected_items])
                root.ids.counter.text = str(len(selected_items))

            else:
                self.selected = False
                try:
                    selected_items.remove(selected_option)
                    root.ids.selected_items.text = "".join([item + "\n" for item in selected_items])
                    root.ids.counter.text = str(len(selected_items))

                except ValueError:
                    pass
