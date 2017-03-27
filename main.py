#!/usr/bin/python2

'''
BORIS mobile
Behavioral Observation Research Interactive Software
Copyright 2017 Olivier Friard

This file is part of BORIS mobile.

  BORIS is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 3 of the License, or
  any later version.

  BORIS mobile is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not see <http://www.gnu.org/licenses/>.

  www.boris.unito.it
'''

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.modalview import ModalView
from kivy.clock import Clock
from kivy.uix.listview import ListView
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown
from kivy.properties import StringProperty

import os
import sys
import json
import time
import codecs
import datetime
import urllib2
import socket
import time

NO_FOCAL_SUBJECT = "No focal subject"
OBSERVATIONS = "observations"
SUBJECTS = "subjects_conf"
ETHOGRAM = "behaviors_conf"

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


class StartPageForm(BoxLayout):

    def exit(self):
        sys.exit()

    def show_SelectProjectForm(self):
        self.clear_widgets()
        self.add_widget(SelectProjectForm())

    def show_DownloadProject(self):
        self.clear_widgets()
        d = DownloadProjectForm()
        self.add_widget(d)


class SelectObservationToSendForm(BoxLayout):

    def send_observation(self):
        self.clear_widgets()
        self.add_widget(SendObsForm())


class SendObsForm(BoxLayout):

    def cancel(self):
        self.clear_widgets()
        self.add_widget(StartPageForm())


    def send_obs(self):

        def send_to_boris(url, observations):

            BUFFER_SIZE = 1024

            def decimal_default(obj):
                if isinstance(obj, Decimal):
                    return float(obj)
                raise TypeError

            try:
                TCP_IP, TCP_PORT = url.split(":")
                TCP_PORT = int(TCP_PORT)
            except:
                return False

            MSG = str.encode(str(json.dumps(observations,
                                            indent=None,
                                            separators=(",", ":"),
                                            default=decimal_default)))

            s = socket.socket()

            try:
                s.connect((TCP_IP, int(TCP_PORT)))
                s.send("put")
            except:
                print("socket error")
                return False

            print("sent ",MSG)

            received = ""
            while 1:
                data = s.recv(BUFFER_SIZE)
                if not data:
                    break
                received += data

            print "received:\n" + received

            if received == "SEND":
                print("sending")

                s = socket.socket()
                s.connect((TCP_IP, int(TCP_PORT)))
                s.send(MSG + b"#####")
                print("sent")
                while 1:
                    data = s.recv(BUFFER_SIZE)
                    if not data:
                        break

            s.close
            return True


        print "obsid", self.obsId

        url = self.url_input.text

        if not url:
            popup = Popup(title="Error", content=Label(text="The URL is empty!"),
                                         size_hint=(None, None),
                                         size=(400, 200))
            popup.open()
            return


        if url.count(":") != 1:
            popup = Popup(title="Error", content=Label(text="The URL is not well formed!\nExample: 192.168.1.1:1234"),
                                         size_hint=(None, None),
                                         size=(400, 200))
            popup.open()
            return


        if BorisApp.project[OBSERVATIONS]:
            if send_to_boris(url, {self.obsId: BorisApp.project[OBSERVATIONS][self.obsId]}):
                popup = Popup(title="Info", content=Label(text="Observation sent successfully"),
                                             size_hint=(None, None),
                                             size=(400, 200))
            else:
                popup = Popup(title="Error", content=Label(text="Observation not sent"),
                                         size_hint=(None, None),
                                         size=(400, 200))
            popup.open()

        else:
            popup = Popup(title="Error", content=Label(text="No observations were found in the selected project"),
                                         size_hint=(None, None),
                                         size=(400, 200))
            popup.open()

        self.clear_widgets()
        self.add_widget(StartPageForm())


