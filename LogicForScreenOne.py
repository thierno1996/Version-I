import sqlite3
import time
from collections import defaultdict
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivymd.app import MDApp
from kivy.uix.textinput import TextInput
from kivymd.uix.textfield import MDTextField
from DataBaseClasses import SQLiteDatabase
from kivy.clock import Clock
import datetime
from kivy.utils import platform
import os
import webbrowser
from kivymd.uix.button import MDIconButton

if platform == 'android':
    from android.storage import primary_external_storage_path

    path = os.path.join(primary_external_storage_path(), "Documents")
    try:
        directory = "factures"
        dir_path = os.path.join(path, directory)
        os.makedirs(dir_path)
    except Exception as e:
        print("the following error: ", e)


class CustomBoxLayout(GridLayout):
    def __init__(self, product_label, price="", amount_label="0", **kwargs):
        super(CustomBoxLayout, self).__init__(**kwargs)
        self.size_hint_y = None
        self.height = "30dp"
        self.cols = 5
        self.product_label = Label(text=product_label, font_size="20dp", color=(0, 0, 0, 1), size_hint_y=None,
                                   height="30dp")  # size_hint_x=None,
        # width="200dp"
        # self.minus_button = Button(text=minus_button, font_size="40dp", background_normal="", color="blue")
        self.price_entry = DigitOnlyTextInput(text=price, size_hint_y=None, height="30dp",
                                              background_normal="",
                                              halign="center", font_size="17dp", size_hint_x=None, width="110dp")
        self.times_amount = Label(text="x", font_size="20dp", color=(0, 0, 1, 1), size_hint_x=None, width="30dp",
                                  size_hint_y=None,
                                  height="30dp", bold=True)

        self.amount_label = DigitOnlyTextInput(text=amount_label, size_hint_y=None, height="30dp",
                                               background_normal="",
                                               halign="center", font_size="17dp", size_hint_x=None, width="75dp")
        # self.plus_button = Button(text=plus_button, font_size="40dp", background_normal="",
        # color="blue")

        self.delete_button = MDIconButton(icon="delete", theme_icon_color="Custom", icon_color=(0, 0, 1, 1))

        self.add_widget(self.product_label)
        # self.add_widget(self.minus_button)
        self.add_widget(self.price_entry)
        self.add_widget(self.times_amount)
        self.add_widget(self.amount_label)
        # self.add_widget(self.plus_button)

        # self.plus_button.bind(on_press=self.plus_button_clicked)
        # self.minus_button.bind(on_press=self.minus_button_clicked)
        self.add_widget(self.delete_button)
        self.amount_label.bind(text=self.re_calculate_price_with_decimal)
        self.delete_button.bind(on_release=self.delete_item)
        self.price_entry.bind(text=self.re_calculate_price_with_decimal)
        with self.product_label.canvas.before:
            Color(rgba=(0, 0, 1, .2))
            self.product_label.rect = Rectangle(size=self.size, pos=self.pos)
            self.product_label.bind(size=self.update_rectangle, pos=self.update_rectangle)

    def delete_item(self, instance):
        app = MDApp.get_running_app().root.get_screen("main_screen")
        root = app
        parent_widget = self.parent
        product_name = self.product_label.text
        if product_name in root.ids.select_item.order_input_name:
            del root.ids.select_item.order_input_name[product_name]
            del root.ids.order_input.get_product_amounts()[product_name]

        parent_widget.remove_widget(self)
        # root.ids.select_item.update_order_counts() #------ for displaying
        root.ids.order_input._calculate_total_price()

    def plus_button_clicked(self, *args):
        app = MDApp.get_running_app().root.get_screen("main_screen")
        root = app
        try:
            self.amount_label.text = str(int(self.amount_label.text) + 1)
        except ValueError:
            self.amount_label.text = str(0)
            self.amount_label.text = str(int(self.amount_label.text) + 1)
        root.ids.select_item.order_input_name[self.product_label.text] += 1
        root.ids.order_input.calculate_total_price(root.ids.order_input.get_product_amounts())

    def minus_button_clicked(self, *args):
        app = MDApp.get_running_app().root.get_screen("main_screen")
        root = app
        if self.amount_label.text != "0" and self.amount_label.text != "":
            self.amount_label.text = str(int(self.amount_label.text) - 1)
            root.ids.select_item.order_input_name[self.product_label.text] -= 1
            root.ids.order_input.calculate_total_price(root.ids.order_input.get_product_amounts())

    def re_calculate_price_with_decimal(self, instance, value):
        app = MDApp.get_running_app().root.get_screen("main_screen")
        root = app
        # product_label = self.product_label.text.replace(",", ".")
        if instance.text.replace(",", "."):
            root.ids.order_input._calculate_total_price()
            """try:
                if product_label.replace(",", ".") in root.ids.select_item.order_input_name:
                    root.ids.select_item.order_input_name[product_label] = 0
                    root.ids.select_item.order_input_name[product_label] += float(instance.text.replace(",", "."))
                else:
                    root.ids.select_item.order_input_name[product_label] = 0
                    root.ids.select_item.order_input_name[product_label] = float(instance.text.replace(",", "."))
                root.ids.order_input._calculate_total_price(root.ids.order_input.get_product_amounts())
            except ValueError as e:
                print(e)"""

    def get_passed_arguments(self):
        result = [child.text for child in self.children]
        return reversed(result)

    def update_rectangle(self, *args):
        self.product_label.rect.size = self.product_label.size
        self.product_label.rect.pos = self.product_label.pos


