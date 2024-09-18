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
__version__ = "0.13"
__version_date__ = "2024-09-18"

__copyright__ = f"(c) {__version_date__[:4]} Olivier Friard - Marco Gamba"

from kivy.app import App
from kivy.utils import platform
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown

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


NO_FOCAL_SUBJECT = "No focal subject"
OBSERVATIONS = "observations"
SUBJECTS = "subjects_conf"
ETHOGRAM = "behaviors_conf"
INDEP_VAR = "independent_variables"

EVENT_TIME_IDX = 0
EVENT_SUBJECT_IDX = 1
EVENT_BEHAVIOR_IDX = 2
EVENT_MODIFIER_IDX = 3
# EVENT_COMMENT_IDX = 4

# modifiers
SINGLE_SELECTION = 0
MULTI_SELECTION = 1
NUMERIC_MODIFIER = 2

YES = "yes"
NO = "no"

RED = [1, 0, 0, 1]
DARKRED = [0.9, 0.1, 0.1, 1]
GRAY = [0.5, 0.5, 0.5, 1]
GREEN = [0.1, 0.9, 0.1, 1]
BLUE = [0.1, 0.1, 0.9, 1]
BLACK = [0, 0, 0, 1]
WHITE = [1, 1, 1, 1]


BEHAV_CAT = "behavioral_categories"

"""
BEHAV_CAT_COLORS = [
    [1.0, 0.6, 0.0, 1],
    [0.1, 0.8, 0.1, 1],
    [0.1, 0.1, 1, 1],
    [0.94, 0.35, 0.48, 1],
    [0.2, 0.4, 0.6, 1],
    [0.4, 0.2, 0.6, 1],
]
"""

FONT_MAX_SIZE_SUBJECT = 40
FONT_MIN_SIZE_SUBJECT = 20

selected_modifiers: dict = {}


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


def contrasted_color(c):
    def luminance(s: str) -> float:
        def conv(c):
            if c <= 0.03928:
                return c / 12.92
            else:
                return ((c + 0.055) / 1.055) ** 2.4

        s = s.replace("#", "")
        r = int(s[:2], 16) / 255
        g = int(s[2:4], 16) / 255
        b = int(s[4:], 16) / 255

        return 0.2126 * conv(r) + 0.7152 * conv(g) + 0.0722 * conv(b)

    def contrast(c1, c2):
        r = (luminance(c1) + 0.05) / (luminance(c2) + 0.05)
        if r < 1:
            return 1 / r
        else:
            return r

    black = "#000000"
    white = "#ffffff"

    if not isinstance(c, str):
        c = "#%02x%02x%02x" % tuple((int(x * 255) for x in c[:3]))

    if contrast(c, black) > 4.5:
        return black
    else:
        return white


def seconds_of_day(time_) -> float:
    """
    return the number of seconds since start of the day
    """

    print(time_.date())
    print(dt.time(0))

    return round((time_ - dt.datetime.combine(time_.date(), dt.time(0))).total_seconds(), 3)

    # return dec((dt - datetime.datetime.combine(dt.date(), datetime.time(0))).total_seconds()).quantize(dec("0.001"))


def get_current_states_modifiers_for_subject(
    state_behaviors_codes: list, events: list, subject: str, time_: float, include_modifiers: bool = False
) -> dict:
    """
    get current states and modifiers (if requested) for a subject at given time

    Args:
        state_behaviors_codes (list): list of behavior codes defined as STATE event
        events (list): list of events
        subject (str): subject name
        time (float): time
        include_modifiers (bool): include modifier if True (default: False)

    Returns:
        dict: current states by subject. dict of list
    """
    current_states: list = []

    for event in events:
        if event[EVENT_TIME_IDX] > time_:
            break
        if event[EVENT_BEHAVIOR_IDX] not in state_behaviors_codes:
            continue
        if event[EVENT_SUBJECT_IDX] != subject:
            continue

        if (event[EVENT_BEHAVIOR_IDX], event[EVENT_MODIFIER_IDX]) not in current_states:
            current_states.append((event[EVENT_BEHAVIOR_IDX], event[EVENT_MODIFIER_IDX]))
        else:
            current_states.remove((event[EVENT_BEHAVIOR_IDX], event[EVENT_MODIFIER_IDX]))

    return current_states


