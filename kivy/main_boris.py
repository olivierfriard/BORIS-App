"""
BORIS App
Behavioral Observation Research Interactive Software
Copyright 2017-2023 Olivier Friard

This file is part of BORIS mobile.

  BORIS App is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 3 of the License, or
  any later version.

  BORIS App is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not see <http://www.gnu.org/licenses/>.

  www.boris.unito.it
"""

"""
The kivy.uix.listview is deprecated in Kivy v.>=1.11

"""

__version__ = "0.4"
__version_date__ = "2023-02-23"

__copyright__ = f"{__version_date__[:4]} Olivier Friard - Marco Gamba - ALPHA"

from kivy.app import App
from kivy.utils import platform
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.modalview import ModalView
from kivy.clock import Clock
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.filechooser import FileChooserListView

# from kivy.uix.listview import ListItemButton
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown
from kivy.properties import StringProperty
from kivy.logger import Logger
from kivy.base import EventLoop

from kivy.core.window import Window


import os
import sys
import json
import time
import datetime
from urllib.request import urlopen
import socket
import time
from decimal import Decimal

NO_FOCAL_SUBJECT = "No focal subject"
OBSERVATIONS = "observations"
SUBJECTS = "subjects_conf"
ETHOGRAM = "behaviors_conf"
INDEPENDENT_VARIABLES = "independent_variables"
VERSION_URL = "https://raw.githubusercontent.com/olivierfriard/BORIS-App/master/ver.txt"

# modifiers
SINGLE_SELECTION = 0
MULTI_SELECTION = 1
NUMERIC_MODIFIER = 2

selected_modifiers = {}
observation_to_send = ""


class StartPageForm(BoxLayout):
    def show_SelectProjectForm(self):
        self.clear_widgets()
        self.add_widget(SelectProjectForm())

    def show_DownloadProject(self):

        w = DownloadProjectForm()
        if os.path.isfile("server_url.config"):
            w.url_input.text = open("server_url.config").read().strip()
        else:
            w.url_input.text = ""

        self.clear_widgets()
        self.add_widget(w)

    def more(self):
        self.clear_widgets()
        self.add_widget(MoreForm())

    def ver(self):
        return __copyright__


class MoreForm(BoxLayout):
    def cancel(self):
        self.clear_widgets()
        self.add_widget(StartPageForm())

    def about(self):
        """
        check if installed version is the most recent
        update after user confirmation
        """
        info_text = (
            f"BORIS App v. {__version__} - {__version_date__}\n\n"
            f"Copyright (C) {__copyright__}\n"
            "Department of Life Sciences and Systems Biology\n"
            "University of Torino - Italy\n"
            "\n"
            "BORIS is released under the GNU General Public License v.3\n"
            "See www.boris.unito.it for details.\n"
            "\n"
            "The authors would like to acknowledge Valentina Matteucci for her precious help.\n"
            "\n"
            "How to cite BORIS:\n"
            "Friard, O. and Gamba, M. (2016),\nBORIS: a free, versatile open-source event-logging software\n"
            "for video/audio coding and live observations.\n"
            "Methods Ecol Evol, 7: 1325–1330.\n"
            "DOI:10.1111/2041-210X.12584"
        )
        close_button = Button(text=info_text)
        popup = Popup(
            title="About BORIS",
            content=close_button,  # Label(text=info_text),
            size_hint=(1, 1),
        )
        close_button.bind(on_press=popup.dismiss)
        popup.open()

        self.clear_widgets()
        self.add_widget(StartPageForm())

    def exit(self):
        Logger.info("exiting...")
        sys.exit()

    def ver(self):
        return __copyright__


class CustomButton(Button):

    root_widget = ObjectProperty()

    def on_release(self, **kwargs):
        super().on_release(**kwargs)
        self.root_widget.btn_callback(self)


class RV(RecycleView):
    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        print(**kwargs)
        # self.data = [{'text': str(x), 'root_widget': self} for x in observations_list]
        # print(self.data)

    def btn_callback(self, btn):
        print(btn, btn.text)

        global observation_to_send
        observation_to_send = btn.text
        self.clear_widgets()
        self.add_widget(SendObsForm())


