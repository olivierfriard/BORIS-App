from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label

import sys
import json



class StartPageForm(BoxLayout):
    def exit(self):
        sys.exit()
    def show_SelectSubjectsForm(self):
        self.clear_widgets()
        self.add_widget(SelectSubjectsForm())
    def show_SelectObservationForm(self):
        self.clear_widgets()
        self.add_widget(SelectObservationForm())


class SelectObservationForm(BoxLayout):
    def cancel(self):
        self.clear_widgets()
        self.add_widget(StartPageForm())

    def view_events(self, selection):
        print selection[0]
        
        try:
            events = open( selection[0],'rb').readlines()
            print 'events:', events
        except:
            popup = Popup(title='Error', content=Label(text='The selected file is not a BORIS observation file!'),   size_hint=(None, None), size=(400, 200))
            popup.open()
            return
        
        
        view_obs = ViewObservationForm()
        self.add_widget(view_obs)
        
        ViewObservationForm.viewobs2_list.item_strings = events
        
        """
        #ViewObservationForm().view( events )
        self.clear_widgets()
        self.add_widget(ViewObservationForm(events))
        """

class ViewObservationForm(BoxLayout):
    viewobs2_list = ObjectProperty()
    def __init__(self, **kwargs):
        print kwargs
        super(ViewObservationForm, self).__init__(**kwargs)

        self.viewobs2_list.item_strings = ['a','b','c']

"""
class ViewObservationForm(BoxLayout):
    viewobs_list = ObjectProperty()
    #print  viewobs_list

    def __init__(self,events):
        print 'init events', events

    '''
    def view(self,events):
        print events
        print type(events)
        print self.viewobs_list.item_strings
        print type(self.viewobs_list)
        self.viewobs_list.item_strings = events
        #print '---',events
        print self.viewobs_list.item_strings
    pass
    '''
"""

class SelectSubjectsForm(BoxLayout):

    def cancel(self):
        self.clear_widgets()
        self.add_widget(StartPageForm())

    def load_subjects(self, path, selection):
        print path, selection[0]

        try:
            BorisApp.subjects = json.loads(open( selection[0],'rb').read() )
            print 'subjects:', BorisApp.subjects
        except:
            popup = Popup(title='Error', content=Label(text='The selected file is not a BORIS subjects file!'),   size_hint=(None, None), size=(400, 200))
            popup.open()
            return

    def next(self):
        #print BorisApp.subjects
        self.clear_widgets()
        self.add_widget(SelectEthogramForm())


class SelectEthogramForm(BoxLayout):

    def cancel(self):
        self.clear_widgets()
        self.add_widget(StartPageForm())

    def load_ethogram(self, path, selection):
        print path, selection
        try:
            BorisApp.behaviors = json.loads(open( selection[0],'rb').read() )
            print 'behaviors:', BorisApp.behaviors
        except:
            popup = Popup(title='Error', content=Label(text='The selected file is not a BORIS behaviors file!'),   size_hint=(None, None), size=(400, 200))
            popup.open()
            return

    def next(self):
        print BorisApp.behaviors
        if BorisApp.behaviors:
            self.clear_widgets()
            self.add_widget(StartObservationForm())
        else:
            print 'No behaviors'
            popup = Popup(title='Error', content=Label(text='You must choose an ethogram'),   size_hint=(None, None), size=(400, 200))
            popup.open()



class StartObservationForm(BoxLayout):
    obsid_input = ObjectProperty()
    obsdate_input = ObjectProperty()    
    def cancel(self):

        print BorisApp.behaviors
        '''
        self.clear_widgets()
        self.add_widget(StartPageForm())
        '''

    def next(self):
        print self.obsid_input.text, self.obsdate_input.text





class BorisRoot(BoxLayout):
    pass



class BorisApp(App):
    subjects = {}
    behaviors = {}
    pass

if __name__ == '__main__':
    BorisApp().run()