class CustomTextFieldScreenOne(MDTextField):
    def __init__(self, **kwargs):
        super(CustomTextFieldScreenOne, self).__init__(**kwargs)
        self.order_input_name = defaultdict(float)
        app = MDApp.get_running_app()
        self.database_path = app.get_database_path()
        print("This is the path", self.database_path)

    """"def on_text_validate(self):
        self.order_registration(self.text.strip().upper())  # .upper())
        self.update_order_counts()
        self.text = ""
        self.hint_text = ""
        super().on_text_validate()
        Clock.schedule_once(lambda dt, self=self: setattr(self, 'focus', True), 0.1)"""

    """def on_parent(self, widget, parent):
        Clock.schedule_once(lambda dt, self=self: setattr(self, 'focus', True), 2)"""

    def order_registration(self, name):
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        try:
            if name:
                cursor.execute("SELECT COUNT(*) FROM product_table WHERE product_name=?", (name,))
                result = cursor.fetchone()
                if result[0] > 0:
                    if name not in self.order_input_name:
                        self.order_input_name[name] += 1
                else:
                    print(f"{name} not in database")
        except sqlite3.OperationalError:
            print("no database available")
        conn.close()

    def update_order_counts(self):  # ----- handling display
        app = MDApp.get_running_app().root.get_screen("main_screen")
        root = app
        product_amounts = root.ids.order_input.get_product_amounts()

        for name, count in self.order_input_name.items():
            if name not in product_amounts:
                price = self.search_price_in_database(name)
                root.ids.order_input.add_widget(
                    CustomBoxLayout(product_label=name, amount_label=str(count), price=str(price)))

        root.ids.order_input._calculate_total_price()

    def search_price_in_database(self, name):
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        query = "SELECT selling_price FROM product_table WHERE product_name = ?"
        cursor.execute(query, (name,))

        price = cursor.fetchone()
        if price is not None:
            price = price[0]

        conn.close()
        return price


