

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.modalview import ModalView
from kivy.clock import Clock

import sys
import json
import time
import codecs
import datetime

NO_FOCAL_SUBJECT = 'No focal subject'


class StartPageForm(BoxLayout):

    def exit(self):
        sys.exit()

    def show_SelectProjectForm(self):
        self.clear_widgets()
        self.add_widget(SelectProjectForm())

    def show_SelectObservationForm(self):
        self.clear_widgets()
        self.add_widget(SelectObservationForm())


class SelectObservationForm(BoxLayout):
    def cancel(self):
        self.clear_widgets()
        self.add_widget(StartPageForm())

    def view_events(self, selection):
        print( selection[0])

        try:
            events = open( selection[0], "r").readlines()
            print( 'events:', events)
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
        print( kwargs)
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

class SelectProjectForm(BoxLayout):

    def cancel(self):
        self.clear_widgets()
        self.add_widget(StartPageForm())

    def load_project(self, path, selection):
        """load project from selected file"""

        if not selection:
            popup = Popup(title="Error", content=Label(text="No project file selected!"), size_hint=(None, None), size=(400, 200))
            popup.open()
            return
        try:
            BorisApp.project = json.loads(open(selection[0], "r").read())
        except:
            popup = Popup(title="Error", content=Label(text="The selected file is not a BORIS behaviors file!"),   size_hint=(None, None), size=(400, 200))
            popup.open()
            return

        self.clear_widgets()

        a = StartObservationForm()
        a.obsdate_input.text = "{:%Y-%m-%d %H:%M}".format(datetime.datetime.now())
        self.add_widget(a)


def behaviorType(ethogram, behavior):
    return [ ethogram[k]["type"] for k in ethogram.keys() if ethogram[k]["code"] == behavior][0]

def behaviorExcluded(ethogram, behavior):
    return [ ethogram[k]["excluded"] for k in ethogram.keys() if ethogram[k]["code"] == behavior][0].split(",")


