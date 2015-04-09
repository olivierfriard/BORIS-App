from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
import sys


class StartPageForm(BoxLayout):
    def exit(self):
        sys.exit()
    def show_SelectSubjectsForm(self):
        self.clear_widgets()
        self.add_widget(SelectSubjectsForm())
    def show_ViewObservationForm(self):
        self.clear_widgets()
        self.add_widget(ViewObservationForm())


class ViewObservationForm(BoxLayout):
    pass

class SelectSubjectsForm(BoxLayout):

    def cancel(self):
        self.clear_widgets()
        self.add_widget(StartPageForm())

    def load_subjects(self, path, selection):
        print path, selection

    def next(self):
        self.clear_widgets()
        self.add_widget(SelectEthogramForm())

class SelectEthogramForm(BoxLayout):

    def cancel(self):
        self.clear_widgets()
        self.add_widget(StartPageForm())

    def load_ethogram(self, path, selection):
        print path, selection

    def next(self):
        pass



class BorisRoot(BoxLayout):
    pass



class BorisApp(App):
    pass

if __name__ == '__main__':
    BorisApp().run()
