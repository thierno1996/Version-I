from kivy.properties import BooleanProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
# from kivymd.uix.button import MDIconButton
import DataBaseClasses
from kivy import platform
from kivymd.uix.textfield import MDTextField
from kivy.clock import Clock
from kivymd.uix.dialog import MDDialog
from kivy.utils import platform
import os
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle


class ScreenOne(MDScreen):
    def __init__(self, **kwargs):
        super(ScreenOne, self).__init__(**kwargs)
        self.dialog = None
        self.rv_screen1 = RVForScreenOne()
        self.rv_instance = RVForScreenOne()
        self.customer_list = None
        self.window = Popup(title="", background_color=(0, 0, 0, .1), separator_color=(0, 0, 0, 0),
                            content=self.rv_screen1,
                            size_hint_y=None, height="300dp",
                            pos_hint={"center_x": .5})
        self.window.bind(on_dismiss=self.pop_up_clear)

    def change_screens_two(self):
        try:
            self.parent.current = "second_screen"
            self.parent.transition.direction = "left"
        except Exception as e:
            self.show_alert_dialog()
            print(e)

    def show_alert_dialog(self):
        from kivymd.uix.button import MDFlatButton
        if not self.dialog:
            self.dialog = MDDialog(
                text="veuillez patienter pendant que le reste de l'application est chargé",
                buttons=[
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=(0, 0, 1, 1),
                        on_press=self.on_yes_button_pressed
                    ),

                ],
            )
        self.dialog.open()

    def on_yes_button_pressed(self, instance):
        self.dialog.dismiss()

    def change_screens_three(self):
        try:
            self.parent.current = "third_screen"
            self.parent.transition.direction = "left"
        except Exception as e:
            self.show_alert_dialog()
            print(e)

    def pop_up_clear(self, dt):
        pass
        # self.ids.popup_controller.text = ""

    def go_to_screen_two(self):
        self.manager.current = "second_screen"
        self.manager.transition.direction = 'right'

    def go_to_screen_three(self):
        self.manager.current = "third_screen"
        self.manager.transition.direction = 'right'

    def go_to_screen_one(self):
        self.manager.current = "main_screen"
        self.manager.transition.direction = 'right'
        # self.ids.select_item.focus = True

    def change_toolbar(self, *args):
        toolbar = self.ids.toolbar
        toolbar.switch_tab("main_screen")
        """"action_item = toolbar.ids.right_actions.children
        action_item[1].text_color = (0, 0, 0, .4)
        action_item[2].text_color = (0, 0, 0, .4)"""

    def on_pre_enter(self, *args):
        Clock.schedule_once(self.change_toolbar, .1)

    def on_leave(self, *args):
        pass
        # self.ids.facture_notif.text = ""

    def open_file_chooser(self, default_path=None):
        def on_selection(*args):
            file_path = args[1][0]
            if platform == 'android':
                self.open_pdf_with_default_app(file_path)
            else:
                os.startfile(file_path)

        def open_file_chooser_android(*args):
            file_chooser = FileChooserListView(
                path=args[0]
            )
            file_chooser.bind(selection=on_selection)

            layout = BoxLayout(orientation='vertical')
            layout.add_widget(file_chooser)

            popup = Popup(
                title='Choose a File',
                content=layout,
                size_hint=(0.9, 0.8)
            )
            popup.open()

        if platform == 'android':
            from android.permissions import request_permissions, Permission
            from android.storage import primary_external_storage_path
            path = os.path.join(primary_external_storage_path(), "Documents", "factures")

            def request_permission_callback(permission, grant_result):
                if all(grant_result):
                    Clock.schedule_once(lambda dt: open_file_chooser_android(path), 0)
                else:
                    root.ids.person.text = "permissions denied"

            request_permissions(
                [Permission.READ_EXTERNAL_STORAGE],
                request_permission_callback
            )
        else:
            Clock.schedule_once(lambda dt: open_file_chooser_android(r"C:\Users\Projects"), 0)

    def open_pdf_with_default_app(self, name):
        if platform == 'android':
            from jnius import autoclass

            try:
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                FileProvider = autoclass('androidx.core.content.FileProvider')
                File = autoclass('java.io.File')

                pdf_path = name  # os.path.join(dir_path, name)
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

    def add_arv(self):
        app = MDApp.get_running_app()
        if self.customer_list is None:
            content_ = BoxLayout(orientation="vertical")
            text_ = TextInput(size_hint_y=None, height="30dp", background_normal="", hint_text="Nom du client...")
            button_ = Button(text="Creer Une Facture", size_hint=(None, None), size=("200dp", "30dp"),
                             pos_hint={"center_x": .5}, bold=True, color=(0, 0, 1, 1), background_normal="")
            content_.add_widget(text_)
            content_.add_widget(self.rv_instance)
            content_.add_widget(button_)

            self.customer_list = Popup(title="Rechercher des clients précédents", separator_color=(0, 0, 1, 1),
                                       content=content_, title_align = "center", title_size = "16dp",
                                       size_hint_y=None, height="400dp", title_color = (1, 1, 1, 1))
                                       #background_color=(0, 0, 1, .5))
                                       #pos_hint={"center_x": .8})

            def update_data(instance, value):
                self.rv_instance.update_data(
                    DataBaseClasses.SQLiteDatabase(app.get_database_path()), "invoice_table", "person_name",
                    instance.text
                )

            text_.bind(text=update_data)

            def customers_(*args):
                text = text_.text
                self.ids.order_input.create_invoice(text)
                self.customer_list.dismiss()
                text_.text = ""

            button_.bind(on_press=customers_)

        self.customer_list.open()


class RVForScreenOne(RecycleView):
    def __init__(self, **kwargs):
        super(RVForScreenOne, self).__init__(**kwargs)
        app = MDApp.get_running_app()
        self.database_path = app.get_database_path()
        self.data = []

    def update_data(self, database_file, table, product_name, text=''):
        # data_base_file = DataBaseClasses.SQLiteDatabase(self.database_path)
        app = MDApp.get_running_app().root.get_screen("main_screen")
        root = app
        result = sorted(database_file.select(f"{table}", [f"{product_name}"]))  # product_table
        original_data = [x[0] for x in result]
        filtered_data = [item for item in original_data if item[:len(text)].lower() == text.lower()]
        if filtered_data:
            self.data = [{'text': str(x)} for x in filtered_data]
            self.refresh_from_data()
        else:
            root.window.dismiss()


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''

    def clear_selection(self, *args):
        ''' Deselects all the currently selected nodes.
        '''
        deselect = self.deselect_node
        nodes = self.selected_nodes
        for node in nodes[:]:
            deselect(node)


class SelectableLabel(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        app = MDApp.get_running_app().root.get_screen("main_screen")
        root = app
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if self.selected:
            if rv.data[index]["text"][:3].isupper():
                text = rv.data[index]["text"].split(".")
                root.ids.order_input.create_invoice(text[0])
                root.customer_list.content.children[1].ids.controller.clear_selection()
                root.customer_list.content.children[2].text = ""
                root.customer_list.dismiss()


            else:
                root.ids.select_item.order_registration(rv.data[index]["text"])
                root.window.content.ids.controller.clear_selection()
                root.ids.select_item.update_order_counts()
                root.window.dismiss()
                root.ids.select_item.text = ""