class StartObservationForm(BoxLayout):

    t0 = 0 # initial time
    fileName = ""
    currentStates = []
    focal_subject = ""
    btnList = {}
    btnSubjectsList = {}
    behaviorsLayout = ""
    subjectsLayout = ""
    obsId = ""


    def cancel(self):
        self.clear_widgets()
        self.add_widget(StartPageForm())

    def start(self):

        def btnBehaviorPressed(obj):
            """
            behavior button pressed
            """
            t = time.time()
            out = ''
            newState = obj.text

            # state event
            #if BorisApp.behaviors[ newState ]['type'] == 'state':
            if "State" in behaviorType(BorisApp.project["behaviors_conf"], newState):
                if newState in self.currentStates:
                    #out += "{time}\t{subject}\t{state}\tSTOP\n".format(time=round(t - self.t0, 3), subject=self.focal_subject, state=newState)
                    BorisApp.project["observations"][self.obsId]["events"].append([round(t - self.t0, 3), self.focal_subject, newState, "", ""])
                    obj.background_color = [1, 1, 1, 1]
                    self.currentStates.remove(newState)
                else:
                    # test if state is exclusive
                    #if BorisApp.behaviors[ newState ]['exclude']:

                    if behaviorExcluded(BorisApp.project["behaviors_conf"], newState) != [""]:
                        statesToStop = []

                        for cs in self.currentStates:
                            if cs in behaviorExcluded(BorisApp.project["behaviors_conf"], newState):
                                #out += "{time}\t{subject}\t{state}\tSTOP\n".format(time=round(t - self.t0, 3), state=cs, subject=self.focal_subject)
                                BorisApp.project["observations"][self.obsId]["events"].append([round(t - self.t0, 3), self.focal_subject, cs, "", ""])
                                statesToStop.append(cs)
                                self.btnList[cs].background_color = [1,1,1,1]

                        for s in statesToStop:
                            self.currentStates.remove(s)


                    BorisApp.project["observations"][self.obsId]["events"].append([round(t - self.t0, 3), self.focal_subject, newState, "", ""])

                    obj.background_color = [5, 1, 1, 1]
                    self.currentStates.append(newState)

            # point event
            if "Point" in behaviorType(BorisApp.project["behaviors_conf"], newState):
                BorisApp.project["observations"][self.obsId]["events"].append([round(t - self.t0, 3), self.focal_subject, newState, "", ""])

            print(BorisApp.project["observations"] )


        def btnSubjectPressed(obj):
            """
            subject button pressed
            """
            # set focal subject
            if self.focal_subject and self.focal_subject != NO_FOCAL_SUBJECT:
                self.btnSubjectsList[ self.focal_subject ].background_color = [1, 1, 1, 1]

            if obj.text == self.focal_subject:
                # set focal subject to NO_FOCAL_SUBJECT
                self.focal_subject == NO_FOCAL_SUBJECT
            else:
                self.focal_subject = obj.text
                obj.background_color = [5, 1, 1, 1]

            print( "focal subject:", self.focal_subject )
            # show behaviors
            self.clear_widgets()
            self.add_widget(self.behaviorsLayout)


        def btnStopPressed(obj):

            def my_callback(instance):
                if instance.title == "y":

                    try:
                        f = open("test.boris", "w")
                        f.write(json.dumps(BorisApp.project, indent=1))
                        f.close()
                    except:

                        print("Project can not be saved!")
                        popup = Popup(title="Error", content=Label(text="Project can not be saved!"), size_hint=(None, None), size=(400, 200))
                        popup.open()

                    self.clear_widgets()
                    self.add_widget(StartPageForm())

            pop = ConfirmStopPopup()
            pop.bind(on_dismiss=my_callback)
            pop.open()


        def view_subjects_layout(obj):
            self.clear_widgets()
            self.add_widget(self.subjectsLayout)

        def clock_callback(dt):
            print('clock')
        # create file for observations

        if not self.obsid_input.text:
            p = Popup(title="Error", content=Label(text="The observation id is empty"), size_hint=(None, None), size=(400, 200))
            p.open()
            return

        self.obsId = self.obsid_input.text
        BorisApp.project["observations"][self.obsId] = {"date": self.obsdate_input.text, "events": []}

        # create layout with subject buttons
        if BorisApp.project["subjects_conf"]:

            subjectsList = sorted([ BorisApp.project["subjects_conf"][k]['name']  for k in BorisApp.project["subjects_conf"].keys()])

            self.subjectsLayout = GridLayout(cols= int((len(subjectsList) + 1)**0.5) , size_hint=(1, 1), spacing=5)
            btn = Button(text=NO_FOCAL_SUBJECT, size_hint_x=1, font_size=24)
            btn.bind(on_release = btnSubjectPressed)
            for subject in subjectsList:
                btn = Button(text=subject, size_hint_x=1, font_size=24)
                btn.background_color = [1, 1, 1, 1]
                btn.bind(on_release = btnSubjectPressed)
                self.btnSubjectsList[subject] = btn
                self.subjectsLayout.add_widget(btn)


        # create layout with behavior buttons
        self.behaviorsLayout = GridLayout(cols= int((len(BorisApp.project["behaviors_conf"]) + 1)**0.5) , size_hint=(1,1), spacing=5)

        behaviorsList = sorted([BorisApp.project["behaviors_conf"][k]["code"] for k in BorisApp.project["behaviors_conf"].keys()])

        for behavior in behaviorsList:
            btn = Button(text=behavior, size_hint_x=1, font_size=24)
            btn.background_color = [1, 1, 1, 1]
            btn.bind(on_release = btnBehaviorPressed)
            self.btnList[behavior] = btn
            self.behaviorsLayout.add_widget(btn)

        btn = Button(text = "Select subject", size_hint_x = 1, font_size = 24)
        btn.background_color = [ 0,1,0,1 ]
        btn.bind(on_release = view_subjects_layout)
        self.behaviorsLayout.add_widget(btn)

        btn = Button(text = "Stop obs", size_hint_x = 1, font_size = 24)
        btn.background_color = [ 1,0,0,1 ]
        btn.bind(on_release = btnStopPressed)
        self.behaviorsLayout.add_widget(btn)

        self.clear_widgets()
        self.add_widget(self.behaviorsLayout)

        self.t0 = time.time()

        Clock.schedule_interval(clock_callback, 60)


class ConfirmStopPopup(Popup):
    def yes(self):
        self.title = "y"
        self.dismiss()

    def no(self):
        self.title = "n"
        self.dismiss()


class BorisRoot(BoxLayout):
    pass

class BorisApp(App):
    project = {}
    pass

if __name__ == '__main__':
    BorisApp().run()
