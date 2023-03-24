__version__ = '1'

from kivy.app import App
from kivy.lang import Builder

kv = """
BoxLayout:
    orientation: 'vertical'
    Label:
        text: 'Scroll TextInput'
        size_hint_y: None
        height: 48
    ToggleButton:
        size_hint_y: None
        height: 48
        text: 'Set Read-Only'
        on_state: text_input.readonly = True if self.state else False
    ScrollView:

        bar_color:(0, 0, 0, 0.4)
        bar_inactiv_color:(0, 0, 0.7, 0.4)
        bar_margin:2
        bar_width:8
        do_scroll_x:True
        do_scroll_y:True
        TextInput:
            id: text_input
            size_hint: .8, None
            height: self.minimum_height
            text: 'This is a long long long set of words\\n' * 100
"""


class ScrollTextApp(App):
    def build(self):
        return Builder.load_string(kv)


ScrollTextApp().run()