'''
def get_current_states_modifiers_by_subject(
    state_behaviors_codes: list, events: list, subjects: dict, time_: float, include_modifiers: bool = False
) -> dict:
    """
    get current states and modifiers (if requested) for subjects at given time

    Args:
        state_behaviors_codes (list): list of behavior codes defined as STATE event
        events (list): list of events
        subjects (dict): dictionary of subjects
        time (float): time or image index for an observation from images
        include_modifiers (bool): include modifier if True (default: False)

    Returns:
        dict: current states by subject. dict of list
    """
    current_states: dict = {}

    for idx in subjects:
        current_states[subjects[idx]["name"]] = {}
    for x in events:
        if x[EVENT_TIME_IDX] > time_:
            break
        if x[EVENT_BEHAVIOR_IDX] in state_behaviors_codes:
            if (x[EVENT_BEHAVIOR_IDX], x[EVENT_MODIFIER_IDX]) not in current_states[x[EVENT_SUBJECT_IDX]]:
                current_states[x[EVENT_SUBJECT_IDX]][(x[EVENT_BEHAVIOR_IDX], x[EVENT_MODIFIER_IDX])] = False

            current_states[x[EVENT_SUBJECT_IDX]][(x[EVENT_BEHAVIOR_IDX], x[EVENT_MODIFIER_IDX])] = not current_states[x[EVENT_SUBJECT_IDX]][
                (x[EVENT_BEHAVIOR_IDX], x[EVENT_MODIFIER_IDX])
            ]

    r: dict = {}
    for idx in subjects:
        r[idx] = [f"{bm[0]} ({bm[1]})" for bm in current_states[subjects[idx]["name"]] if current_states[subjects[idx]["name"]][bm]]

    return r
'''


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
        self.ids.lbl.text = (
            f"The ethogram contains {len(BorisApp.project[ETHOGRAM])} behavior{'s.' if len(BorisApp.project[ETHOGRAM]) > 1 else '.'}"
        )
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