class SelectObservationToSendForm(BoxLayout):
    def go_back(self):
        self.clear_widgets()
        self.add_widget(StartPageForm())

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

            MSG = str.encode(str(json.dumps(observations, indent=None, separators=(",", ":"), default=decimal_default)))

            s = socket.socket()

            try:
                s.connect((TCP_IP, int(TCP_PORT)))
                s.send("put")
            except:
                Logger.info("socket error")
                return False

            Logger.info("sent %s" % MSG)

            received = ""
            while 1:
                data = s.recv(BUFFER_SIZE)
                if not data:
                    break
                received += data

            Logger.info("received:\n" + received)

            if received == "SEND":
                Logger.info("Sending")

                s = socket.socket()
                s.connect((TCP_IP, int(TCP_PORT)))
                s.send(MSG + b"#####")
                print("sent")
                Logger.info("sent")
                while 1:
                    data = s.recv(BUFFER_SIZE)
                    if not data:
                        break

            s.close
            return True

        url = self.url_input.text

        if not url:
            Popup(
                title="Error", content=Label(text="The URL is empty!"), size_hint=(None, None), size=("400dp", "200dp")
            ).open()
            return

        if url.count(":") != 1:
            Popup(
                title="Error",
                content=Label(text="The URL is not well formed!\nExample: 192.168.1.1:1234"),
                size_hint=(None, None),
                size=("400dp", "200dp"),
            ).open()
            return

        print(BorisApp.project[OBSERVATIONS])

        if BorisApp.project[OBSERVATIONS]:
            if send_to_boris(url, {self.obsId: BorisApp.project[OBSERVATIONS][self.obsId]}):
                Popup(
                    title="BORIS App - Info",
                    content=Label(text="Observation sent successfully"),
                    size_hint=(None, None),
                    size=("400dp", "200dp"),
                ).open()
            else:
                Popup(
                    title="Error",
                    content=Label(text="Observation not sent"),
                    size_hint=(None, None),
                    size=("400dp", "200dp"),
                ).open()

        else:
            Popup(
                title="Error",
                content=Label(text="No observations were found in the selected project"),
                size_hint=(None, None),
                size=("400dp", "200dp"),
            ).open()

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
                return "", str(sys.exc_info()[0])

            BUFFER_SIZE = 1024

            s = socket.socket()

            try:
                s.connect((TCP_IP, int(TCP_PORT)))
                s.send(str.encode("get"))
            except:
                return "", str(sys.exc_info()[0])

            received = ""
            while 1:
                data = s.recv(BUFFER_SIZE)
                if not data:
                    break
                received += data

            print("received:\n" + received)
            s.close

            return received, ""

        def save_project_file(filename, content):
            try:
                with open(filename, "wb") as f:
                    f.write(content)
                Popup(
                    title="BORIS",
                    content=Label(text="Project downloaded and saved as:\n'{}'".format(filename)),
                    size_hint=(None, None),
                    size=("500dp", "200dp"),
                ).open()
            except:
                Popup(
                    title="BORIS - Error",
                    content=Label(text="Project not saved!"),
                    size_hint=(None, None),
                    size=("400dp", "200dp"),
                ).open()

        def choose_for_existing_file(instance):
            print(instance.title)
            if instance.title == "cancel":
                return
            if instance.title == "overwrite":
                save_project_file(self.filename, self.content)
                return
            if instance.title == "rename":
                save_project_file(
                    "{}.{}.boris".format(
                        self.filename, datetime.datetime.now().isoformat("_").split(".")[0].replace(":", "")
                    ),
                    self.content,
                )
                return

        url = self.url_input.text

        if not url:
            popup = Popup(
                title="Error", content=Label(text="The URL is empty!"), size_hint=(None, None), size=(400, 200)
            )
            popup.open()
            return

        # from site
        if not self.cb_input.active:
            try:
                response = urlopen(url)
                self.content = response.read()
            except:
                popup = Popup(
                    title="Error",
                    content=Label(text="Error: " + str(sys.exc_info()[0])),
                    size_hint=(None, None),
                    size=(400, 200),
                ).open()
                return
        # from BORIS
        else:
            if url.count(":") != 1:
                popup = Popup(
                    title="Error",
                    content=Label(text="The URL is not well formed!\nExample: 192.168.1.1:1234"),
                    size_hint=(None, None),
                    size=(400, 200),
                )
                popup.open()
                return

            self.content, err_msg = download_from_boris(url)
            if err_msg:
                popup = Popup(
                    title="Error", content=Label(text="Error: " + err_msg), size_hint=(None, None), size=(400, 200)
                )
                popup.open()
                return

        if self.content:

            # check if BORIS project
            try:
                decoded = json.loads(self.content)
            except:
                Popup(
                    title="Error",
                    content=Label(text="Error in downloaded file!"),
                    size_hint=(None, None),
                    size=("400dp", "200dp"),
                ).open()
                return
            if "project_name" not in decoded:
                Popup(
                    title="Error",
                    content=Label(text="The downloaded file does not seem to be a BORIS project!"),
                    size_hint=(None, None),
                    size=("400dp", "200dp"),
                ).open()
                return

            if self.cb_input.active:  # from BORIS
                if "project_name" in decoded and decoded["project_name"]:
                    self.filename = decoded["project_name"] + ".boris"
                else:
                    self.filename = (
                        "NONAME_" + datetime.datetime.now().isoformat("_").split(".")[0].replace(":", "") + ".boris"
                    )
            else:
                self.filename = url.rsplit("/", 1)[-1]

            if os.path.isfile(self.filename):
                print("file exists!")
                pop = AskForExistingFile(size=("500dp", "200dp"))
                pop.bind(on_dismiss=choose_for_existing_file)
                pop.open()

            else:  # from site
                save_project_file(self.filename, self.content)

        else:
            Popup(
                title="Error",
                content=Label(text="Project file can not be downloaded!"),
                size_hint=(None, None),
                size=(400, 200),
            ).open()

        self.clear_widgets()
        self.add_widget(StartPageForm())


