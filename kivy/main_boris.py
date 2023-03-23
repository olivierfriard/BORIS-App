"""
BORIS App
Behavioral Observation Research Interactive Software
Copyright 2017-2023 Olivier Friard

This file is part of BORIS App.

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

__app_name__ = "BORIS"
__version__ = "0.7"
__version_date__ = "2023-03-23"

__copyright__ = f"(c) {__version_date__[:4]} Olivier Friard - Marco Gamba - ALPHA"

from kivy.app import App
from kivy.utils import platform
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.uix.textinput import TextInput

from kivy.properties import StringProperty
from kivy.logger import Logger
from kivy.base import EventLoop

from kivy.core.window import Window

import sys
import json
import time
import datetime as dt
import time
import pathlib as pl

from decimal import Decimal

NO_FOCAL_SUBJECT = "No focal subject"
OBSERVATIONS = "observations"
SUBJECTS = "subjects_conf"
ETHOGRAM = "behaviors_conf"
INDEP_VAR = "independent_variables"
VERSION_URL = "https://raw.githubusercontent.com/olivierfriard/BORIS-App/master/ver.txt"

# modifiers
SINGLE_SELECTION = 0
MULTI_SELECTION = 1
NUMERIC_MODIFIER = 2

YES = "yes"
NO = "no"

RED = [1, 0, 0, 1]
GRAY = [0.5, 0.5, 0.5, 1]

BEHAV_CAT = "behavioral_categories"
BEHAV_CAT_COLORS = [
    [1.0, 0.6, 0.0, 1],
    [0.1, 0.8, 0.1, 1],
    [0.1, 0.1, 1, 1],
    [0.94, 0.35, 0.48, 1],
    [0.2, 0.4, 0.6, 1],
    [0.4, 0.2, 0.6, 1],
]

FONT_MAX_SIZE_SUBJECT = 40
FONT_MIN_SIZE_SUBJECT = 20

selected_modifiers = {}
observation_to_send = ""


if platform == "android":
    from android.storage import primary_external_storage_path  # secondary_external_storage_path

    primary_storage_dir = primary_external_storage_path()
else:
    primary_storage_dir = "."


def dynamic_font_size(n: int) -> int:
    """
    return font size adapted to the number of item
    """

    if n >= 20:
        return f"{FONT_MIN_SIZE_SUBJECT}dp"
    else:
        return f"{int((FONT_MIN_SIZE_SUBJECT - FONT_MAX_SIZE_SUBJECT) / 20 * n + FONT_MAX_SIZE_SUBJECT)}dp"


class StartPageForm(BoxLayout):
    def show_SelectProjectForm(self):

        self.clear_widgets()
        self.add_widget(SelectProjectForm())

    def more(self):
        self.clear_widgets()
        self.add_widget(MoreForm())

    def ver(self):
        return f"v.{__version__ } {__copyright__}"


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


class ViewProjectForm(BoxLayout):

    selected_item = StringProperty("no selection")

    def show(self):
        self.ids.lbl.text = f"project file: {pl.Path(BorisApp.projectFileName).name}"
        rows = []
        rows.append(f"project name: {BorisApp.project['project_name']}")
        rows.append(f"project date: {BorisApp.project['project_date'].replace('T', ' ')}")
        rows.append(f"project description: {BorisApp.project['project_description']}")
        rows.append(f"Number of behaviors: {len(BorisApp.project[ETHOGRAM])}")
        rows.append(f"Number of behavioral categories: {len(BorisApp.project.get(BEHAV_CAT, []))}")
        rows.append(f"Number of subjects: {len(BorisApp.project[SUBJECTS])}")
        rows.append(f"Number of observations: {len(BorisApp.project[OBSERVATIONS])}")

        self.ids.project_info.text = "\n".join(rows)

    def selection_changed(self, *args):
        self.selected_item = args[0].selection[0].text

    def view_ethogram(self):
        """
        display ethogram
        """
        self.clear_widgets()
        w = ViewEthogramForm()
        self.add_widget(w)
        w.show()

    def new_observation(self):
        """
        start a new observation
        """
        self.clear_widgets()
        a = StartObservationForm()
        a.obsdate_input.text = f"{dt.datetime.now():%Y-%m-%d %H:%M:%S}"
        self.add_widget(a)

    def go_back(self):
        """
        go to the start page
        """
        self.clear_widgets()
        self.add_widget(StartPageForm())


class ViewEthogramForm(BoxLayout):
    """
    display ethogram details
    """

    def show(self):
        self.ids.lbl.text = f"The ethogram contains {len(BorisApp.project[ETHOGRAM])} behavior{'s.' if len(BorisApp.project[ETHOGRAM]) > 1 else '.'}"
        rows = []
        for idx in BorisApp.project[ETHOGRAM]:
            rows.append(BorisApp.project[ETHOGRAM][idx]["code"])
            rows.append(f"Type of behavior: {BorisApp.project[ETHOGRAM][idx]['type']}")
            rows.append(f"Description: {BorisApp.project[ETHOGRAM][idx]['description']}")
            rows.append(
                f"Behavioral category: {BorisApp.project[ETHOGRAM][idx]['category'] if BorisApp.project[ETHOGRAM][idx]['category'] else 'None'}"
            )
            rows.append(f"Modifiers: {'Yes' if BorisApp.project[ETHOGRAM][idx]['modifiers'] else 'No'}")
            rows.append("")

        self.ids.project_info.text = "\n".join(rows)

    def view_project(self):
        self.clear_widgets()
        w = ViewProjectForm()
        self.add_widget(w)
        w.show()

    def new_observation(self):
        """
        start a new observation
        """
        self.clear_widgets()
        a = StartObservationForm()
        a.obsdate_input.text = f"{dt.datetime.now():%Y-%m-%d %H:%M:%S}"
        self.add_widget(a)

    def go_back(self):
        """
        go to the start page
        """
        self.clear_widgets()
        self.add_widget(StartPageForm())


class SelectProjectForm(BoxLayout):
    def cancel(self):
        self.clear_widgets()
        self.add_widget(StartPageForm())

    def open_project(self, path, selection):
        """
        open project from selected file
        """

        if not selection:
            pop = InfoPopup()
            pop.ids.label.text = f"No project file selected!"
            pop.open()
            return

        try:
            BorisApp.projectFileName = selection[0]
            BorisApp.project = json.loads(open(BorisApp.projectFileName, "r").read())
        except Exception:
            pop = InfoPopup()
            pop.ids.label.text = "The selected file is not a BORIS behaviors file!"
            pop.open()
            return

        if not BorisApp.project[ETHOGRAM]:
            pop = InfoPopup()
            pop.ids.label.text = "The ethogram of this project is empty!"
            pop.open()
            return

        self.clear_widgets()
        w = ViewProjectForm()
        self.add_widget(w)
        w.show()


def behaviorType(ethogram: dict, behavior: str) -> str:
    """
    returns the type of behavior: POINT or STATE
    """
    return [ethogram[k]["type"] for k in ethogram.keys() if ethogram[k]["code"] == behavior][0]


def behaviorExcluded(ethogram, behavior):
    return [ethogram[k]["excluded"] for k in ethogram.keys() if ethogram[k]["code"] == behavior][0].split(",")


class StartObservationForm(BoxLayout):

    time0 = 0  # initial time
    focal_subject = NO_FOCAL_SUBJECT
    btnList, btnSubjectsList, mem, behavior_color, currentStates, modifiers = {}, {}, {}, {}, {}, {}
    fileName, obsId, behaviorsLayout, subjectsLayout = "", "", "", ""

    time_ = 0
    behav_ = ""
    iv = {}

    def cancel(self):
        """
        returns to home page
        """
        self.clear_widgets()
        self.add_widget(StartPageForm())

    def show_start_observation_form(self):
        self.clear_widgets()
        w = StartObservationForm()
        w.obsid_input.text = self.mem["obsId"]
        w.obsdate_input.text = self.mem["obsDate"]
        w.obsdescription_input.text = self.mem["obsDescription"]
        w.day_time_input.active = self.mem["day_time"]
        w.epoch_time_input.active = self.mem["epoch_time"]

        self.add_widget(w)

    def go_back(self, obj):
        """
        return to 'start observation' screen
        """

        # check if numeric indep var values are numeric
        if INDEP_VAR in BorisApp.project:
            for idx in BorisApp.project[INDEP_VAR]:
                if BorisApp.project[INDEP_VAR][idx]["label"] in self.iv:
                    if (
                        BorisApp.project[INDEP_VAR][idx]["type"] == "numeric"
                        and self.iv[BorisApp.project[INDEP_VAR][idx]["label"]].text
                    ):
                        try:
                            _ = float(self.iv[BorisApp.project[INDEP_VAR][idx]["label"]].text)
                        except:
                            Popup(
                                title="Error",
                                content=Label(
                                    text=f"The variable '{BorisApp.project[INDEP_VAR][idx]['label']}' must be numeric",
                                    size_hint=(None, None),
                                    size=(400, 200),
                                ),
                            ).open()
                            return

        self.show_start_observation_form()

    def set_date_to_now(self):
        """
        set date to now
        """
        self.obsdate_input.text = f"{dt.datetime.now():%Y-%m-%d %H:%M:%S}"

    def indep_var(self):
        """
        input independent variables
        """

        self.mem = {
            "obsId": self.obsid_input.text,
            "obsDate": self.obsdate_input.text,
            "obsDescription": self.obsdescription_input.text,
        }
        if INDEP_VAR not in BorisApp.project or not BorisApp.project[INDEP_VAR]:
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

        if INDEP_VAR in BorisApp.project:
            for idx in BorisApp.project[INDEP_VAR]:
                layout1 = BoxLayout(orientation="horizontal")
                s = BorisApp.project[INDEP_VAR][idx]["label"]
                if BorisApp.project[INDEP_VAR][idx]["description"]:
                    s += "\n({})".format(BorisApp.project[INDEP_VAR][idx]["description"])
                lb1 = Label(text=s, size_hint_x=1, font_size=20)
                layout1.add_widget(lb1)

                ti = TextInput(
                    text=BorisApp.project[INDEP_VAR][idx]["default value"],
                    multiline=False,
                    size_hint_x=1,
                    font_size="25dp",
                )
                self.iv[BorisApp.project[INDEP_VAR][idx]["label"]] = ti
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

            def on_goback_button_release(obj):

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

            for iidx in sorted([int(x) for x in self.modifiers[behavior].keys()]):
                idx = str(iidx)

                self.current_modifiers[behavior][idx] = []

                if self.modifiers[behavior][idx]["type"] in (SINGLE_SELECTION, MULTI_SELECTION):

                    layout.add_widget(Label(text=self.modifiers[behavior][idx]["name"], size_hint=(0.2, 0.2)))

                    modifiers_number = len(self.modifiers[behavior][idx]["values"])
                    font_size = dynamic_font_size(modifiers_number)

                    for modif in self.modifiers[behavior][idx]["values"]:
                        btn = Button(
                            text=modif.split(" (")[0],
                            font_size=font_size,
                            on_release=on_button_release,
                            background_normal="",
                            background_color=GRAY,
                            size_hint_y=1,
                        )
                        self.modifier_buttons[btn] = [
                            behavior,
                            idx,
                            self.modifiers[behavior][idx]["type"],
                            modif.split(" (")[0],
                        ]
                        layout.add_widget(btn)

                if self.modifiers[behavior][idx]["type"] == NUMERIC_MODIFIER:

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

            btn = Button(text="Go back", font_size=font_size, size_hint_y=0.2)
            btn.background_color = RED
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

            if len(subjectsList) >= 20:
                subjects_font_size = FONT_MIN_SIZE_SUBJECT
            else:
                subjects_font_size = (FONT_MIN_SIZE_SUBJECT - FONT_MAX_SIZE_SUBJECT) / 20 * len(
                    subjectsList
                ) + FONT_MAX_SIZE_SUBJECT

            subjectsLayout = GridLayout(cols=int((len(subjectsList) + 1) ** 0.5), size_hint=(1, 1), spacing=5)

            for subject in subjectsList:
                btn = Button(text=subject, size_hint_x=1, font_size=subjects_font_size)
                btn.background_normal = ""
                btn.background_color = GRAY
                btn.bind(on_release=btnSubjectPressed)
                self.btnSubjectsList[subject] = btn
                subjectsLayout.add_widget(btn)

            # cancel button
            btn = Button(text="Cancel", size_hint_x=1, size_hint_y=0.2, font_size=subjects_font_size - 2)
            btn.background_color = RED
            btn.bind(on_release=view_behaviors_layout)
            subjectsLayout.add_widget(btn)

            return subjectsLayout

        def create_behaviors_layout():
            """
            grid with buttons for behaviors
            Button background color indicate the behavioral category (if any)
            """

            behaviorsLayout = BoxLayout(orientation="vertical", spacing=3)

            # header with obs id
            obsid_time = BoxLayout(orientation="horizontal", size_hint_y=0.1)

            self.obsid_header = Label(text=f"Observation: {self.obsId}")
            self.time_header = Label(text=f"{dt.datetime.now():%Y-%m-%d %H:%M:%S}")
            obsid_time.add_widget(self.obsid_header)
            obsid_time.add_widget(self.time_header)

            behaviorsLayout.add_widget(obsid_time)

            gdrid_layout = GridLayout(
                cols=int((len(BorisApp.project[ETHOGRAM]) + 1) ** 0.5), size_hint=(1, 1), spacing=3
            )

            behaviors_list = sorted([BorisApp.project[ETHOGRAM][k]["code"] for k in BorisApp.project[ETHOGRAM]])
            # check modifiers
            self.modifiers_layout = {}
            for idx in BorisApp.project[ETHOGRAM]:
                self.modifiers[BorisApp.project[ETHOGRAM][idx]["code"]] = BorisApp.project[ETHOGRAM][idx]["modifiers"]

            # font size
            behaviors_font_size = dynamic_font_size(len(behaviors_list))

            if BEHAV_CAT in BorisApp.project:
                colors_list = BEHAV_CAT_COLORS
                categories_list = set(
                    [
                        BorisApp.project[ETHOGRAM][k]["category"]
                        for k in BorisApp.project[ETHOGRAM].keys()
                        if "category" in BorisApp.project[ETHOGRAM][k]
                    ]
                )

                for idx, category in enumerate(sorted(categories_list)):
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
                for behavior in behaviors_list:
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
            """
            record event in observation
            change button color if STATE event
            """

            def seconds_of_day(time_) -> float:
                """
                return the number of seconds since start of the day
                """

                print(time_.date())
                print(dt.time(0))

                return round((time_ - dt.datetime.combine(time_.date(), dt.time(0))).total_seconds(), 3)

                # return dec((dt - datetime.datetime.combine(dt.date(), datetime.time(0))).total_seconds()).quantize(dec("0.001"))

            time_, newState, modifier = event

            if "State" in behaviorType(BorisApp.project[ETHOGRAM], newState):

                # deselect
                if self.focal_subject in self.currentStates and newState in self.currentStates[self.focal_subject]:
                    BorisApp.project[OBSERVATIONS][self.obsId]["events"].append(
                        [round(time_ - self.time0, 3), self.focal_subject, newState, modifier, ""]
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
                                        [round(time_ - self.time0, 3), self.focal_subject, cs, "", ""]
                                    )
                                    statesToStop.append(cs)
                                    self.btnList[cs].background_color = self.behavior_color[cs]

                            for s in statesToStop:
                                self.currentStates[self.focal_subject].remove(s)

                    BorisApp.project[OBSERVATIONS][self.obsId]["events"].append(
                        [round(time_ - self.time0, 3), self.focal_subject, newState, modifier, ""]
                    )

                    self.btnList[newState].background_color = [1, 0, 0, 1]  # red

                    if self.focal_subject not in self.currentStates:
                        self.currentStates[self.focal_subject] = []
                    self.currentStates[self.focal_subject].append(newState)

            # point event
            if "Point" in behaviorType(BorisApp.project[ETHOGRAM], newState):
                # add event
                if BorisApp.project[OBSERVATIONS][self.obsId]["start_from_current_time"]:
                    time_output = seconds_of_day(dt.datetime.now())
                    print(f"{time_output}")
                elif BorisApp.project[OBSERVATIONS][self.obsId]["start_from_current_epoch_time"]:
                    time_output = round(time_, 3)
                else:
                    time_output = round(time_ - self.time0, 3)

                print([time_output, self.focal_subject, newState, modifier, ""])

                BorisApp.project[OBSERVATIONS][self.obsId]["events"].append(
                    [time_output, self.focal_subject, newState, modifier, ""]
                )

            Logger.info(f"{__app_name__}: current state {self.currentStates}")
            Logger.info(f"{__app_name__}: event {BorisApp.project[OBSERVATIONS][self.obsId]['events'][-1]}")

        def btnBehaviorPressed(obj):
            """
            behavior button pressed
            """

            global selected_modifier
            selected_modifier = {}

            self.time_ = time.time()  # epoch time
            self.behav_ = obj.text

            # check if modifiers
            if self.modifiers[self.behav_]:
                view_modifiers_layout(self.behav_)
            else:
                write_event((self.time_, self.behav_, ""))

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
            """
            stop current observation
            """

            def stop_obs_callback(instance):
                if instance.title == YES:
                    try:
                        with open(BorisApp.projectFileName, "w") as f:
                            f.write(json.dumps(BorisApp.project, indent=1))

                        pop = InfoPopup()
                        pop.ids.label.text = f"Observation saved in\n{BorisApp.projectFileName}"
                        pop.open()

                    except Exception:
                        print(f"The observation {self.obsId} can not be saved!")

                        pop = InfoPopup()
                        pop.ids.label.text = f"The observation {self.obsId} can not be saved!"
                        pop.open()

                    self.clock_timer.cancel()
                    self.clear_widgets()
                    self.add_widget(StartPageForm())

            pop = ConfirmStopPopup()
            pop.bind(on_dismiss=stop_obs_callback)
            pop.open()

        def clock(delta_time):
            self.time_header.text = f"{dt.datetime.now():%Y-%m-%d %H:%M:%S} | {time.time() - self.time0:.3f} s"

        def obs_exists(nb_events):
            def obs_exists_callback(instance):
                if instance.title == "cancel":
                    self.show_start_observation_form()

            pop = AskExistingObservation()
            if nb_events:
                pop.ids.lb_obs_exists.text = (
                    f"An observation with the same id and {nb_events} coded events already exists"
                )
            else:
                pop.ids.lb_obs_exists.text = f"An observation with the same id already exists. No events were coded"

            pop.bind(on_dismiss=obs_exists_callback)
            pop.open()
            print("end popup")
            # print(pop.result)

        # check if observation id field is empty
        if not self.obsid_input.text:
            pop = InfoPopup()
            pop.ids.label.text = "The observation id is empty"
            pop.open()
            return

        if self.obsid_input.text.upper() in (x.upper() for x in BorisApp.project[OBSERVATIONS]):
            self.mem["obsId"] = self.obsid_input.text
            self.mem["obsDate"] = self.obsdate_input.text
            self.mem["obsDescription"] = self.obsdescription_input.text
            self.mem["day_time"] = self.day_time_input.active
            self.mem["epoch_time"] = self.epoch_time_input.active
            # number of events in existing obs
            nb_events = [
                len(BorisApp.project[OBSERVATIONS][x]["events"])
                for x in BorisApp.project[OBSERVATIONS]
                if x.upper() == self.obsid_input.text.upper()
            ][0]
            obs_exists(nb_events)
            # pop.ids.label.text = f"This observation id ({self.obsid_input.text}) already exists."
            # pop.open()
            # return

        # check if date is correct
        if not self.obsdate_input.text:
            pop = InfoPopup()
            pop.ids.label.text = "The date is empty. Use the YYYY-MM-DD HH:MM:SS format"
            pop.open()
            return

        try:
            time.strptime(self.obsdate_input.text, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            pop = InfoPopup()
            pop.ids.label.text = "The date is not valid. Use the YYYY-MM-DD HH:MM:SS format"
            pop.open()
            return

        Logger.info(f"{__app_name__}: observation id {self.obsid_input.text}")
        Logger.info(f"{__app_name__}: description {self.obsdescription_input.text}")
        Logger.info(f"{__app_name__}: observation date {self.obsdate_input.text}")

        self.obsId = self.obsid_input.text

        BorisApp.project[OBSERVATIONS][self.obsId] = {
            "date": self.obsdate_input.text.replace(" ", "T"),
            "close_behaviors_between_videos": False,
            "time offset": 0.0,
            "scan_sampling_time": 0,
            "description": self.obsdescription_input.text,
            "file": [],
            "events": [],
            "visualize_spectrogram": False,
            "visualize_waveform": False,
            "start_from_current_time": self.day_time_input.active,
            "start_from_current_epoch_time": self.epoch_time_input.active,
            "type": "LIVE",
            INDEP_VAR: {},
        }

        # independent variables
        for label in self.iv:
            BorisApp.project[OBSERVATIONS][self.obsId][INDEP_VAR][label] = self.iv[label].text

        Logger.info(f"{__app_name__}: indep var {BorisApp.project[OBSERVATIONS][self.obsId][INDEP_VAR]}")

        # create layout with subject buttons
        if BorisApp.project[SUBJECTS]:
            self.subjectsLayout = create_subjects_layout()

        # create layout with behavior buttons
        self.behaviorsLayout = create_behaviors_layout()

        view_behaviors_layout(None)

        self.time0 = time.time()

        # start timer
        self.clock_timer = Clock.schedule_interval(clock, 1)


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
        self.title = YES
        self.dismiss()

    def no(self):
        self.title = NO
        self.dismiss()


class AskExistingObservation(Popup):
    def cancel(self):
        self.title = "cancel"
        self.dismiss()

    def overwrite(self):
        self.title = "overwrite"
        self.dismiss()


class InfoPopup(Popup):
    def close(self):
        self.dismiss()


class BorisRoot(BoxLayout):
    pass


class BorisApp(App):

    """
    class YourApp(App):
        font_size = NumericProperty(20)

    font_size: app.font_size
    """

    def request_android_permissions(self):
        from android.permissions import request_permissions, Permission

        def callback(permissions, results):
            """
            Defines the callback to be fired when runtime permission
            has been granted or denied. This is not strictly required,
            but added for the sake of completeness.
            """
            if all([res for res in results]):
                Logger.info(f"{__app_name__}: All permissions granted.")
            else:
                Logger.info(f"{__app_name__}: Some permissions refused.")

        request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE], callback)
        # MANAGE_EXTERNAL_STORAGE ?

    project = {}
    projectFileName = ""

    app_primary_storage_dir = StringProperty(primary_storage_dir)

    Window.clearcolor = (1, 1, 1, 1)

    def build(self):
        if platform == "android":
            Logger.info(f"{__app_name__}: Android detected. Requesting permissions")
            self.request_android_permissions()

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
    Logger.info(f"{__app_name__}: Starting BORIS App")
    BorisApp().run()
