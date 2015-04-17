from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.modalview import ModalView

import sys
import json
import time
import codecs
import datetime

NO_FOCAL_SUBJECT = 'No focal subject'


class StartPageForm(BoxLayout):

    def exit(self):
        '''
        self.clear_widgets()
        self.add_widget(DatePicker())
        '''

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
        '''load subjects from file'''
        try:
            BorisApp.subjects = json.loads(open( selection[0],'rb').read() )
            print 'subjects:', BorisApp.subjects
        except:
            popup = Popup(title='Error', content=Label(text='The selected file is not a BORIS subjects file!'),   size_hint=(None, None), size=(400, 200))
            popup.open()
            return
        self.next()

    def next(self):
        '''show select ethogram form'''
        self.clear_widgets()
        self.add_widget(SelectEthogramForm())


class SelectEthogramForm(BoxLayout):

    def cancel(self):
        self.clear_widgets()
        self.add_widget(StartPageForm())

    def load_ethogram(self, path, selection):
        '''load ethogram from selected file'''
        if not selection:
            popup = Popup(title='Error', content=Label(text='No file selected!'),   size_hint=(None, None), size=(400, 200))
            popup.open()
            return
        try:
            BorisApp.behaviors = json.loads(open( selection[0],'rb').read() )
            print 'behaviors:', BorisApp.behaviors
        except:
            popup = Popup(title='Error', content=Label(text='The selected file is not a BORIS behaviors file!'),   size_hint=(None, None), size=(400, 200))
            popup.open()
            return

        self.clear_widgets()

        a = StartObservationForm()
        a.obsdate_input.text = '{:%Y-%m-%d %H:%M}'.format(datetime.datetime.now())
        self.add_widget(a)



class StartObservationForm(BoxLayout):
    obsid_input = ObjectProperty()
    obsdate_input = ObjectProperty()    

    t0 = 0 # initial time
    fileName = ''
    currentStates = []
    focal_subject = ''
    btnList = {}
    btnSubjectsList = {}
    behaviorsLayout = ''
    subjectsLayout = ''

    def cancel(self):
        self.clear_widgets()
        self.add_widget(StartPageForm())

    def start(self):

        def btnBehaviorPressed(obj):
            '''
            behavior button pressed
            '''
            t = time.time()
            out = ''
            newState = obj.text

            # state event
            if BorisApp.behaviors[ newState ]['type'] == 'state':
                if newState in self.currentStates:
                    out += u'{time}\t{subject}\t{state}\tSTOP\n'.format(time=round(t - self.t0, 3), subject=self.focal_subject, state=newState)
                    obj.background_color = [1,1,1,1]
                    self.currentStates.remove(newState)
                else:
                    # test if state is exclusive
                    if BorisApp.behaviors[ newState ]['exclude']:
                        statesToStop = []

                        for cs in self.currentStates:
                            if cs in BorisApp.behaviors[ newState ]['exclude']:
                                out += u'{time}\t{subject}\t{state}\tSTOP\n'.format(time=round(t - self.t0, 3), state=cs, subject=self.focal_subject)
                                statesToStop.append(cs)
                                self.btnList[cs].background_color = [1,1,1,1]

                        for s in statesToStop:
                            self.currentStates.remove(s)

                    out += u'{time}\t{subject}\t{state}\tSTART\n'.format(time=round(t - self.t0, 3), state=newState, subject= self.focal_subject)
                    obj.background_color = [5,1,1,1]
                    self.currentStates.append(newState)

            # point event
            if BorisApp.behaviors[ newState ]['type'] == 'point':
                out = u'{time}\t{subject}\t{state}\n'.format( time=round(t - self.t0, 3), state=newState, subject= self.focal_subject )

            with codecs.open(self.fileName,"ab","utf-8") as f:
                f.write(out)


        def btnSubjectPressed(obj):
            '''
            subject button pressed
            '''
            # set focal subject
            if self.focal_subject and self.focal_subject != NO_FOCAL_SUBJECT:
                self.btnSubjectsList[ self.focal_subject ].background_color = [1,1,1,1]

            if obj.text == self.focal_subject:
                # set focal subject to NO_FOCAL_SUBJECT
                self.focal_subject == NO_FOCAL_SUBJECT
            else:
                self.focal_subject = obj.text
                obj.background_color = [5,1,1,1]

            print( 'focal subject:', self.focal_subject )
            # show behaviors
            self.clear_widgets()
            self.add_widget(self.behaviorsLayout)

        def btnStopPressed(obj):

            def my_callback(instance):
                if instance.title == 'y':
                    self.clear_widgets()
                    self.add_widget(StartPageForm())

            pop = ConfirmStopPopup()
            pop.bind( on_dismiss=my_callback )
            pop.open()

        def view_subjects_layout(obj):
            self.clear_widgets()
            self.add_widget(self.subjectsLayout)

        # create file for observations

        if not self.obsid_input.text:
            p = Popup(title='Error', content=Label(text='The observation id is empty'), size_hint=(None, None), size=(400, 200))
            p.open()
            return

        self.fileName = self.obsid_input.text.replace(' ','_').replace('/','_').replace('(','_').replace(')','_')+'.boris_observation.tsv'
        print type( self.obsid_input.text  )
        id_ = u'observation_id:{0}\n'.format( self.obsid_input.text.decode('utf-8') )
        with codecs.open(self.fileName, 'wb', "utf-8") as f:
            f.write( id_ )
            f.write( u'date:{0}\n'.format( self.obsdate_input.text ) )

        # create layout with subject buttons
        if BorisApp.subjects:
            self.subjectsLayout = GridLayout(cols= int((len(BorisApp.subjects['subjects'])+1)**0.5) , size_hint=(1,1), spacing=5)
            btn = Button(text = NO_FOCAL_SUBJECT, size_hint_x = 1, font_size = 24)
            btn.bind(on_release = btnSubjectPressed)
            for subject in BorisApp.subjects['subjects']:
                btn = Button(text = subject, size_hint_x = 1, font_size = 24)
                btn.background_color = [ 1,1,1,1 ]
                btn.bind(on_release = btnSubjectPressed)
                self.btnSubjectsList[ subject ] = btn
                self.subjectsLayout.add_widget(btn)


        # create layout with behavior buttons
        self.behaviorsLayout = GridLayout(cols= int((len(BorisApp.behaviors)+1)**0.5) , size_hint=(1,1), spacing=5)

        for b in BorisApp.behaviors:
            btn = Button(text = b, size_hint_x = 1, font_size = 24)
            btn.background_color = [ 1,1,1,1 ]
            btn.bind(on_release = btnBehaviorPressed)
            self.btnList[ b ] = btn
            self.behaviorsLayout.add_widget(btn)

        btn = Button(text = 'Select subject', size_hint_x = 1, font_size = 24)
        btn.background_color = [ 0,1,0,1 ]
        btn.bind(on_release = view_subjects_layout)
        self.behaviorsLayout.add_widget(btn)

        btn = Button(text = 'Stop obs', size_hint_x = 1, font_size = 24)
        btn.background_color = [ 1,0,0,1 ]
        btn.bind(on_release = btnStopPressed)
        self.behaviorsLayout.add_widget(btn)

        self.clear_widgets()
        self.add_widget(self.behaviorsLayout)

        self.t0 = time.time()