class CartClass(BoxLayout):
    def __init__(self, **kwargs):
        super(CartClass, self).__init__(**kwargs)
        app = MDApp.get_running_app()
        self.database_path = app.get_database_path()
        self.product_amounts = {}
        # self.user_prices = {}
        # self.register_sold_items()

    def get_product_amounts(self):
        for child in reversed(self.children):
            product_name = child.product_label.text.replace(",", ".")
            if child.amount_label.text != "":
                amount = float(child.amount_label.text.replace(",", "."))
                # if amount > 0:
                self.product_amounts[product_name] = amount
            # self.user_prices[child.product_label.text] = child.price_entry.text

        return self.product_amounts

    def _calculate_total_price(self):
        app = MDApp.get_running_app().root.get_screen("main_screen")
        root = app
        total_price = 0

        for child_widget in self.children:
            if isinstance(child_widget, CustomBoxLayout):
                price = float(child_widget.price_entry.text.replace(",", "."))
                try:
                    amount = float(child_widget.amount_label.text)
                except ValueError:
                    amount = float(child_widget.amount_label.text.replace(",", "."))

                integer_amount = int(amount)
                fractional_part = amount % 1

                item_price = price * integer_amount
                total_price += item_price

                if fractional_part > 0:
                    fractional_price = price * fractional_part
                    total_price += fractional_price

        root.ids.total.text = "{:,.2f} CFA".format(round(total_price, 2))

    def calculate_total_price(self, product_amounts):
        app = MDApp.get_running_app().root.get_screen("main_screen")
        root = app
        date = datetime.date.today().strftime('%Y-%m-%d')
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            selected_products = list(self.get_product_amounts().keys())
            query = "SELECT product_name, selling_price FROM product_table WHERE product_name IN ({})".format(
                ",".join("?" * len(selected_products)))
            cursor.execute(query, selected_products)
            results = cursor.fetchall()
            total_price = 0
            for name, price in results:
                amount = product_amounts[name]
                if amount.is_integer():  # if amount is a whole number
                    total_price += float(price) * amount
                else:  # if amount is a decimal number
                    box_price = float(price) * int(amount)
                    half_box_price = float(price) / 2
                    total_price += box_price + half_box_price

            conn.close()

            """local_currency = locale.setlocale(locale.LC_ALL, '')
            if local_currency:
                currency_total = locale.currency(total_price, grouping=True)
                root.ids.total.text = currency_total
            else:"""
            root.ids.total.text = "{:,.2f} CFA".format(round(total_price, 2))

            # root.ids.total.text = str("{: ,}".format(total_price)) + ""
            return results
        except Exception as e:
            root.ids.total.text = str(e)

    def calculate_total_profit(self, product_amounts):
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            selected_products = list(self.get_product_amounts().keys())
            query = "SELECT product_name, buying_price FROM product_table WHERE product_name IN ({})".format(
                ",".join("?" * len(selected_products)))
            cursor.execute(query, selected_products)
            results = cursor.fetchall()
            total_price = 0
            for name, price in results:
                amount = product_amounts[name]
                print(amount)
                total_price += float(price) * float(amount)
            print("this is total price: " + str(int(total_price)))

            conn.close()
            return total_price
        except Exception as e:
            print(e)

    def register_sold_items(self):
        app = MDApp.get_running_app().root.get_screen("main_screen")
        root = app

        now = datetime.datetime.now()
        DateAndMinutes = now.strftime("%Y-%m-%d %H:%M")
        date = datetime.date.today().strftime('%d-%m-%Y')
        db = SQLiteDatabase(self.database_path)
        db.create_table("sales_history", ["product_name", "sold_amount", "date", "DateAndMinutes"])
        # alter_query = "ALTER TABLE sales_history ADD COLUMN cart_price TEXT"
        # alter_query = "ALTER TABLE sales_history DROP COLUMN cart_price "
        # db.cursor.execute(alter_query)
        # db.delete("sales_total_history")
        # db.delete("sales_history")
        try:
            for key, value in self.get_product_amounts().items():
                db.insert("sales_history", [key, value, date, DateAndMinutes])
                current_quantity = db.select("product_table", ["quantity"], f"product_name = '{key}'")[0][0]
                if current_quantity:
                    updated_quantity = float(current_quantity) - float(value)
                    db.update("product_table", {"quantity": updated_quantity}, f"product_name = '{key}'")
            db.create_table("sales_total_history", ["date", "cart_price", "profit_column"])
            # alter_query = "ALTER TABLE sales_total_history ADD COLUMN profit_column "
            # db.cursor.execute(alter_query)
        except IndexError:
            pass

        if self.calculate_total_profit(self.product_amounts):
            profit = self.calculate_total_profit(self.product_amounts)
            total_price = root.ids.total.text.replace(",", "").replace("CFA", "")
            db.insert("sales_total_history", [date, total_price, profit])
            print(profit)
        else:
            total_price = root.ids.total.text.replace(",", "").replace("CFA", "")
            db.insert("sales_total_history", [date, total_price, "0"])
        # print(root.order_input.product_amounts)

    def _get_children_data(self):
        children_data = []

        for child_widget in self.children:
            if isinstance(child_widget, CustomBoxLayout):
                product_label = child_widget.product_label.text
                price_entry = child_widget.price_entry.text
                amount_label = child_widget.amount_label.text
                children_data.extend([amount_label.replace(",", "."), product_label, price_entry])

        return children_data

    def create_invoice(self, name):
        from newFatura import CustomCanvas
        import shutil
        app = MDApp.get_running_app().root.get_screen("main_screen")
        date = datetime.date.today().strftime('%d-%m-%Y')
        root = app
        list_of_all_items = self._get_children_data()
        # def handle_name(name):
        name = name  # root.ids.person.text
        if name:
            invoice_name = f"{name.upper()}.pdf"
            try:
                CustomCanvas(invoice_name, list_of_all_items, name, root.ids.total.text).draw()
                list_of_all_items.clear()
                self.open_pdf_with_default_app(invoice_name)
                self.create_invoice_table(invoice_name)
                # root.ids.person.text = ""
            except:
                return

            try:
                src_path = invoice_name
                if platform == 'android':
                    dst_path = dir_path
                else:
                    dst_path = r"C:\Users\Projects\bin"
                shutil.copy(src_path, dst_path)
                os.remove(src_path)
            except:

                return

        # Open the popup window to get the name from the user
        # name_popup = NamePopup(callback=handle_name)
        # name_popup.open()

    def open_pdf_with_default_pdf(self):
        app = MDApp.get_running_app().root.get_screen("main_screen")
        root = app

        # def handle_name(name):
        name = root.ids.person.text
        if name:
            if platform == 'android':
                from jnius import autoclass

                try:
                    PythonActivity = autoclass('org.kivy.android.PythonActivity')
                    Intent = autoclass('android.content.Intent')
                    Uri = autoclass('android.net.Uri')
                    FileProvider = autoclass('androidx.core.content.FileProvider')
                    File = autoclass('java.io.File')

                    pdf_path = os.path.join(dir_path, name + ".pdf")
                    context = PythonActivity.mActivity.getApplicationContext()
                    authority = "{}.fileprovider".format(context.getPackageName())
                    content_uri = FileProvider.getUriForFile(context, authority, File(pdf_path))

                    intent = Intent()
                    intent.setAction(Intent.ACTION_VIEW)
                    intent.setDataAndType(content_uri, "application/pdf")
                    intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)

                    package_manager = context.getPackageManager()
                    intent.resolveActivity(package_manager)

                    current_activity = PythonActivity.mActivity
                    current_activity.startActivity(intent)
                except Exception as e:
                    print("Error opening PDF file:", str(e))

            else:
                try:
                    # Open the PDF file using the default app on non-Android platforms
                    pdf_path = name + ".pdf"
                    os.startfile(pdf_path)
                except Exception as e:
                    print("Error opening PDF file:", str(e))

        # Open the popup window to get the name from the user
        # name_popup = NamePopup(callback=handle_name)
        # name_popup.open()

    def open_pdf_with_default_app(self, name):
        app = MDApp.get_running_app().root.get_screen("main_screen")
        root = app
        # name = root.ids.person.text
        if platform == 'android':
            from jnius import autoclass

            try:
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                FileProvider = autoclass('androidx.core.content.FileProvider')
                File = autoclass('java.io.File')

                pdf_path = os.path.join(dir_path, name)
                context = PythonActivity.mActivity.getApplicationContext()
                authority = "{}.fileprovider".format(context.getPackageName())
                content_uri = FileProvider.getUriForFile(context, authority, File(pdf_path))

                intent = Intent()
                intent.setAction(Intent.ACTION_VIEW)
                intent.setDataAndType(content_uri, "application/pdf")
                intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)

                package_manager = context.getPackageManager()
                intent.resolveActivity(package_manager)

                current_activity = PythonActivity.mActivity
                current_activity.startActivity(intent)
            except Exception as e:
                print("Error opening PDF file:", str(e))

        else:
            try:
                # Open the PDF file using the default app on non-Android platforms
                pdf_path = name
                os.startfile(pdf_path)
            except Exception as e:
                print("Error opening PDF file:", str(e))

    def create_invoice_table(self, name):
        db = SQLiteDatabase(self.database_path)
        db.create_table("invoice_table", ["person_name"])
        # db.delete("invoice_table")
        try:
            name_exist = db.select("invoice_table", ["person_name"], f"person_name = '{name}'")[0][0]
            print("name", name_exist)
        except IndexError:
            db.insert("invoice_table", [name])


class DigitOnlyTextInput(TextInput):
    def __init__(self, **kwargs):
        super(DigitOnlyTextInput, self).__init__(**kwargs)

    def insert_text(self, substring, from_undo=False):
        allowed_chars = "1234567890,"
        digits = [char for char in substring if char in allowed_chars]
        return super().insert_text("".join(digits), from_undo=from_undo)
