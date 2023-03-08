"""
read QR Code

https://stackoverflow.com/questions/73067952/kivy-load-camera-zbarscan-on-click-button/73077097#73077097
"""


from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy_garden.zbarcam import ZBarCam
from kivy.utils import platform
from kivy.logger import Logger

__version__ = 1


class QrScanner(BoxLayout):
    def __init__(self, **kwargs):
        super(QrScanner, self).__init__(**kwargs)
        btn1 = Button(text="Scan Me", font_size="50sp")
        btn1.bind(on_press=self.callback)
        self.add_widget(btn1)

    def request_android_permissions(self):
        """
        Since API 23, Android requires permission to be requested at runtime.
        """
        from android.permissions import request_permissions, Permission

        def callback(permissions, results):
            """
            Defines the callback to be fired when runtime permission
            has been granted or denied. This is not strictly required,
            but added for the sake of completeness.
            """
            if all([res for res in results]):
                print("callback. All permissions granted.")
            else:
                print("callback. Some permissions refused.")

        request_permissions([Permission.CAMERA], callback)

    def build(self):
        if platform == "android":
            print("Android detected. Requesting permissions")
            self.request_android_permissions()

    def callback(self, instance):
        """On click button, initiate zbarcam and schedule text reader"""
        self.remove_widget(instance)  # remove button
        self.zbarcam = ZBarCam()
        self.add_widget(self.zbarcam)
        Clock.schedule_interval(self.read_qr_text, 2)

    def read_qr_text(self, *args):
        """
        Check if zbarcam.symbols is filled and stop scanning in such case
        """
        Logger.info(f"XXXX {self.zbarcam.symbols}")
        if len(self.zbarcam.symbols) > 0:  # when something is detected
            self.qr_text = self.zbarcam.symbols[0].data  # text from QR
            Clock.unschedule(self.read_qr_text, 2)
            self.zbarcam.stop()  # stop zbarcam
            self.zbarcam.ids["xcamera"]._camera._device.release()  # release camera
            # print(self.qr_text)
            Logger.info(f"XXXX {self.self.qr_text.symbols}")


class QrApp(App):
    def build(self):
        return QrScanner()


if __name__ == "__main__":
    QrApp().run()