class ConfirmStopPopup(Popup):
    def yes(self):
        self.title = 'y'
        self.dismiss()

    def no(self):
        self.title = 'n'
        self.dismiss()


from functools import partial
from datetime import date, timedelta

class DatePicker(BoxLayout):

    def __init__(self, *args, **kwargs):
        super(DatePicker, self).__init__(**kwargs)
        self.date = date.today()
        self.orientation = "vertical"
        self.month_names = ('January',
                            'February', 
                            'March', 
                            'April', 
                            'May', 
                            'June', 
                            'July', 
                            'August', 
                            'September', 
                            'October',
                            'November',
                            'December')
        if kwargs.has_key("month_names"):
            self.month_names = kwargs['month_names']
        self.header = BoxLayout(orientation='horizontal', size_hint=(1, 0.2))
        self.body = GridLayout(cols=7)
        self.add_widget(self.header)
        self.add_widget(self.body)

        self.populate_body()
        self.populate_header()

    def populate_header(self, *args, **kwargs):
        self.header.clear_widgets()
        previous_month = Button(text = "<")
        previous_month.bind(on_press=partial(self.move_previous_month))
        next_month = Button(text = ">", on_press = self.move_next_month)
        next_month.bind(on_press=partial(self.move_next_month))
        month_year_text = self.month_names[self.date.month -1] + ' ' + str(self.date.year)
        current_month = Label(text=month_year_text, size_hint = (2, 1))

        self.header.add_widget(previous_month)
        self.header.add_widget(current_month)
        self.header.add_widget(next_month)

    def populate_body(self, *args, **kwargs):
        self.body.clear_widgets()
        date_cursor = date(self.date.year, self.date.month, 1)
        for filler in range(date_cursor.isoweekday()-1):
            self.body.add_widget(Label(text=""))
        while date_cursor.month == self.date.month:
            date_label = Button(text = str(date_cursor.day))
            date_label.bind(on_press=partial(self.set_date, 
                                                  day=date_cursor.day))
            if self.date.day == date_cursor.day:
                date_label.background_normal, date_label.background_down = date_label.background_down, date_label.background_normal
            self.body.add_widget(date_label)
            date_cursor += timedelta(days = 1)

    def set_date(self, *args, **kwargs):
        self.date = date(self.date.year, self.date.month, kwargs['day'])
        self.populate_body()
        self.populate_header()

        self.clear_widgets()
        self.add_widget(StartPageForm())

        print self.date




    def move_next_month(self, *args, **kwargs):
        if self.date.month == 12:
            self.date = date(self.date.year + 1, 1, self.date.day)
        else:
            self.date = date(self.date.year, self.date.month + 1, self.date.day)
        self.populate_header()
        self.populate_body()

    def move_previous_month(self, *args, **kwargs):
        if self.date.month == 1:
            self.date = date(self.date.year - 1, 12, self.date.day)
        else:
            self.date = date(self.date.year, self.date.month -1, self.date.day)
        self.populate_header()
        self.populate_body()







class BorisRoot(BoxLayout):
    pass


class BorisApp(App):
    subjects = {}
    behaviors = {}
    pass

if __name__ == '__main__':
    BorisApp().run()