""" 2021-09
class MyButton(ListItemButton):
    def __init__(self, **kwargs):
        self.font_size = 24

        super(ListItemButton, self).__init__(**kwargs)
"""


class ViewProjectForm(BoxLayout):

    selected_item = StringProperty("no selection")

    def selection_changed(self, *args):
        print("sel changed")
        self.selected_item = args[0].selection[0].text

    def on_selected_item(self, *args):
        print("selected item text", args[1])
        self.clear_widgets()
        w = SendObsForm()
        w.obsId = args[1]
        w.lb_observation_id.text = "Observation: {}".format(args[1])

        if os.path.isfile("server_url.config"):
            w.url_input.text = open("server_url.config").read().strip()
        else:
            w.url_input.text = ""
        self.add_widget(w)

    # ListItemButton

    def send_observations(self):

        if not BorisApp.project[OBSERVATIONS]:
            Popup(
                title="BORIS",
                content=Label(text="The current project do not contain observations"),
                size_hint=(None, None),
                size=("400dp", "200dp"),
            ).open()
            return

        self.clear_widgets()
        # w = SelectObservationToSendForm()

        w = RV()
        w.data = [{"text": str(x), "root_widget": w} for x in sorted(BorisApp.project[OBSERVATIONS].keys())]

        # w.ids.lbl.text = "project file name: {}".format(BorisApp.projectFileName)

        """ 2021-09
        w.observations_list.adapter = ListAdapter(data=sorted(BorisApp.project[OBSERVATIONS].keys()),
                                                  cls=MyButton,
                                                  selection_mode="single")

        w.observations_list.adapter.bind(on_selection_change=self.selection_changed)
        """

        self.add_widget(w)

    def new_observation(self):

        self.clear_widgets()
        a = StartObservationForm()
        a.obsdate_input.text = "{:%Y-%m-%d %H:%M:%S}".format(datetime.datetime.now())
        self.add_widget(a)

    def go_back(self):
        self.clear_widgets()
        self.add_widget(StartPageForm())


class SelectProjectForm(BoxLayout):
    '''
    def __init__(self, *args, **kwargs):
        super(SelectProjectForm, self).__init__(*args, **kwargs)

        if platform == "android":
            # from jnius import autoclass

            # Environment = autoclass("android.os.Environment")
            # sdpath = Environment.getExternalStorageDirectory()

            """
            from android.permissions import request_permissions, Permission

            request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
            """

            """
            from android.storage import primary_external_storage_path
            from android.storage import secondary_external_storage_path

            primary_storage_dir = primary_external_storage_path()
            secondary_external_storage_path = secondary_external_storage_path()
            # os.getenv("EXTERNAL_STORAGE")

            Popup(
                title="info",
                content=Label(text=f"{primary_storage_dir}"),
                size_hint=(None, None),
                size=(400, 200),
            ).open()
            """

            # self.fichoo = FileChooserListView(path=primary_storage_dir, filters=["*.boris"])
            # self.fichoo.show(primary_storage_dir)

        else:
            self.fichoo = FileChooserListView(path=".", filters=["*.boris"])

        # self.add_widget(self.fichoo)
    '''

    def cancel(self):
        self.clear_widgets()
        self.add_widget(StartPageForm())

    def open_project(self, path, selection):
        """
        open project from selected file
        """

        if not selection:
            Popup(
                title="Error", content=Label(text="No project file selected!"), size_hint=(None, None), size=(400, 200)
            ).open()
            return

        try:
            BorisApp.projectFileName = selection[0]
            BorisApp.project = json.loads(open(BorisApp.projectFileName, "r").read())
        except:
            Popup(
                title="Error",
                content=Label(text="The selected file is not a BORIS behaviors file!"),
                size_hint=(None, None),
                size=(400, 200),
            ).open()
            return

        if not BorisApp.project[ETHOGRAM]:
            Popup(
                title="Error",
                content=Label(text="The ethogram of this project is empty!"),
                size_hint=(None, None),
                size=(400, 200),
            ).open()
            return

        self.clear_widgets()
        w = ViewProjectForm()
        w.ids.lbl.text = f"project file path: {BorisApp.projectFileName}"

        rows = []
        rows.append("project name: {}".format(BorisApp.project["project_name"]))
        rows.append("project date: {}".format(BorisApp.project["project_date"].replace("T", " ")))
        rows.append("project description: {}".format(BorisApp.project["project_description"]))
        rows.append("Number of behaviors: {}".format(len(BorisApp.project[ETHOGRAM].keys())))
        if "behavioral_categories" in BorisApp.project:
            rows.append("Number of behavior categories: {}".format(len(BorisApp.project["behavioral_categories"])))
        rows.append("Number of subjects: {}".format(len(BorisApp.project[SUBJECTS].keys())))
        rows.append("Number of observations: {}".format(len(BorisApp.project[OBSERVATIONS].keys())))

        w.ids.project_info.text = "\n".join(rows)
        self.add_widget(w)


