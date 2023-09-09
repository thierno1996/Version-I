import os
from kivy.utils import platform
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from ScreenOne import ScreenOne
from kivy.core.window import Window
from kivy.clock import Clock
from DataBaseClasses import SQLiteDatabase
import shutil

Builder.load_file("ScreenOne.kv")
if platform == 'android':
    from android.permissions import request_permissions, Permission


    def callback(permission, result):
        if all([res for res in result]):
            result_of_permissions = "I got all permissons"
        else:
            result_of_permissions = "I didnt get all permissions"


    request_permissions(
        [Permission.CAMERA, Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE],
        callback)


class MyScreenManager(MDScreenManager):
    def __init__(self, **kwargs):
        super(MyScreenManager, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_key)

    def on_key(self, window, key, *args):
        if key == 27:
            if self.current != "main_screen":
                self.current = "main_screen"
                self.transition.direction = "right"
                return True
            else:
                return False


class SmallStore(MDApp):
    def __init__(self, **kwargs):
        super(SmallStore, self).__init__(**kwargs)
        self.package = "org.test.fiboutique"

    def build(self):
        # self.icon = 'icon.png'
        self.sm = MyScreenManager()
        screen1 = ScreenOne(name="main_screen")
        self.sm.add_widget(screen1)
        self.copy_prepopulated_database()
        if platform == "android":
            from android import loadingscreen
            Clock.schedule_once(lambda dt: loadingscreen.hide_loading_screen())
        return self.sm

    def copy_prepopulated_database(self):
        if platform == 'android':
            source_path = 'SmallStore.db'
            destination_path = os.path.join(self.get_storage_path(), 'SmallStore.db')
            if not os.path.exists(destination_path):
                try:
                    shutil.copy(source_path, destination_path)
                except Exception as e:
                    print("the foloowing", e)

    def get_storage_path(self):
        if platform == 'android':
            from android import mActivity
            context = mActivity.getApplicationContext()
            result = context.getExternalFilesDir(None)
            if result:
                storage_path = str(result.toString())
                print("the result", result)
                return storage_path
            else:
                print("nothing")

        else:
            return ''

    def get_database_path(self):
        return os.path.join(self.get_storage_path(), 'SmallStore.db')

    def on_start(self):
        if platform == "android":
            from jnius import autoclass
            from android import loadingscreen
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            ActivityInfo = autoclass("android.content.pm.ActivityInfo")
            activity = PythonActivity.mActivity
            activity.setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_USER)
            Clock.schedule_once(lambda dt: loadingscreen.hide_loading_screen(), 3)
            print("loading_screen is :", loadingscreen)
        Clock.schedule_once(lambda dt: self.load_screens(), 5)
        # self.create_dir()

    def load_screens(self):
        from ScreenThree import ScreenThree
        from ScreenTwo import ScreenTwo
        Builder.load_file("ScreenTwo.kv")
        Builder.load_file("ScreenThree.kv")
        screen2 = ScreenTwo(name="second_screen")
        self.sm.add_widget(screen2)
        screen3 = ScreenThree(name="third_screen")
        self.sm.add_widget(screen3)
        print("everything is loaded")

    def create_dir(self):
        if platform == 'android':
            from android.storage import primary_external_storage_path
            path = os.path.join(primary_external_storage_path(), "Documents")
            try:
                directory = "MonMagasin"
                dir_path = os.path.join(path, directory)
                os.makedirs(dir_path)
            except Exception as e:
                print("the following error: ", e)

    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == "__main__":
    SmallStore().run()
