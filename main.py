#!/usr/bin/python3

'''

'''


from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.modalview import ModalView
from kivy.clock import Clock
from kivy.uix.listview import ListView
from kivy.uix.textinput import TextInput

import sys
import json
import time
import codecs
import datetime
#import urllib.request
#import urllib2

NO_FOCAL_SUBJECT = "No focal subject"


class StartPageForm(BoxLayout):

    def exit(self):
        sys.exit()

    def show_SelectProjectForm(self):
        self.clear_widgets()
        self.add_widget(SelectProjectForm())

    def show_SelectProjectView(self):
        self.clear_widgets()
        self.add_widget(SelectProjectView())

    def show_DownloadProject(self):
        self.clear_widgets()
        self.add_widget(DownloadProjectForm())


class DownloadProjectForm(BoxLayout):

    def cancel(self):
        self.clear_widgets()
        self.add_widget(StartPageForm())

    def download_project(self):
        print(self.url_input.text)
        url = "http://penelope.unito.it/archive/boris/files/Lemur_catta_ethogram.boris"
        #response = urllib.request.urlopen(url)
        response = urllib2.urlopen(url)
        print(response.code)
        if response.code == 200:
            txt = response.read()
            print(txt)
            filename = url.rsplit("/", 1)[-1]
            try:
                with open(filename, "wb") as f:
                    f.write(txt)
                popup = Popup(title="OK", content=Label(text="Project downloaded and saved"),   size_hint=(None, None), size=(400, 200))
                popup.open()
            except:
                popup = Popup(title="Error", content=Label(text="Project not saved!"),   size_hint=(None, None), size=(400, 200))
                popup.open()
        else:
            popup = Popup(title="Error", content=Label(text="Project file can not be downloaded!"),   size_hint=(None, None), size=(400, 200))
            popup.open()

        self.clear_widgets()
        self.add_widget(StartPageForm())


class ViewProjectForm(BoxLayout):

    def new_observation(self):

        self.clear_widgets()
        a = StartObservationForm()
        a.obsdate_input.text = "{:%Y-%m-%d %H:%M}".format(datetime.datetime.now())
        self.add_widget(a)


    def go_back(self):
        self.clear_widgets()
        self.add_widget(StartPageForm())



