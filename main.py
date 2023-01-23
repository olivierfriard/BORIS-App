import os
from kivy.utils import platform
from kivy.core.window import Window
from kivy.lang import Builder

from kivymd.app import MDApp
from kivymd.uix.filemanager import MDFileManager
from kivymd.toast import toast


KV = """
MDBoxLayout:
    orientation: "vertical"

    MDTopAppBar:
        title: "MDFileManager"
        left_action_items: [["menu", lambda x: None]]
        elevation: 3

    MDFloatLayout:

        MDRoundFlatIconButton:
            text: "Open manager"
            icon: "folder"
            pos_hint: {"center_x": .5, "center_y": .5}
            on_release: app.file_manager_open()
"""


class Example(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.events)
        self.manager_open = False
        self.file_manager = MDFileManager(exit_manager=self.exit_manager, select_path=self.select_path)

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        return Builder.load_string(KV)

    def file_manager_open(self):

        if platform == "android":
            import android
            from android.permissions import request_permissions, Permission

            print("request permission")

            request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])

            from android.storage import primary_external_storage_path

            primary_storage_dir = primary_external_storage_path()
            print("primary_storage_dir", primary_storage_dir)

            # from android.storage import secondary_external_storage_path

            # secondary_ext_storage = secondary_external_storage_path()
            # print("secondary_ext_storage", secondary_ext_storage)

            print('os.getenv("EXTERNAL_STORAGE")', os.getenv("EXTERNAL_STORAGE"))

            # path = os.path.join(os.getenv("EXTERNAL_STORAGE"), "")

            # print("path", path)
            # self.file_manager.show(path)
            self.file_manager.show(primary_storage_dir)
            self.manager_open = True

        else:

            self.file_manager.show(os.path.expanduser("~"))  # output manager to the screen
            self.manager_open = True

    def select_path(self, path: str):
        """
        It will be called when you click on the file name
        or the catalog selection button.

        :param path: path to the selected directory or file;
        """

        self.exit_manager()
        toast(path)

    def exit_manager(self, *args):
        """Called when the user reaches the root of the directory tree."""

        self.manager_open = False
        self.file_manager.close()

    def events(self, instance, keyboard, keycode, text, modifiers):
        """Called when buttons are pressed on the mobile device."""

        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True


Example().run()