class DownloadProjectForm(BoxLayout):

    def cancel(self):
        self.clear_widgets()
        self.add_widget(StartPageForm())

    def download_project(self):

        def download_from_boris(url):
            try:
                TCP_IP, TCP_PORT = url.split(":")
                TCP_PORT = int(TCP_PORT)
            except:
                return None

            BUFFER_SIZE = 1024

            s = socket.socket()

            s.connect((TCP_IP, int(TCP_PORT)))
            s.send(str.encode("get"))

            received = ""
            while 1:
                data = s.recv(BUFFER_SIZE)
                if not data:
                    break
                received += data

            print "received:\n" + received
            s.close

            return received


        def save_project_file(filename, content):
            try:
                with open(filename, "wb") as f:
                    f.write(content)
                popup = Popup(title="Success", content=Label(text="Project downloaded and saved as:\n'{}'".format(filename)),   size_hint=(None, None), size=(400, 200))
                popup.open()
            except:
                popup = Popup(title="Error", content=Label(text="Project not saved!"),   size_hint=(None, None), size=(400, 200))
                popup.open()


        def choose_for_existing_file(instance):
            print(instance.title)
            if instance.title == "cancel":
                return
            if instance.title == "overwrite":
                save_project_file(self.filename, self.content)
                return
            if instance.title == "rename":
                save_project_file( "{}.{}.boris".format(self.filename, datetime.datetime.now().isoformat("_").split(".")[0].replace(":","")), self.content)
                return

        url = self.url_input.text

        if not url:
            popup = Popup(title="Error", content=Label(text="The URL is empty!"),
                                         size_hint=(None, None),
                                         size=(400, 200))
            popup.open()
            return

        # from site
        if not self.cb_input.active:
            response = urllib2.urlopen(url)
            self.content = response.read()
        # from BORIS
        else:
            if url.count(":") != 1:
                popup = Popup(title="Error", content=Label(text="The URL is not well formed!\nExample: 192.168.1.1:1234"),
                                             size_hint=(None, None),
                                             size=(400, 200))
                popup.open()
                return

            self.content = download_from_boris(url)
            if self.content is None:
                popup = Popup(title="Error", content=Label(text="The URL is not well formed!\nExample: 192.168.1.1:1234"),
                                             size_hint=(None, None),
                                             size=(400, 200))
                popup.open()
                return


        if self.content:
            if self.cb_input.active: # from BORIS
                try:
                    decoded = json.loads(self.content)
                except:
                    popup = Popup(title="Error", content=Label(text="Error in BORIS project!"),
                                                 size_hint=(None, None),
                                                 size=(400, 200))
                    popup.open()
                    return
                if "project_name" in decoded and decoded["project_name"]:
                    self.filename = decoded["project_name"] + ".boris"
                else:
                    self.filename = "NONAME_" + datetime.datetime.now().isoformat("_").split(".")[0].replace(":","") + ".boris"
            else:
                self.filename = url.rsplit("/", 1)[-1]

            if os.path.isfile(self.filename):
                print("file exists!")

                pop = AskForExistingFile()
                pop.title = "The project '{}' already exists on this device".format(self.filename)
                #pop.content=Label(text='Hello world')
                pop.bind(on_dismiss=choose_for_existing_file)
                pop.open()

            else:
                save_project_file(self.filename, self.content)

        else:
            popup = Popup(title="Error", content=Label(text="Project file can not be downloaded!"),   size_hint=(None, None), size=(400, 200))
            popup.open()

        self.clear_widgets()
        self.add_widget(StartPageForm())