class SelectProjectForm(BoxLayout):

    def cancel(self):
        self.clear_widgets()
        self.add_widget(StartPageForm())

    def open_project(self, path, selection):
        """open project from selected file"""

        if not selection:
            popup = Popup(title="Error", content=Label(text="No project file selected!"), size_hint=(None, None), size=(400, 200))
            popup.open()
            return

        try:
            BorisApp.projectFileName = selection[0]
            BorisApp.project = json.loads(open(BorisApp.projectFileName, "r").read())
        except:
            popup = Popup(title="Error", content=Label(text="The selected file is not a BORIS behaviors file!"),   size_hint=(None, None), size=(400, 200))
            popup.open()
            return

        self.clear_widgets()
        w = ViewProjectForm()
        w.ids.lbl.text = "project file name: {}".format(BorisApp.projectFileName)

        rows =  []
        rows.append("project name: {}".format(BorisApp.project["project_name"]))
        rows.append("project date: {}".format(BorisApp.project["project_date"].replace("T", " ")))
        rows.append("project description: {}".format(BorisApp.project["project_description"]))
        rows.append("Number of behaviors: {}".format(len(BorisApp.project["behaviors_conf"].keys())))
        if "behavioral_categories" in BorisApp.project:
            rows.append("Number of behavior categories: {}".format(len(BorisApp.project["behavioral_categories"])))
        rows.append("Number of subjects: {}".format(len(BorisApp.project["subjects_conf"].keys())))
        rows.append("Number of observations: {}".format(len(BorisApp.project["observations"].keys())))

        w.ids.projectslist.item_strings = rows
        self.add_widget(w)

        '''
        self.clear_widgets()
        a = StartObservationForm()
        a.obsdate_input.text = "{:%Y-%m-%d %H:%M}".format(datetime.datetime.now())
        self.add_widget(a)
        '''


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
    mem = {}

    def cancel(self):
        self.clear_widgets()
        self.add_widget(StartPageForm())

    def go_back(self, obj):
        print("go back")

        print("mem obs id", self.mem)
        self.clear_widgets()
        w = StartObservationForm()
        w.obsid_input.text = self.mem["obsId"]
        w.obsdate_input.text = self.mem["obsDate"]
        w.obsdescription_input.text = self.mem["obsDescription"]
        self.add_widget(w)


    def indep_var(self):
        """
        show independent variables
        """


        self.mem = {"obsId": self.obsid_input.text, "obsDate": self.obsdate_input.text, "obsDescription":self.obsdescription_input.text}
        print("mem :", self.mem)

        layout = BoxLayout(orientation="vertical")
        lb = Label(text="Independent variables", size_hint_y=0.1)
        layout.add_widget(lb)

        if "independent_variables" in BorisApp.project:
            for idx in BorisApp.project["independent_variables"]:
                layout1 = BoxLayout(orientation="horizontal")
                s = BorisApp.project["independent_variables"][idx]["label"]
                if BorisApp.project["independent_variables"][idx]["description"]:
                    s += " ({})".format(BorisApp.project["independent_variables"][idx]["description"])
                lb1 = Label(text=s)
                layout1.add_widget(lb1)

                ti = TextInput(text=BorisApp.project["independent_variables"][idx]["default value"], multiline=False)
                layout1.add_widget(ti)

                layout.add_widget(layout1)


        layout2 = BoxLayout(orientation="vertical", height="40dp", size_hint_y=None)
        btn = Button(text="Go back", size_hint_x=1)
        btn.bind(on_release = self.go_back)
        btn.background_color = [1, 1, 1, 1]
        layout2.add_widget(btn)

        layout.add_widget(layout2)

        self.clear_widgets()
        self.add_widget(layout)


    def start(self):

        def view_behaviors_layout(obj):
            self.clear_widgets()
            self.add_widget(self.behaviorsLayout)


        def view_subjects_layout(obj):
            self.clear_widgets()
            self.add_widget(self.subjectsLayout)
            print("current focal subject:", self.focal_subject)


        def btnBehaviorPressed(obj):
            """
            behavior button pressed
            """
            t = time.time()
            out = ""
            newState = obj.text

            # state event
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

            print("clicked button", obj.text)

            # set focal subject
            if self.focal_subject and self.focal_subject != NO_FOCAL_SUBJECT:
                self.btnSubjectsList[ self.focal_subject ].background_color = [1, 1, 1, 1]

            # deselect already selected subject
            if obj.text == self.focal_subject:
                self.focal_subject = NO_FOCAL_SUBJECT
            else:
                self.focal_subject = obj.text
                obj.background_color = [5, 1, 1, 1]

            print("new focal subject:", self.focal_subject)
            btnSelSubj.text = self.focal_subject
            # show behaviors
            '''
            self.clear_widgets()
            self.add_widget(self.behaviorsLayout)
            '''
            view_behaviors_layout(None)


        def btnStopPressed(obj):

            def my_callback(instance):
                if instance.title == "y":
                    try:
                        #f = open(self.obsId +".boris", "w")
                        f = open(BorisApp.projectFileName, "w")
                        f.write(json.dumps(BorisApp.project, indent=1))
                        f.close()

                        popup = Popup(title="Observation saved", content=Label(text="Observation saved in {}".format(BorisApp.projectFileName)),   size_hint=(None, None), size=(400, 200))
                        popup.open()

                    except:

                        print("The observation {} can not be saved!".format(self.obsId))
                        popup = Popup(title="Error", content=Label(text="The observation {} can not be saved!".format(self.obsId)), size_hint=(None, None), size=(400, 200))
                        popup.open()

                    self.clear_widgets()
                    self.add_widget(StartPageForm())

            pop = ConfirmStopPopup()
            pop.bind(on_dismiss=my_callback)
            pop.open()


        def clock_callback(dt):
            print('clock')
        # create file for observations

        if not self.obsid_input.text:
            p = Popup(title="Error", content=Label(text="The observation id is empty"), size_hint=(None, None), size=(400, 200))
            p.open()
            return

        print("obs id:", self.obsid_input.text)
        print("description:", self.obsdescription_input.text)

        self.obsId = self.obsid_input.text
        BorisApp.project["observations"][self.obsId] = {"date": self.obsdate_input.text,
                                                        "close_behaviors_between_videos": False,
                                                        "time offset": 0.0,
                                                        "scan_sampling_time": 0,
                                                        "time offset second player": 0.0,
                                                        "description": self.obsdescription_input.text,
                                                        "file": [],
                                                        "events": [],
                                                        "visualize_spectrogram": False,
                                                        "type": "LIVE",
                                                        "independent_variables": {}}

        # create layout with subject buttons
        if BorisApp.project["subjects_conf"]:

            subjectsList = sorted([BorisApp.project["subjects_conf"][k]["name"] for k in BorisApp.project["subjects_conf"].keys()])

            # check number of subjects
            subjects_font_size = 24
            if len(subjectsList) > 20:
                subjects_font_size = 14

            self.subjectsLayout = GridLayout(cols= int((len(subjectsList) + 1)**0.5) , size_hint=(1, 1), spacing=5)
            btn = Button(text=NO_FOCAL_SUBJECT, size_hint_x=1, font_size=subjects_font_size)
            btn.bind(on_release = btnSubjectPressed)
            for subject in subjectsList:
                btn = Button(text=subject, size_hint_x=1, font_size=subjects_font_size)
                btn.background_color = [1, 1, 1, 1]
                btn.bind(on_release = btnSubjectPressed)
                self.btnSubjectsList[subject] = btn
                self.subjectsLayout.add_widget(btn)

            # cancel button
            btn = Button(text = "Cancel", size_hint_x=1, font_size=subjects_font_size)
            btn.background_color = [1, 0, 0, 1] # red
            btn.bind(on_release = view_behaviors_layout)
            self.subjectsLayout.add_widget(btn)


        # create layout with behavior buttons
        self.behaviorsLayout = GridLayout(cols= int((len(BorisApp.project["behaviors_conf"]) + 1)**0.5) , size_hint=(1,1), spacing=5)

        behaviorsList = sorted([BorisApp.project["behaviors_conf"][k]["code"] for k in BorisApp.project["behaviors_conf"].keys()])

        # check number of behaviors
        behaviors_font_size = 24
        if len(behaviorsList) > 20:
            behaviors_font_size = 14


        if "behavioral_categories" in BorisApp.project:
            colors_list = [[1,.2,.2, 1], [.1, 0.8, .1, 1], [.1, .1, 1, 1], [0.94, 0.35, 0.48, 1]]
            categoriesList = set([BorisApp.project["behaviors_conf"][k]["category"] for k in BorisApp.project["behaviors_conf"].keys() if "category" in BorisApp.project["behaviors_conf"][k]])
            print(sorted(categoriesList))
            for idx, category in enumerate(sorted(categoriesList)):
                behav_list_category = sorted([BorisApp.project["behaviors_conf"][k]["code"] for k in BorisApp.project["behaviors_conf"].keys() if "category" in BorisApp.project["behaviors_conf"][k] and BorisApp.project["behaviors_conf"][k]["category"] == category])
                for behavior in behav_list_category:
                    btn = Button(text=behavior, size_hint_x=1, font_size=behaviors_font_size)
                    #btn.background_color = [idx, 1, 1, 1]   #hex('#03A9F4')
                    btn.background_normal = ""
                    btn.background_color = colors_list[idx % len(colors_list)]
                    btn.bind(on_release = btnBehaviorPressed)
                    self.btnList[behavior] = btn
                    self.behaviorsLayout.add_widget(btn)

        else:
            for behavior in behaviorsList:
                btn = Button(text=behavior, size_hint_x=1, font_size=behaviors_font_size)
                btn.background_color = [1, 1, 1, 1]
                btn.bind(on_release = btnBehaviorPressed)
                self.btnList[behavior] = btn
                self.behaviorsLayout.add_widget(btn)

        # add subject button
        if BorisApp.project["subjects_conf"]:
            btnSelSubj = Button(text = "Select\nsubject", size_hint_x=1, font_size=behaviors_font_size)
            btnSelSubj.background_normal = ""
            btnSelSubj.background_color = [0, 1, 0, 1] # green
            btnSelSubj.bind(on_release = view_subjects_layout)
            self.behaviorsLayout.add_widget(btnSelSubj)

        # add stop button
        btn = Button(text = "Stop obs", size_hint_x=1, font_size=behaviors_font_size)
        btn.background_normal = ""
        btn.background_color = [1, 0, 0, 1] # red
        btn.bind(on_release = btnStopPressed)
        self.behaviorsLayout.add_widget(btn)

        self.clear_widgets()
        self.add_widget(self.behaviorsLayout)

        self.t0 = time.time()

        # start timer
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
    projectFileName = ""
    pass

if __name__ == "__main__":
    BorisApp().run()