def behaviorType(ethogram, behavior):
    return [ethogram[k]["type"] for k in ethogram.keys() if ethogram[k]["code"] == behavior][0]


def behaviorExcluded(ethogram, behavior):
    return [ethogram[k]["excluded"] for k in ethogram.keys() if ethogram[k]["code"] == behavior][0].split(",")


class StartObservationForm(BoxLayout):

    t0 = 0  # initial time
    focal_subject = NO_FOCAL_SUBJECT
    btnList, btnSubjectsList, mem, behavior_color, currentStates, modifiers = {}, {}, {}, {}, {}, {}
    fileName, obsId, behaviorsLayout, subjectsLayout = "", "", "", ""

    time_ = 0
    behav_ = ""
    iv = {}

    def cancel(self):
        self.clear_widgets()
        self.add_widget(StartPageForm())

    def show_start_observation_form(self):
        self.clear_widgets()
        w = StartObservationForm()
        w.obsid_input.text = self.mem["obsId"]
        w.obsdate_input.text = self.mem["obsDate"]
        w.obsdescription_input.text = self.mem["obsDescription"]
        self.add_widget(w)

    def go_back(self, obj):
        """
        return to 'start observation' screen
        """

        print("mem obs id", self.mem)

        # check if numeric indep var values are numeric
        if "independent_variables" in BorisApp.project:
            for idx in BorisApp.project["independent_variables"]:
                if BorisApp.project["independent_variables"][idx]["label"] in self.iv:
                    if (
                        BorisApp.project["independent_variables"][idx]["type"] == "numeric"
                        and self.iv[BorisApp.project["independent_variables"][idx]["label"]].text
                    ):
                        try:
                            _ = float(self.iv[BorisApp.project["independent_variables"][idx]["label"]].text)
                        except:
                            Popup(
                                title="Error",
                                content=Label(
                                    text="The variable '{}' must be numeric".format(
                                        BorisApp.project["independent_variables"][idx]["label"]
                                    )
                                ),
                                size_hint=(None, None),
                                size=(400, 200),
                            ).open()
                            return

        self.show_start_observation_form()

    def indep_var(self):
        """
        input independent variables
        """

        self.mem = {
            "obsId": self.obsid_input.text,
            "obsDate": self.obsdate_input.text,
            "obsDescription": self.obsdescription_input.text,
        }
        if INDEPENDENT_VARIABLES not in BorisApp.project or not BorisApp.project[INDEPENDENT_VARIABLES]:
            Popup(
                title="BORIS",
                content=Label(text="The current project do not have independent variables"),
                size_hint=(None, None),
                size=("400dp", "200dp"),
            ).open()
            self.show_start_observation_form()
            return

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

                ti = TextInput(
                    text=BorisApp.project["independent_variables"][idx]["default value"],
                    multiline=False,
                    size_hint_x=1,
                    font_size="25dp",
                )
                self.iv[BorisApp.project["independent_variables"][idx]["label"]] = ti
                layout1.add_widget(ti)

                layout.add_widget(layout1)

        layout2 = BoxLayout(orientation="vertical", height="40dp", size_hint_y=None)
        btn = Button(text="Go back", size_hint_x=1)
        btn.bind(on_release=self.go_back)
        btn.background_color = [1, 1, 1, 1]
        layout2.add_widget(btn)

        layout.add_widget(layout2)

        self.clear_widgets()
        self.add_widget(layout)

    def start(self):
        """
        start new observation
        """
        self.modifier_buttons = {}
        self.current_modifiers = {}

        def create_modifiers_layout(behavior):
            """
            create modifiers layout for each behavior
            """

            def on_button_release(obj):

                behavior, idx, type_, modifier = self.modifier_buttons[obj]
                if behavior not in self.current_modifiers:
                    self.current_modifiers[behavior] = {}

                if type_ == SINGLE_SELECTION:
                    # all button to grey
                    for o in [
                        o
                        for o in self.modifier_buttons
                        if self.modifier_buttons[o][0] == behavior and self.modifier_buttons[o][1] == idx
                    ]:
                        o.background_color = [0.5, 0.5, 0.5, 1]

                    if idx in self.current_modifiers[behavior]:
                        if (
                            self.current_modifiers[behavior][idx] == []
                            or modifier not in self.current_modifiers[behavior][idx]
                        ):
                            self.current_modifiers[behavior][idx] = [modifier]
                            obj.background_color = [0.9, 0.1, 0.1, 1]  # red
                        else:
                            self.current_modifiers[behavior][idx] = []
                            obj.background_color = [0.5, 0.5, 0.5, 1]
                    else:
                        self.current_modifiers[behavior][idx] = [modifier]
                        obj.background_color = [0.9, 0.1, 0.1, 1]  # red

                if type_ == MULTI_SELECTION:
                    if idx in self.current_modifiers[behavior]:
                        if (
                            self.current_modifiers[behavior][idx] == []
                            or modifier not in self.current_modifiers[behavior][idx]
                        ):
                            self.current_modifiers[behavior][idx].append(modifier)
                            obj.background_color = [0.9, 0.1, 0.1, 1]  # red
                        else:
                            self.current_modifiers[behavior][idx].remove(modifier)
                            obj.background_color = [0.5, 0.5, 0.5, 1]
                    else:
                        self.current_modifiers[behavior][idx] = [modifier]
                        obj.background_color = [0.9, 0.1, 0.1, 1]  # red

                if type_ == NUMERIC_MODIFIER:
                    self.current_modifiers[behavior][idx] = [obj.text]

                print("self.current_modifiers", self.current_modifiers)

            def on_goback_button_release(obj):
                print("self.current_modifiers", self.current_modifiers)
                modifiers = ""
                behavior, _, _ = self.modifier_buttons[obj]
                for idx in sorted([int(k) for k in self.current_modifiers[behavior]]):
                    if modifiers:
                        modifiers += "|"
                    if self.current_modifiers[behavior][str(idx)]:
                        modifiers += ",".join(self.current_modifiers[behavior][str(idx)])
                    else:
                        modifiers += "None"

                write_event([self.time_, self.behav_, modifiers])

                view_behaviors_layout(obj)

            layout = BoxLayout(orientation="vertical")
            font_size = 24

            self.current_modifiers[behavior] = {}

            if isinstance(self.modifiers[behavior], dict):  # project version >= 4.0.0
                for iidx in sorted([int(x) for x in self.modifiers[behavior].keys()]):
                    idx = str(iidx)

                    self.current_modifiers[behavior][idx] = []

                    if self.modifiers[behavior][idx]["type"] in [0, 1]:  # modifiers type: one, many

                        layout.add_widget(Label(text=self.modifiers[behavior][idx]["name"], size_hint=(0.2, 0.2)))

                        for modif in self.modifiers[behavior][idx]["values"]:
                            btn = Button(
                                text=modif.split(" (")[0],
                                font_size=font_size,
                                on_release=on_button_release,
                                background_normal="",
                                background_color=[0.5, 0.5, 0.5, 1],
                            )
                            self.modifier_buttons[btn] = [
                                behavior,
                                idx,
                                self.modifiers[behavior][idx]["type"],
                                modif.split(" (")[0],
                            ]
                            layout.add_widget(btn)

                    if self.modifiers[behavior][idx]["type"] == 2:  # numeric

                        layout.add_widget(
                            Label(
                                text=self.modifiers[behavior][idx]["name"] + " (validate with <Enter>)",
                                size_hint=(0.2, 0.2),
                            )
                        )
                        ti = TextInput(
                            text="",
                            multiline=False,
                            size_hint_x=1,
                            font_size="25dp",
                            input_type="number",
                            on_text_validate=on_button_release,
                        )
                        self.modifier_buttons[ti] = [behavior, idx, self.modifiers[behavior][idx]["type"], ""]
                        layout.add_widget(ti)

            else:  # project version < 4.0.0
                if len(self.modifiers[behavior].split(",")) > 10:
                    font_size = 14

                for idx, modifier_set in enumerate(self.modifiers[behavior].split("|")):
                    self.current_modifiers[behavior][str(idx)] = []
                    layout.add_widget(Label(text="Modifiers #{}".format(idx), size_hint=(0.2, 0.2)))
                    for modif in modifier_set.split(","):
                        btn = Button(
                            text=modif.split(" (")[0],
                            font_size=font_size,
                            on_release=on_button_release,
                            background_normal="",
                            background_color=[0.5, 0.5, 0.5, 1],
                        )
                        self.modifier_buttons[btn] = [behavior, str(idx), 0, modif.split(" (")[0]]
                        layout.add_widget(btn)

            btn = Button(text="Go back", font_size=font_size)
            btn.background_color = [1, 0, 0, 1]  # red
            btn.bind(on_release=on_goback_button_release)
            self.modifier_buttons[btn] = [behavior, 0, ""]
            layout.add_widget(btn)

            return layout

        def create_subjects_layout():
            """
            create subject layout
            """

            subjectsList = sorted([BorisApp.project[SUBJECTS][k]["name"] for k in BorisApp.project[SUBJECTS].keys()])

            # check number of subjects
            subjects_font_size = 24
            if len(subjectsList) > 20:
                subjects_font_size = 14

            subjectsLayout = GridLayout(cols=int((len(subjectsList) + 1) ** 0.5), size_hint=(1, 1), spacing=5)
            btn = Button(text=NO_FOCAL_SUBJECT, size_hint_x=1, font_size=subjects_font_size)
            btn.bind(on_release=btnSubjectPressed)
            for subject in subjectsList:
                btn = Button(text=subject, size_hint_x=1, font_size=subjects_font_size)
                btn.background_normal = ""
                btn.background_color = [0.5, 0.5, 0.5, 1]  # gray
                btn.bind(on_release=btnSubjectPressed)
                self.btnSubjectsList[subject] = btn
                subjectsLayout.add_widget(btn)

            # cancel button
            btn = Button(text="Cancel", size_hint_x=1, font_size=subjects_font_size)
            btn.background_color = [1, 0, 0, 1]  # red
            btn.bind(on_release=view_behaviors_layout)
            subjectsLayout.add_widget(btn)

            return subjectsLayout

        def create_behaviors_layout():
            """
            grid with buttons for behaviors
            Button background color indicate the behavioral category (if any)

            """

            behaviorsLayout = BoxLayout(orientation="vertical", spacing=3)

            behaviorsLayout.add_widget(Label(text=f"Observation: {self.obsId}", size_hint_y=0.05))

            gdrid_layout = GridLayout(
                cols=int((len(BorisApp.project[ETHOGRAM]) + 1) ** 0.5), size_hint=(1, 1), spacing=3
            )

            behaviorsList = sorted([BorisApp.project[ETHOGRAM][k]["code"] for k in BorisApp.project[ETHOGRAM].keys()])
            # check modifiers
            self.modifiers_layout = {}
            for idx in BorisApp.project[ETHOGRAM]:
                self.modifiers[BorisApp.project[ETHOGRAM][idx]["code"]] = BorisApp.project[ETHOGRAM][idx]["modifiers"]

            print("modifiers", self.modifiers)

            # check number of behaviors
            behaviors_font_size = "24dp"
            if len(behaviorsList) > 20:
                behaviors_font_size = "14dp"

            if "behavioral_categories" in BorisApp.project:
                colors_list = [
                    [1.0, 0.6, 0.0, 1],
                    [0.1, 0.8, 0.1, 1],
                    [0.1, 0.1, 1, 1],
                    [0.94, 0.35, 0.48, 1],
                    [0.2, 0.4, 0.6, 1],
                    [0.4, 0.2, 0.6, 1],
                ]
                categoriesList = set(
                    [
                        BorisApp.project[ETHOGRAM][k]["category"]
                        for k in BorisApp.project[ETHOGRAM].keys()
                        if "category" in BorisApp.project[ETHOGRAM][k]
                    ]
                )

                for idx, category in enumerate(sorted(categoriesList)):
                    behav_list_category = sorted(
                        [
                            BorisApp.project[ETHOGRAM][k]["code"]
                            for k in BorisApp.project[ETHOGRAM].keys()
                            if "category" in BorisApp.project[ETHOGRAM][k]
                            and BorisApp.project[ETHOGRAM][k]["category"] == category
                        ]
                    )
                    for behavior in behav_list_category:
                        btn = Button(text=behavior, size_hint_x=1, font_size=behaviors_font_size)
                        btn.background_normal = ""
                        if category == "":
                            btn.background_color = [0.5, 0.5, 0.5, 1]  # gray
                        else:
                            btn.background_color = colors_list[idx % len(colors_list)]
                        self.behavior_color[behavior] = btn.background_color
                        btn.bind(on_release=btnBehaviorPressed)
                        self.btnList[behavior] = btn
                        gdrid_layout.add_widget(btn)

                        # create modifiers layout
                        if self.modifiers[behavior]:
                            self.modifiers_layout[behavior] = create_modifiers_layout(behavior)

            else:
                for behavior in behaviorsList:
                    btn = Button(text=behavior, size_hint_x=1, font_size=behaviors_font_size)
                    btn.background_normal = ""
                    btn.background_color = [0.5, 0.5, 0.5, 1]  # gray
                    self.behavior_color[behavior] = btn.background_color
                    btn.bind(on_release=btnBehaviorPressed)
                    self.btnList[behavior] = btn
                    gdrid_layout.add_widget(btn)

                    # create modifiers layout
                    if self.modifiers[behavior]:
                        self.modifiers_layout[behavior] = create_modifiers_layout(behavior)

            behaviorsLayout.add_widget(gdrid_layout)

            hlayout = BoxLayout(orientation="horizontal", size_hint_y=0.1)
            # add subject button
            if BorisApp.project[SUBJECTS]:
                self.btnSelSubj = Button(text="Select focal subject", size_hint_x=1, font_size="24dp")
                self.btnSelSubj.background_normal = ""
                self.btnSelSubj.background_color = [0.1, 0.9, 0.1, 1]  # green
                self.btnSelSubj.bind(on_release=view_subjects_layout)
                hlayout.add_widget(self.btnSelSubj)

            # add stop button
            btn = Button(text="Stop obs", size_hint_x=1, font_size="24dp")
            btn.background_normal = ""
            btn.background_color = [0.9, 0.1, 0.1, 1]  # red
            btn.bind(on_release=btnStopPressed)
            hlayout.add_widget(btn)

            behaviorsLayout.add_widget(hlayout)

            return behaviorsLayout

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
                    self.btnList[cs].background_color = [1, 0, 0, 1]  # red

            self.add_widget(self.behaviorsLayout)

        def view_subjects_layout(obj):
            """
            display subjects page
            """
            self.clear_widgets()
            self.add_widget(self.subjectsLayout)
            print("current focal subject:", self.focal_subject)

        def view_modifiers_layout(behavior):
            self.clear_widgets()
            self.add_widget(self.modifiers_layout[behavior])

        def write_event(event):

            t, newState, modifier = event

            if "State" in behaviorType(BorisApp.project[ETHOGRAM], newState):

                # deselect
                if self.focal_subject in self.currentStates and newState in self.currentStates[self.focal_subject]:
                    BorisApp.project[OBSERVATIONS][self.obsId]["events"].append(
                        [round(t - self.t0, 3), self.focal_subject, newState, modifier, ""]
                    )

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
                                    BorisApp.project[OBSERVATIONS][self.obsId]["events"].append(
                                        [round(t - self.t0, 3), self.focal_subject, cs, "", ""]
                                    )
                                    statesToStop.append(cs)
                                    self.btnList[cs].background_color = self.behavior_color[cs]

                            for s in statesToStop:
                                self.currentStates[self.focal_subject].remove(s)

                    BorisApp.project[OBSERVATIONS][self.obsId]["events"].append(
                        [round(t - self.t0, 3), self.focal_subject, newState, modifier, ""]
                    )

                    self.btnList[newState].background_color = [1, 0, 0, 1]  # red

                    if self.focal_subject not in self.currentStates:
                        self.currentStates[self.focal_subject] = []
                    self.currentStates[self.focal_subject].append(newState)

            # point event
            if "Point" in behaviorType(BorisApp.project[ETHOGRAM], newState):
                BorisApp.project[OBSERVATIONS][self.obsId]["events"].append(
                    [round(t - self.t0, 3), self.focal_subject, newState, modifier, ""]
                )

            print("current state", self.currentStates)

            print(BorisApp.project[OBSERVATIONS][self.obsId]["events"][-1])

        def btnBehaviorPressed(obj):
            """
            behavior button pressed
            """

            global selected_modifier
            selected_modifier = {}

            t = time.time()
            newState = obj.text

            self.time_ = t
            self.behav_ = newState

            # check if modifiers
            if self.modifiers[newState]:
                view_modifiers_layout(newState)

            else:
                write_event([self.time_, newState, ""])

        def btnSubjectPressed(obj):
            """
            subject button pressed
            """
            print("self.focal_subject", self.focal_subject)
            print("clicked button", obj.text)

            # deselect already selected subject
            if obj.text == self.focal_subject:
                self.btnSubjectsList[self.focal_subject].background_color = [0.5, 0.5, 0.5, 1]  # gray
                self.focal_subject = NO_FOCAL_SUBJECT
            else:
                if self.focal_subject != NO_FOCAL_SUBJECT:
                    self.btnSubjectsList[self.focal_subject].background_color = [0.5, 0.5, 0.5, 1]  # gray
                self.focal_subject = obj.text
                self.btnSubjectsList[self.focal_subject].background_color = [1, 0, 0, 1]  # red

            print("new focal subject:", self.focal_subject)
            self.btnSelSubj.text = self.focal_subject

            print("current states", self.currentStates)
            # show behaviors
            view_behaviors_layout(None)

        def btnStopPressed(obj):
            def my_callback(instance):
                if instance.title == "y":
                    try:
                        with open(BorisApp.projectFileName, "w") as f:
                            f.write(json.dumps(BorisApp.project, indent=1))

                        popup = Popup(
                            title="Observation saved",
                            content=Label(text="Observation saved in {}".format(BorisApp.projectFileName)),
                            size_hint=(None, None),
                            size=(400, 200),
                        )
                        popup.open()
                    except:
                        print("The observation {} can not be saved!".format(self.obsId))
                        popup = Popup(
                            title="Error",
                            content=Label(text="The observation {} can not be saved!".format(self.obsId)),
                            size_hint=(None, None),
                            size=(400, 200),
                        )
                        popup.open()

                    self.clear_widgets()
                    self.add_widget(StartPageForm())

            pop = ConfirmStopPopup()
            pop.bind(on_dismiss=my_callback)
            pop.open()

        """
        def clock_callback(dt):
            print('clock')
        """

        # check if observation id field is empty
        if not self.obsid_input.text:
            p = Popup(
                title="Error",
                content=Label(text="The observation id is empty"),
                size_hint=(None, None),
                size=(400, 200),
            )
            p.open()
            return

        # check if date is correct
        if not self.obsdate_input.text:
            p = Popup(
                title="Error",
                content=Label(text="The date is empty. Use the YYY-MM-DD HH:MM:SS format"),
                size_hint=(None, None),
                size=(400, 200),
            )
            p.open()
            return

        try:
            time.strptime(self.obsdate_input.text, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            p = Popup(
                title="Error",
                content=Label(text="The date is not valid. Use the YYY-MM-DD HH:MM:SS format"),
                size_hint=(None, None),
                size=(400, 200),
            )
            p.open()
            return

        if self.obsdate_input.text in BorisApp.project[OBSERVATIONS]:
            p = Popup(
                title="Error",
                content=Label(text="This observation id already exists."),
                size_hint=(None, None),
                size=(400, 200),
            )
            p.open()
            return

        # check if observation id already exists
        if self.obsid_input.text in BorisApp.project[OBSERVATIONS]:
            p = Popup(
                title="Error",
                content=Label(text="This observation id already exists."),
                size_hint=(None, None),
                size=(400, 200),
            )
            p.open()
            return

        print("obs id:", self.obsid_input.text)
        print("description:", self.obsdescription_input.text)
        print("observation date:", self.obsdate_input.text)

        self.obsId = self.obsid_input.text
        # format date with T
        """
        if self.obsdate_input.text[10] == " ":
            self.obsdate_input.text[10] = "T"
        """
        BorisApp.project[OBSERVATIONS][self.obsId] = {
            "date": self.obsdate_input.text.replace(" ", "T"),
            "close_behaviors_between_videos": False,
            "time offset": 0.0,
            "scan_sampling_time": 0,
            "time offset second player": 0.0,
            "description": self.obsdescription_input.text,
            "file": [],
            "events": [],
            "visualize_spectrogram": False,
            "type": "LIVE",
            "independent_variables": {},
        }

        # independent variables
        for label in self.iv:
            BorisApp.project[OBSERVATIONS][self.obsId]["independent_variables"][label] = self.iv[label].text
        print("indep var\n", BorisApp.project[OBSERVATIONS][self.obsId]["independent_variables"])

        # create layout with subject buttons
        if BorisApp.project[SUBJECTS]:
            self.subjectsLayout = create_subjects_layout()

        # create layout with behavior buttons
        self.behaviorsLayout = create_behaviors_layout()

        view_behaviors_layout(None)

        self.t0 = time.time()

        # start timer
        """
        Clock.schedule_interval(clock_callback, 60)
        """


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


class ConfirmUpdatePopup(Popup):
    def yes(self):
        self.title = "y"
        self.dismiss()

    def no(self):
        self.title = "n"
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

    """
    class YourApp(App):
        font_size = NumericProperty(20)

    font_size: app.font_size
    """

    project = {}
    projectFileName = ""

    Window.clearcolor = (1, 1, 1, 1)

    if platform == "android":

        from android.storage import primary_external_storage_path  # secondary_external_storage_path

        primary_storage_dir = StringProperty(primary_external_storage_path())

    else:

        primary_storage_dir = StringProperty(".")

    def on_pause(self):
        print("on_pause")
        return True

    def on_resume(self):
        print("on_resume")

    def hook_keyboard(self, window, key, *largs):
        if window == 27:  # esc pressed
            return True

    EventLoop.window.bind(on_keyboard=hook_keyboard)


if __name__ == "__main__":
    Logger.info("Starting BORIS App")
    BorisApp().run()