class ViewProjectForm(BoxLayout):

    selected_item = StringProperty('no selection')

    def selection_changed(self, *args):
        self.selected_item = args[0].selection[0].text

    def on_selected_item(self, *args):
        print 'selected item text', args[1]
        self.clear_widgets()
        w = SendObsForm()
        w.obsId = args[1]
        w.label2.text = "Observation: %s" % args[1]
        self.add_widget(w)


    def send_observations(self):


        self.clear_widgets()
        w = SelectObservationToSendForm()


        w.ids.lbl.text = "project file name: {}".format(BorisApp.projectFileName)

        rows =  []
        for obsId in BorisApp.project[OBSERVATIONS]:
            rows.append(obsId)
        w.observations_list.adapter.data = rows

        w.observations_list.adapter.bind(on_selection_change=self.selection_changed)

        self.add_widget(w)




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
            popup = Popup(title="Error", content=Label(text="No project file selected!"),
                          size_hint=(None, None), size=(400, 200))
            popup.open()
            return

        try:
            BorisApp.projectFileName = selection[0]
            BorisApp.project = json.loads(open(BorisApp.projectFileName, "r").read())
        except:
            popup = Popup(title="Error", content=Label(text="The selected file is not a BORIS behaviors file!"),
                          size_hint=(None, None), size=(400, 200))
            popup.open()
            return

        if not BorisApp.project[ETHOGRAM]:
            popup = Popup(title="Error", content=Label(text="The ethogram of this project is empty!"),
                          size_hint=(None, None), size=(400, 200))
            popup.open()
            return

        self.clear_widgets()
        w = ViewProjectForm()
        w.ids.lbl.text = "project file name: {}".format(BorisApp.projectFileName)

        rows =  []
        rows.append("project name: {}".format(BorisApp.project["project_name"]))
        rows.append("project date: {}".format(BorisApp.project["project_date"].replace("T", " ")))
        rows.append("project description: {}".format(BorisApp.project["project_description"]))
        rows.append("Number of behaviors: {}".format(len(BorisApp.project[ETHOGRAM].keys())))
        if "behavioral_categories" in BorisApp.project:
            rows.append("Number of behavior categories: {}".format(len(BorisApp.project["behavioral_categories"])))
        rows.append("Number of subjects: {}".format(len(BorisApp.project[SUBJECTS].keys())))
        rows.append("Number of observations: {}".format(len(BorisApp.project[OBSERVATIONS].keys())))

        w.ids.projectslist.item_strings = rows
        self.add_widget(w)



def behaviorType(ethogram, behavior):
    return [ ethogram[k]["type"] for k in ethogram.keys() if ethogram[k]["code"] == behavior][0]

def behaviorExcluded(ethogram, behavior):
    return [ ethogram[k]["excluded"] for k in ethogram.keys() if ethogram[k]["code"] == behavior][0].split(",")



