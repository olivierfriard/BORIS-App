import sys

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
#from kivy.graphics import Color, Ellipse, Line
import time
from kivy.base import EventLoop
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListItemLabel,ListView

from kivy.adapters.listadapter import ListAdapter

from kivy.uix.filechooser import FileChooserListView

import json

class BORIS(App):

    t0 = 0
    currentStates = []
    btnList = {}
    obsId = ''
    fileName = ''
    behaviors = {}

    def hook_keyboard(self, window, key, *largs):
        if key == 27:
            self.sm.current='home'
            return True 

    sm = ScreenManager()

    def build(self):

        EventLoop.window.bind(on_keyboard=self.hook_keyboard)

        def btn_released(obj):
            t = time.time()
            out = ''
            newState = obj.text

            # state event
            if self.behaviors[ newState ]['type'] == 'state':
                if newState in self.currentStates:
                    out += '{0}\t{1}\tSTOP\n'.format(round(t - self.t0, 3), newState)
                    obj.background_color = [1,1,1,1]
                    self.currentStates.remove(newState)
                else:
                    # test if state is exclusive
                    if self.behaviors[ newState ]['exclude']:
                        statesToStop = []

                        for cs in self.currentStates:
                            if cs in self.behaviors[ newState ]['exclude']:
                                out += '{0}\t{1}\tSTOP\n'.format(round(t - self.t0, 3), cs)
                                statesToStop.append(cs)
                                self.btnList[cs].background_color = [1,1,1,1]

                        for s in statesToStop:
                            self.currentStates.remove(s)

                    out += '{0}\t{1}\tSTART\n'.format(round(t - self.t0, 3), newState)
                    obj.background_color = [5,1,1,1]
                    self.currentStates.append(newState)

            # point event
            if self.behaviors[ newState ]['type'] == 'point':
                out = '{0}\t{1}\n'.format( round(t - self.t0, 3), newState )


            with open(self.fileName,'a') as f:
                f.write(out)


        def btn_new_obs_released(obj):
            self.sm.current = 'ethogram'

        def btn_view_obs_released(obj):
            self.sm.current = 'observations_list'


        def btn_start_released(obj):
            '''
            start a new observaiton
            '''
            if not self.obsId.text: 
                popup = Popup(title='Please note',  content=Label(text='You must choose an id for the new observation'),   size_hint=(None, None), size=(400, 200))
                popup.open()
                return

            self.t0 = time.time()
            self.fileName = self.obsId.text.replace(' ','_').replace('/','_').replace('(','_').replace(')','_')+'.boris_observation.tsv'
            open(self.fileName, 'w')
            self.sm.current = 'behaviors'


        def btn_stop_released(obj):

            self.sm.current = 'confirm_exit'


        def btn_select_ethogram(obj):
            '''
            load ethogram in JSON format
            '''
            if fc.selection:
                try:
                    self.behaviors = json.loads(open(fc.selection[0]).read())
                except:
                    popup = Popup(title='Error', content=Label(text='The selected file is not a BORIS ethogram!'),   size_hint=(None, None), size=(400, 200))
                    popup.open()
                    return

                layout = behaviors_layout(self.behaviors)

                screen = Screen(name='behaviors')
                screen.add_widget(layout)

                self.sm.add_widget(screen)

                self.sm.current = 'new_observation'



        def btn_view_observation(obj):
            '''
            view observation
            '''

            if fc.selection:

                #open(fc.selection[0]).readlines()
                screen = Screen(name='view_observation')
                fileContent = open(fc.selection[0]).readlines()

                adapter = ListAdapter( data = [r.replace('\t','   ') for r in fileContent], cls = ListItemLabel)

                list_view = ListView(adapter = adapter)

                screen.add_widget(list_view)

                self.sm.add_widget(screen)

                self.sm.current = 'view_observation'


        def btn_exit_released(obj):

            if self.fileName: 
                popup = Popup(title='Please note', content=Label(text='A current observation is running'),   size_hint=(None, None), size=(400, 200))
                popup.open()

            sys.exit()

        def btn_confirm(obj):

            if obj.text == 'Yes':
                self.fileName = ''
                self.sm.current = 'home'
            if obj.text == 'No':
                self.sm.current = 'behaviors'



        def behaviors_layout( behaviors ):
            layout = GridLayout(cols= int((len(behaviors)+1)**0.5) , size_hint=(1,1), spacing=5)

            for b in behaviors:
                btn = Button(text = b, size_hint_x = 1, font_size = 24)
                btn.background_color = [ 1,1,1,1 ]
                btn.bind(on_release = btn_released)
                self.btnList[ b ] = btn
                layout.add_widget(btn)

            btn = Button(text = 'Select subject', size_hint_x=1)
            btn.background_color = [ 0,1,0,1 ]
            btn.bind(on_release = btn_stop_released)
            layout.add_widget(btn)

            btn = Button(text = 'Stop obs', size_hint_x=1)
            btn.background_color = [ 1,0,0,1 ]
            btn.bind(on_release = btn_stop_released)
            layout.add_widget(btn)

            return layout



        # home screen
        screen = Screen(name='home')
        layout = BoxLayout(orientation = 'vertical',size_hint_y=1)

        logo = Image(source='logo_boris_500px.png')
        layout.add_widget(logo)

        hlayout = BoxLayout(orientation = 'horizontal', spacing=10, size_hint_y=0.3)

        # start/stop button
        btn = Button(text='New observation',size_hint_x=1, font_size=32)
        btn.background_color = [ 1,0,0,1 ]
        btn.bind(on_release=btn_new_obs_released)
        hlayout.add_widget(btn)

        btn = Button(text='View observation',size_hint_x=1, font_size=32)
        btn.background_color = [ 1,0,0,1 ]
        btn.bind(on_release=btn_view_obs_released)
        hlayout.add_widget(btn)

        btn = Button(text='Exit',size_hint_x=1, font_size=32)
        btn.background_color = [ 1,0,0,1 ]
        btn.bind(on_release=btn_exit_released)
        hlayout.add_widget(btn)

        layout.add_widget(hlayout)

        screen.add_widget(layout)
        self.sm.add_widget(screen)


        # choose ethogram
        screen = Screen(name='ethogram')
        layout = BoxLayout(orientation = 'horizontal')

        fc = FileChooserListView(path='.',filters=['*.boris_ethogram'])

        btn = Button( text='Select ethogram' )
        btn.bind(on_release=btn_select_ethogram)

        layout.add_widget(btn)
        layout.add_widget(fc)

        screen.add_widget(layout)
        self.sm.add_widget(screen)


        # observations list
        screen = Screen(name='observations_list')
        layout = BoxLayout(orientation = 'horizontal')

        fc = FileChooserListView(path='.',filters=['*.boris_observation.tsv'])

        btn = Button( text='View observation' )
        btn.bind(on_release=btn_view_observation)

        layout.add_widget(btn)
        layout.add_widget(fc)

        screen.add_widget(layout)
        self.sm.add_widget(screen)


        # confirm exit
        screen = Screen(name='confirm_exit')
        layout = BoxLayout(orientation = 'vertical')

        layout.add_widget(Label(text='Are you sure you want to stop the current observation?'))

        btn = Button( text='Yes' )
        btn.bind(on_release=btn_confirm)
        layout.add_widget(btn)

        btn = Button( text='No' )
        btn.bind(on_release=btn_confirm)
        layout.add_widget(btn)

        screen.add_widget(layout)
        self.sm.add_widget(screen)




        # observation info
        screen = Screen(name='new_observation')
        
        layout = BoxLayout(orientation = 'vertical', spacing=10)
        
        hlayout = BoxLayout(orientation = 'horizontal', spacing=10)
        hlayout.add_widget(Label(text='Observation id', font_size=24))
        self.obsId = TextInput(multiline=False, font_size=24)
        hlayout.add_widget(self.obsId)
        layout.add_widget( hlayout ) 
        
        btn = Button(text='Start',size_hint_x=1, font_size=32)
        btn.background_color = [ 1,0,0,1 ]
        btn.bind(on_release=btn_start_released)
        layout.add_widget(btn)

        screen.add_widget(layout)
        self.sm.add_widget(screen)

        # behaviors screen
        '''
        screen = Screen(name='behaviors')

        #layout = behaviors_layout({'grooming':{'type':'state','exclude':['eat','sleep']},'eat':{'type':'state','exclude':['sleep']},'sleep':{'type':'state','exclude':['eat']},'jump':{'type':'point','exclude':[]}})
        #screen.add_widget(layout)

        self.sm.add_widget(screen)
        '''

        # view observation
        '''
        screen = Screen(name='view_observation')
        lw = ListView( item_strings = ["Palo Alto, MX", "Palo Alto, US"] )
        screen.add_widget( lw )
        self.sm.add_widget(screen)
        '''


        return self.sm


if __name__ == '__main__':
    BORIS().run()