def behaviorExcluded(ethogram, behavior) -> list:
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
        """
        show start observation page
        """
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
        return to 'start observation' screen from independent variables page
        """

        # check if numeric indep var values are numeric
        for idx in BorisApp.project.get(INDEP_VAR, {}):
            if BorisApp.project[INDEP_VAR][idx]["label"] in self.iv:
                if BorisApp.project[INDEP_VAR][idx]["type"] == "numeric" and self.iv[BorisApp.project[INDEP_VAR][idx]["label"]].text:
                    try:
                        _ = float(self.iv[BorisApp.project[INDEP_VAR][idx]["label"]].text)
                    except:
                        pop = InfoPopup()
                        pop.ids.label.text = f"The variable '{BorisApp.project[INDEP_VAR][idx]['label']}' must be numeric."
                        pop.open()
                        return

        for label in self.iv:
            self.mem["indep_var|" + label] = self.iv[label].text

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

        self.mem["obsId"] = self.obsid_input.text
        self.mem["obsDate"] = self.obsdate_input.text
        self.mem["obsDescription"] = self.obsdescription_input.text
        self.mem["day_time"] = self.day_time_input.active
        self.mem["epoch_time"] = self.epoch_time_input.active

        if not BorisApp.project.get(INDEP_VAR, {}):
            pop = InfoPopup()
            pop.ids.label.text = "The current project does not define independent variables"
            pop.open()
            self.show_start_observation_form()
            return

        main_layout = BoxLayout(orientation="vertical")
        title_layout = BoxLayout(orientation="horizontal", size_hint_y=0.1)
        title_layout.add_widget(Label(text="Independent variables", font_size="25dp"))
        main_layout.add_widget(title_layout)

        parameters_layout = BoxLayout(orientation="vertical", size_hint_y=0.8)

        for idx in BorisApp.project.get(INDEP_VAR, {}):
            layout = BoxLayout(orientation="horizontal")
            s = BorisApp.project[INDEP_VAR][idx]["label"]
            if BorisApp.project[INDEP_VAR][idx]["description"]:
                s += "\n({})".format(BorisApp.project[INDEP_VAR][idx]["description"])
            lb1 = Label(text=s, size_hint_x=1, font_size="18dp")  # , halign="left", valign="middle")
            # lb1.bind(size=lb1.setter("text_size"))
            layout.add_widget(lb1)

            # numeric, text, timestamp
            if BorisApp.project[INDEP_VAR][idx]["type"] in ("numeric", "text", "timestamp"):
                if "indep_var|" + BorisApp.project[INDEP_VAR][idx]["label"] in self.mem:
                    value = self.mem["indep_var|" + BorisApp.project[INDEP_VAR][idx]["label"]]
                else:
                    value = BorisApp.project[INDEP_VAR][idx]["default value"]

                ti = TextInput(
                    text=value,
                    multiline=False,
                    size_hint_x=1,
                    font_size="22dp",
                )
                self.iv[BorisApp.project[INDEP_VAR][idx]["label"]] = ti
                layout.add_widget(ti)

            # set of values
            if BorisApp.project[INDEP_VAR][idx]["type"] == "value from set":
                if "indep_var|" + BorisApp.project[INDEP_VAR][idx]["label"] in self.mem:
                    value = self.mem["indep_var|" + BorisApp.project[INDEP_VAR][idx]["label"]]
                else:
                    value = BorisApp.project[INDEP_VAR][idx]["default value"]

                dropdown = DropDown()
                for choice in BorisApp.project[INDEP_VAR][idx]["possible values"].split(","):
                    btn = Button(text=choice, size_hint_y=None, size_hint_x=1, font_size="18dp")
                    btn.bind(on_release=lambda btn: dropdown.select(btn.text))
                    dropdown.add_widget(btn)

                mainbutton = Button(text=value, size_hint_x=1, font_size="22dp", background_normal="")

                mainbutton.background_color = WHITE
                mainbutton.color = BLACK
                layout.add_widget(mainbutton)
                self.iv[BorisApp.project[INDEP_VAR][idx]["label"]] = mainbutton

                mainbutton.bind(on_release=dropdown.open)
                dropdown.bind(on_select=lambda instance, x: setattr(mainbutton, "text", x))

                # layout.add_widget(dropdown)

            parameters_layout.add_widget(layout)

        main_layout.add_widget(parameters_layout)

        menu_layout = BoxLayout(orientation="vertical", size_hint_y=0.1)
        # Go back button
        btn = Button(text="Go back", size_hint_x=1, font_size="25dp")
        btn.bind(on_release=self.go_back)
        # btn.background_color =  GRAY
        menu_layout.add_widget(btn)

        main_layout.add_widget(menu_layout)

        self.clear_widgets()
        self.add_widget(main_layout)

    def start(self):
        """
        start new observation
        """
        self.modifier_buttons: dict = {}

        def create_modifiers_layout(behavior):
            """
            create modifiers layout for each behavior
            """

            def on_button_release(obj):
                """
                manage selected modifier
                """

                behavior, idx, type_, modifier = self.modifier_buttons[obj]

                print(f"{modifier=} {idx=}")

                if type_ == SINGLE_SELECTION:
                    # switch color
                    if obj.background_color == GRAY:
                        obj.background_color = DARKRED
                    else:
                        obj.background_color = GRAY

                    # all other buttons to gray
                    for btn in self.modifier_buttons:
                        if btn == obj:
                            continue
                        if self.modifier_buttons[btn][0] == behavior and self.modifier_buttons[btn][1] == idx:
                            btn.background_color = GRAY

                if type_ == MULTI_SELECTION:
                    # switch color
                    if obj.background_color == GRAY:
                        obj.background_color = DARKRED
                    else:
                        obj.background_color = GRAY

            def on_goback_button_release(obj):
                """
                get selected modifier(s)
                write event and go back to observation
                """

                modifiers: dict = {}
                for idx in sorted([int(x) for x in self.modifiers[behavior]]):
                    idx = str(idx)
                    modifiers[idx] = []
                    if self.modifiers[behavior][idx]["type"] == NUMERIC_MODIFIER:
                        for btn in self.modifier_buttons:
                            # button correspond to selected behavior
                            if self.modifier_buttons[btn][1] == idx and self.modifier_buttons[btn][0] == self.behav_:
                                if btn.text:
                                    modifiers[idx].append(btn.text)
                                else:
                                    modifiers[idx].append("None")
                    else:
                        for btn in self.modifier_buttons:
                            # button correspond to selected behavior
                            if (
                                self.modifier_buttons[btn][1] == idx
                                and self.modifier_buttons[btn][0] == self.behav_
                                and btn.background_color == DARKRED
                            ):
                                modifiers[idx].append(self.modifier_buttons[btn][3])
                        if not modifiers[idx]:
                            modifiers[idx].append("None")

                print(f"{modifiers=}")

                write_event([self.time_, self.behav_, "|".join([x for x in [",".join(modifiers[idx]) for idx in modifiers]])])

                view_behaviors_layout(obj)

            # check the modifier type single or multiple
            text = "Modifier"
            for idx in self.modifiers[behavior]:
                if self.modifiers[behavior][idx]["type"] == SINGLE_SELECTION:
                    text = "Select the modifier"
                if self.modifiers[behavior][idx]["type"] == MULTI_SELECTION:
                    text = "Select the modifier(s)"
                if self.modifiers[behavior][idx]["type"] == NUMERIC_MODIFIER:
                    text = "Input the numeric modifier"

            scrollwidget_layout = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))

            main_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
            main_layout.bind(minimum_height=main_layout.setter("height"))

            title_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=40)
            # Go back button
            btn = Button(
                text="Go back",
                font_size="20dp",
                size_hint_x=0.2,
            )
            btn.bind(on_release=on_goback_button_release)
            self.modifier_buttons[btn] = [behavior, -1, "", ""]

            title_layout.add_widget(btn)
            title_layout.add_widget(
                Label(
                    text=text,
                    font_size="20dp",
                    height=40,
                )
            )
            main_layout.add_widget(title_layout)

            font_size = "20dp"

            for iidx in sorted([int(x) for x in self.modifiers[behavior]]):
                idx = str(iidx)

                print(f"{behavior=} {idx=}")

                # add modifier set name
                main_layout.add_widget(
                    Label(
                        text=self.modifiers[behavior][idx]["name"],
                        font_size=font_size,
                        size_hint_y=None,
                        height=40,
                    )
                )

                if self.modifiers[behavior][idx]["type"] in (SINGLE_SELECTION, MULTI_SELECTION):
                    for modif in self.modifiers[behavior][idx]["values"]:
                        btn = Button(
                            text=modif.split(" (")[0],
                            font_size=font_size,
                            on_release=on_button_release,
                            background_normal="",
                            background_color=GRAY,
                            size_hint_y=None,
                            # height=40,
                        )
                        self.modifier_buttons[btn] = [
                            behavior,
                            idx,
                            self.modifiers[behavior][idx]["type"],
                            modif.split(" (")[0],
                        ]
                        main_layout.add_widget(btn)

                if self.modifiers[behavior][idx]["type"] == NUMERIC_MODIFIER:
                    main_layout.add_widget(
                        Label(
                            text=self.modifiers[behavior][idx]["name"] + " (validate with <Enter>)",
                            size_hint_y=None,
                            # height=40,
                        )
                    )
                    ti = TextInput(
                        text="",
                        multiline=False,
                        size_hint_y=None,
                        # height=40,
                        font_size="25dp",
                        input_type="number",
                        on_text_validate=on_button_release,
                    )
                    self.modifier_buttons[ti] = [behavior, idx, self.modifiers[behavior][idx]["type"], ""]
                    main_layout.add_widget(ti)

            # Go back button
            btn1 = Button(
                text="Go back",
                font_size=font_size,
                size_hint_y=None,
            )
            btn1.bind(on_release=on_goback_button_release)
            self.modifier_buttons[btn1] = [behavior, -1, "", ""]

            main_layout.add_widget(btn1)

            scrollwidget_layout.add_widget(main_layout)

            # return main_layout
            return scrollwidget_layout

        def create_subjects_layout():
            """
            create subject layout
            """

            subjectsList = sorted([BorisApp.project[SUBJECTS][k]["name"] for k in BorisApp.project[SUBJECTS].keys()])

            # check number of subjects

            if len(subjectsList) >= 20:
                subjects_font_size = FONT_MIN_SIZE_SUBJECT
            else:
                subjects_font_size = (FONT_MIN_SIZE_SUBJECT - FONT_MAX_SIZE_SUBJECT) / 20 * len(subjectsList) + FONT_MAX_SIZE_SUBJECT

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

            gdrid_layout = GridLayout(cols=int((len(BorisApp.project[ETHOGRAM]) + 1) ** 0.5), size_hint=(1, 1), spacing=3)

            # check modifiers
            self.modifiers_layout = {}
            for idx in BorisApp.project[ETHOGRAM]:
                self.modifiers[BorisApp.project[ETHOGRAM][idx]["code"]] = BorisApp.project[ETHOGRAM][idx]["modifiers"]

            # font size
            behaviors_font_size = dynamic_font_size(len(BorisApp.project[ETHOGRAM]))

            """
            # if BEHAV_CAT in BorisApp.project:
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
            """

            # for behavior in behaviors_list:
            for idx in BorisApp.project[ETHOGRAM]:
                behavior = BorisApp.project[ETHOGRAM][idx]["code"]
                behav_col = BorisApp.project[ETHOGRAM][idx].get("color", None)
                btn = Button(text=behavior, size_hint_x=1, font_size=behaviors_font_size)
                btn.background_normal = ""
                if (behav_col is not None) and (behav_col != ""):
                    btn.background_color = behav_col
                    btn.color = contrasted_color(behav_col)
                    self.behavior_color[behavior] = behav_col

                else:
                    btn.background_color = GRAY
                    btn.color = contrasted_color("#808080")
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
                self.btnSelSubj.background_color = BLUE
                self.btnSelSubj.bind(on_release=view_subjects_layout)
                hlayout.add_widget(self.btnSelSubj)

            # add stop button
            btn = Button(text="Stop obs", size_hint_x=1, font_size="24dp")
            btn.background_normal = ""
            btn.background_color = DARKRED
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

            for behavior, _ in self.currentStates.get(self.focal_subject, []):
                self.btnList[behavior].background_color = [1, 0, 0, 1]  # red

            self.add_widget(self.behaviorsLayout)

        def view_subjects_layout(obj):
            """
            display subjects page
            """
            self.clear_widgets()
            self.add_widget(self.subjectsLayout)

            print("current focal subject:", self.focal_subject)

        def view_modifiers_layout(behavior):
            """
            show the layout for the modifiers selection
            """

            self.clear_widgets()

            state_behaviors = [
                BorisApp.project[ETHOGRAM][x]["code"]
                for x in BorisApp.project[ETHOGRAM]
                if "STATE EVENT" in BorisApp.project[ETHOGRAM][x]["type"].upper()
            ]

            print(f'{BorisApp.project[OBSERVATIONS][self.obsId]["events"]=}')

            if BorisApp.project[OBSERVATIONS][self.obsId]["start_from_current_time"]:
                time_output = seconds_of_day(dt.datetime.now())
            elif BorisApp.project[OBSERVATIONS][self.obsId]["start_from_current_epoch_time"]:
                time_output = round(self.time_, 3)
            else:
                time_output = round(self.time_ - self.time0, 3)

            print(f"{time_output=}")

            if self.focal_subject == NO_FOCAL_SUBJECT:
                focal_subject = ""
            else:
                focal_subject = self.focal_subject

            current_states_modifiers = get_current_states_modifiers_for_subject(
                state_behaviors, BorisApp.project[OBSERVATIONS][self.obsId]["events"], focal_subject, time_output
            )

            print(f"{current_states_modifiers=}")

            # all modifier buttons to gray
            for btn in self.modifier_buttons:
                if self.modifier_buttons[btn][0] == behavior:
                    if self.modifier_buttons[btn][2] in (SINGLE_SELECTION, MULTI_SELECTION):
                        btn.background_color = GRAY
                    if self.modifier_buttons[btn][2] == NUMERIC_MODIFIER:
                        btn.text = ""

            # set modifier button to red when modifier is active
            for btn in self.modifier_buttons:
                # check if button index != 0 and button correspond to selected behavior
                if self.modifier_buttons[btn][1] and self.modifier_buttons[btn][0] == behavior:
                    # search current modifier
                    for b, m in current_states_modifiers:
                        if b == behavior and self.modifier_buttons[btn][3] == m:
                            btn.background_color = DARKRED

            self.add_widget(self.modifiers_layout[behavior])

        def write_event(event):
            """
            record event in observation
            change button color if STATE event
            """

            time_, newState, modifier = event

            # add event
            if BorisApp.project[OBSERVATIONS][self.obsId]["start_from_current_time"]:
                time_output = seconds_of_day(dt.datetime.now())
            elif BorisApp.project[OBSERVATIONS][self.obsId]["start_from_current_epoch_time"]:
                time_output = round(time_, 3)
            else:
                time_output = round(time_ - self.time0, 3)

            if self.focal_subject == NO_FOCAL_SUBJECT:
                focal_subject = ""
            else:
                focal_subject = self.focal_subject

            print([time_output, focal_subject, newState, modifier, ""])

            if "State" in behaviorType(BorisApp.project[ETHOGRAM], newState):
                # deselect
                if [newState, modifier] in self.currentStates.get(self.focal_subject, []):
                    BorisApp.project[OBSERVATIONS][self.obsId]["events"].append([time_output, focal_subject, newState, modifier, ""])
                    self.btnList[newState].background_color = self.behavior_color[newState]
                    self.btnList[newState].color = contrasted_color(self.behavior_color[newState])
                    self.currentStates[self.focal_subject].remove([newState, modifier])

                # select
                else:
                    # test if state is exclusive
                    if behaviorExcluded(BorisApp.project[ETHOGRAM], newState) != [""]:
                        statesToStop: list = []

                        print(self.currentStates)

                        for current_behavior, current_modifier in self.currentStates.get(self.focal_subject, []):
                            if current_behavior in behaviorExcluded(BorisApp.project[ETHOGRAM], newState):
                                BorisApp.project[OBSERVATIONS][self.obsId]["events"].append(
                                    [time_output, focal_subject, current_behavior, current_modifier, ""]
                                )
                                statesToStop.append([current_behavior, current_modifier])
                                self.btnList[current_behavior].background_color = self.behavior_color[current_behavior]
                                self.btnList[current_behavior].color = contrasted_color(self.behavior_color[current_behavior])

                        for s in statesToStop:
                            self.currentStates[self.focal_subject].remove(s)

                    BorisApp.project[OBSERVATIONS][self.obsId]["events"].append([time_output, focal_subject, newState, modifier, ""])

                    self.btnList[newState].background_color = [1, 0, 0, 1]  # red

                    if self.focal_subject not in self.currentStates:
                        self.currentStates[self.focal_subject] = []
                    self.currentStates[self.focal_subject].append([newState, modifier])

            # point event
            if "Point" in behaviorType(BorisApp.project[ETHOGRAM], newState):
                if behaviorExcluded(BorisApp.project[ETHOGRAM], newState) != [""]:
                    statesToStop: list = []

                    print(self.currentStates)

                    for current_behavior, current_modifier in self.currentStates.get(self.focal_subject, []):
                        if current_behavior in behaviorExcluded(BorisApp.project[ETHOGRAM], newState):
                            BorisApp.project[OBSERVATIONS][self.obsId]["events"].append(
                                [time_output, focal_subject, current_behavior, current_modifier, ""]
                            )
                            statesToStop.append([current_behavior, current_modifier])
                            self.btnList[current_behavior].background_color = self.behavior_color[current_behavior]
                            self.btnList[current_behavior].color = contrasted_color(self.behavior_color[current_behavior])

                    for s in statesToStop:
                        self.currentStates[self.focal_subject].remove(s)

                BorisApp.project[OBSERVATIONS][self.obsId]["events"].append([time_output, focal_subject, newState, modifier, ""])

            with open(BorisApp.projectFileName, "w") as f:
                f.write(json.dumps(BorisApp.project, indent=0))

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
                self.btnSubjectsList[self.focal_subject].background_color = GRAY
                self.focal_subject = NO_FOCAL_SUBJECT
            else:
                if self.focal_subject != NO_FOCAL_SUBJECT:
                    self.btnSubjectsList[self.focal_subject].background_color = GRAY
                self.focal_subject = obj.text
                self.btnSubjectsList[self.focal_subject].background_color = RED

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
                            f.write(json.dumps(BorisApp.project, indent=0))
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

                    w = ViewProjectForm()
                    self.add_widget(w)
                    w.show()

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
                pop.ids.lb_obs_exists.text = f"An observation with the same id and {nb_events} coded events already exists"
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

        if self.day_time_input.active and self.epoch_time_input.active:
            pop = InfoPopup()
            pop.ids.label.text = "You can not select to record the day time together with epoch time"
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

        print(f"{self.iv=}")
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
    mem = {}

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