class StartObservationForm(BoxLayout):

    t0 = 0 # initial time
    focal_subject = NO_FOCAL_SUBJECT
    btnList, btnSubjectsList, mem, behavior_color, currentStates, modifiers = {}, {}, {}, {}, {}, {}
    fileName, obsId, behaviorsLayout, subjectsLayout = "", "", "", ""

    time_ = 0
    behav_ = ""
    iv = {}

    def cancel(self):
        self.clear_widgets()
        self.add_widget(StartPageForm())


    def go_back(self, obj):
        """
        return to 'start observation' screen
        """

        print("go back", obj)
        print("mem obs id", self.mem)

        # check if numeric indep var values are numeric
        if "independent_variables" in BorisApp.project:
            for idx in BorisApp.project["independent_variables"]:
                if BorisApp.project["independent_variables"][idx]["label"] in self.iv:
                    if (BorisApp.project["independent_variables"][idx]["type"] == "numeric" and
                       self.iv[BorisApp.project["independent_variables"][idx]["label"]].text):
                        try:
                            _ = float(self.iv[BorisApp.project["independent_variables"][idx]["label"]].text)
                        except:
                            p = Popup(title="Error", content=Label(text="The variable '{}' must be numeric".format(BorisApp.project["independent_variables"][idx]["label"])),
                                      size_hint=(None, None), size=(400, 200))
                            p.open()
                            return


        self.clear_widgets()
        w = StartObservationForm()
        w.obsid_input.text = self.mem["obsId"]
        w.obsdate_input.text = self.mem["obsDate"]
        w.obsdescription_input.text = self.mem["obsDescription"]
        self.add_widget(w)


    def indep_var(self):
        """
        input independent variables
        """

        self.mem = {"obsId": self.obsid_input.text, "obsDate": self.obsdate_input.text, "obsDescription": self.obsdescription_input.text}
        print("mem :", self.mem)

        layout = BoxLayout(orientation="vertical")
        lb = Label(text="Independent variables", size_hint_y=0.1)
        layout.add_widget(lb)

        if "independent_variables" in BorisApp.project:
            for idx in BorisApp.project["independent_variables"]:
                layout1 = BoxLayout(orientation="horizontal")
                s = BorisApp.project["independent_variables"][idx]["label"]
                if BorisApp.project["independent_variables"][idx]["description"]:
                    s += "\n({})".format(BorisApp.project["independent_variables"][idx]["description"])
                lb1 = Label(text=s, size_hint_x=1, font_size=20)
                layout1.add_widget(lb1)

                ti = TextInput(text=BorisApp.project["independent_variables"][idx]["default value"], multiline=False, size_hint_x=1, font_size=25)
                self.iv[BorisApp.project["independent_variables"][idx]["label"]] = ti
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
        """
        start new observation
        """

        def view_behaviors_layout(obj):
            """
            display behaviors page
            """
            self.clear_widgets()
            for behavior in self.btnList:
                self.btnList[behavior].background_color = self.behavior_color[behavior]

            if self.focal_subject in self.currentStates:
                print(self.currentStates[self.focal_subject])
                for cs in self.currentStates[self.focal_subject]:
                    self.btnList[cs].background_color = [1, 0, 0, 1] # red

            self.add_widget(self.behaviorsLayout)


        def view_subjects_layout(obj):
            """
            display subjects page
            """
            self.clear_widgets()
            self.add_widget(self.subjectsLayout)
            print("current focal subject:", self.focal_subject)


        def write_event(event):
            #print("event", event)
            t, newState, modifier = event

            if "State" in behaviorType(BorisApp.project[ETHOGRAM], newState):

                # deselect
                if self.focal_subject in self.currentStates and newState in self.currentStates[self.focal_subject]:
                    BorisApp.project[OBSERVATIONS][self.obsId]["events"].append([round(t - self.t0, 3), self.focal_subject, newState, modifier, ""])
                    #obj.background_color = self.behavior_color[newState]

                    self.btnList[newState].background_color = self.behavior_color[newState]

                    self.currentStates[self.focal_subject].remove(newState)

                # select
                else:
                    # test if state is exclusive
                    if behaviorExcluded(BorisApp.project[ETHOGRAM], newState) != [""]:
                        statesToStop = []

                        if self.focal_subject in self.currentStates:
                            for cs in self.currentStates[self.focal_subject]:
                                if cs in behaviorExcluded(BorisApp.project[ETHOGRAM], newState):
                                    BorisApp.project[OBSERVATIONS][self.obsId]["events"].append([round(t - self.t0, 3), self.focal_subject, cs, "", ""])
                                    statesToStop.append(cs)
                                    self.btnList[cs].background_color = self.behavior_color[cs]

                            for s in statesToStop:
                                self.currentStates[self.focal_subject].remove(s)

                    BorisApp.project[OBSERVATIONS][self.obsId]["events"].append([round(t - self.t0, 3), self.focal_subject, newState, modifier, ""])

                    #obj.background_color = [1, 0, 0, 1] # red
                    self.btnList[newState].background_color = [1, 0, 0, 1] # red


                    if self.focal_subject not in self.currentStates:
                        self.currentStates[self.focal_subject] = []
                    self.currentStates[self.focal_subject].append(newState)

            # point event
            if "Point" in behaviorType(BorisApp.project[ETHOGRAM], newState):
                BorisApp.project[OBSERVATIONS][self.obsId]["events"].append([round(t - self.t0, 3), self.focal_subject, newState, modifier, ""])

            print("current state", self.currentStates)

            print(BorisApp.project[OBSERVATIONS][self.obsId]["events"][-1])


        def btnBehaviorPressed(obj):
            """
            behavior button pressed
            """

            selected_modifier = ""

            def callback(obj):

                print("selected_modifier", obj.text)

                if obj.text != "Go back":
                    selected_modifier = obj.text
                else:
                    selected_modifier = ""
                popup.dismiss()
                write_event([self.time_, self.behav_, selected_modifier])

            t = time.time()
            newState = obj.text

            self.time_ = t
            self.behav_ = newState

            # check if modifiers
            if self.modifiers[newState]:

                popup = Popup()
                anchor_layout = BoxLayout(orientation="vertical")

                font_size = 24
                if len(self.modifiers[obj.text].split(",")) > 10:
                    font_size = 14

                for modif in self.modifiers[obj.text].split(","):
                    btn = Button(text=modif, size_hint=(1, .5), font_size=font_size, on_release=callback)
                    anchor_layout.add_widget(btn)

                btn = Button(text="Go back", size_hint=(1, .1), font_size=14)
                btn.background_color = [1, 0, 0, 1] # red
                btn.bind(on_release=callback)
                anchor_layout.add_widget(btn)

                popup.content=anchor_layout
                popup.open()

            else:
                write_event([t, obj.text, ""])


        def btnSubjectPressed(obj):
            """
            subject button pressed
            """
            print("self.focal_subject", self.focal_subject)
            print("clicked button", obj.text)

            # deselect already selected subject
            if obj.text == self.focal_subject:
                self.btnSubjectsList[self.focal_subject].background_color = [.5, .5, .5, 1] # gray
                self.focal_subject = NO_FOCAL_SUBJECT
            else:
                if self.focal_subject != NO_FOCAL_SUBJECT:
                    self.btnSubjectsList[self.focal_subject].background_color = [.5, .5, .5, 1] # gray
                self.focal_subject = obj.text
                self.btnSubjectsList[self.focal_subject].background_color = [1, 0, 0, 1] # red

            print("new focal subject:", self.focal_subject)
            btnSelSubj.text = self.focal_subject

            print("current states", self.currentStates)
            # show behaviors
            view_behaviors_layout(None)


        def btnStopPressed(obj):

            def my_callback(instance):
                if instance.title == "y":
                    try:
                        with open(BorisApp.projectFileName, "w") as f:
                            f.write(json.dumps(BorisApp.project, indent=1))

                        popup = Popup(title="Observation saved", content=Label(text="Observation saved in {}".format(BorisApp.projectFileName)), size_hint=(None, None), size=(400, 200))
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


        '''
        def clock_callback(dt):
            print('clock')
        '''

        # check if observation id field is empty
        if not self.obsid_input.text:
            p = Popup(title="Error", content=Label(text="The observation id is empty"), size_hint=(None, None), size=(400, 200))
            p.open()
            return

        # check if observation id already exists
        if self.obsid_input.text in BorisApp.project[OBSERVATIONS]:
            p = Popup(title="Error", content=Label(text="This observation id already exists."), size_hint=(None, None), size=(400, 200))
            p.open()
            return

        print("obs id:", self.obsid_input.text)
        print("description:", self.obsdescription_input.text)

        self.obsId = self.obsid_input.text
        BorisApp.project[OBSERVATIONS][self.obsId] = {"date": self.obsdate_input.text,
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

        for label in self.iv:
            BorisApp.project[OBSERVATIONS][self.obsId]["independent_variables"][label] = self.iv[label].text
        print("indep var\n", BorisApp.project[OBSERVATIONS][self.obsId]["independent_variables"])


        # create layout with subject buttons
        if BorisApp.project[SUBJECTS]:

            subjectsList = sorted([BorisApp.project[SUBJECTS][k]["name"] for k in BorisApp.project[SUBJECTS].keys()])

            # check number of subjects
            subjects_font_size = 24
            if len(subjectsList) > 20:
                subjects_font_size = 14

            self.subjectsLayout = GridLayout(cols=int((len(subjectsList) + 1)**0.5), size_hint=(1, 1), spacing=5)
            btn = Button(text=NO_FOCAL_SUBJECT, size_hint_x=1, font_size=subjects_font_size)
            btn.bind(on_release = btnSubjectPressed)
            for subject in subjectsList:
                btn = Button(text=subject, size_hint_x=1, font_size=subjects_font_size)
                btn.background_normal = ""
                btn.background_color = [.5, .5, .5, 1] # gray
                btn.bind(on_release = btnSubjectPressed)
                self.btnSubjectsList[subject] = btn
                self.subjectsLayout.add_widget(btn)

            # cancel button
            btn = Button(text = "Cancel", size_hint_x=1, font_size=subjects_font_size)
            btn.background_color = [1, 0, 0, 1] # red
            btn.bind(on_release = view_behaviors_layout)
            self.subjectsLayout.add_widget(btn)

        # create layout with behavior buttons
        self.behaviorsLayout = BoxLayout(orientation='vertical', spacing=5)

        self.behaviorsLayout.add_widget(Label(text="Observation: {}".format(self.obsId), size_hint_y=0.05))

        gdrid_layout = GridLayout(cols=int((len(BorisApp.project[ETHOGRAM]) + 1)**0.5), size_hint=(1, 1), spacing=5)

        behaviorsList = sorted([BorisApp.project[ETHOGRAM][k]["code"] for k in BorisApp.project[ETHOGRAM].keys()])
        # check modifiers
        for idx in BorisApp.project[ETHOGRAM]:
            self.modifiers[BorisApp.project[ETHOGRAM][idx]["code"]] = BorisApp.project[ETHOGRAM][idx]["modifiers"]

        print("modiifers", self.modifiers)

        # check number of behaviors
        behaviors_font_size = 24
        if len(behaviorsList) > 20:
            behaviors_font_size = 14

        if "behavioral_categories" in BorisApp.project:
            colors_list = [[1.0, 0.6, 0.0, 1], [.1, 0.8, .1, 1], [.1, .1, 1, 1], [0.94, 0.35, 0.48, 1], [0.2, 0.4, 0.6, 1], [0.4, 0.2, 0.6, 1]]
            categoriesList = set([BorisApp.project[ETHOGRAM][k]["category"] for k in BorisApp.project[ETHOGRAM].keys() if "category" in BorisApp.project[ETHOGRAM][k]])

            #print(sorted(categoriesList))

            for idx, category in enumerate(sorted(categoriesList)):
                behav_list_category = sorted([BorisApp.project[ETHOGRAM][k]["code"] for k in BorisApp.project[ETHOGRAM].keys() if "category" in BorisApp.project[ETHOGRAM][k] and BorisApp.project[ETHOGRAM][k]["category"] == category])
                for behavior in behav_list_category:
                    btn = Button(text=behavior, size_hint_x=1, font_size=behaviors_font_size)
                    btn.background_normal = ""
                    if category == "":
                        btn.background_color = [.5, .5, .5, 1] # gray
                    else:
                        btn.background_color = colors_list[idx % len(colors_list)]
                    self.behavior_color[behavior] = btn.background_color
                    btn.bind(on_release = btnBehaviorPressed)
                    self.btnList[behavior] = btn
                    gdrid_layout.add_widget(btn)

        else:
            for behavior in behaviorsList:
                btn = Button(text=behavior, size_hint_x=1, font_size=behaviors_font_size)
                btn.background_normal = ""
                btn.background_color = [.5, .5, .5, 1] # gray
                self.behavior_color[behavior] = btn.background_color
                btn.bind(on_release = btnBehaviorPressed)
                self.btnList[behavior] = btn
                gdrid_layout.add_widget(btn)

        self.behaviorsLayout.add_widget(gdrid_layout)

        hlayout = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        # add subject button
        if BorisApp.project[SUBJECTS]:
            btnSelSubj = Button(text = "Select focal subject", size_hint_x=1, font_size=behaviors_font_size)
            btnSelSubj.background_normal = ""
            btnSelSubj.background_color = [0.1, 0.9, 0.1, 1] # green
            btnSelSubj.bind(on_release = view_subjects_layout)
            hlayout.add_widget(btnSelSubj)

        # add stop button
        btn = Button(text = "Stop obs", size_hint_x=1, font_size=behaviors_font_size)
        btn.background_normal = ""
        btn.background_color = [0.9, 0.1, 0.1, 1] # red
        btn.bind(on_release = btnStopPressed)
        hlayout.add_widget(btn)

        self.behaviorsLayout.add_widget(hlayout)

        self.clear_widgets()
        self.add_widget(self.behaviorsLayout)

        self.t0 = time.time()

        # start timer
        '''
        Clock.schedule_interval(clock_callback, 60)
        '''


class AskForExistingFile(Popup):
    def cancel(self):
        self.title = "cancel"
        self.dismiss()
    def overwrite(self):
        self.title = "overwrite"
        self.dismiss()
    def rename(self):
        self.title = "rename"
        self.dismiss()


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

