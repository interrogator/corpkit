#!/usr/bin/env python

"""
# corpkit GUI
# Daniel McDonald

# This file conains the frontend side of the corpkit gui.
# You can use py2app or pyinstaller on it to make a .app,
# or just run it as a script.

# Below is a string that is used to determine when minor
# updates are available on github for automatic download:
# <updated>DATE-REPLACE</updated>

# Tabbed notebook template created by: 
# Patrick T. Cossette <cold_soul79078@yahoo.com>
"""

from __future__ import print_function

import sys
import string
import time
import os
import threading
import tkMessageBox as messagebox
import tkSimpleDialog as simpledialog
import tkFileDialog as filedialog
try:
    import Tkinter as tkinter
    from Tkinter import *
    from ttk import Progressbar, Style
    from Tkinter import _setit
except ImportError:
    import tkinter
    from tkinter import * 
    from tkinter.ttk import Progressbar, Style
    from tkinter import _setit

# determine path to gui resources:
py_script = False
rd = sys.argv[0]
if sys.platform == 'darwin':
    key = 'Mod1'
    fext = 'app'
    if '.app' in rd:
        rd = os.path.join(rd.split('.app', 1)[0] + '.app', 'Contents', 'MacOS')
else:
    key = 'Control'
    fext = 'exe'
if '.py' in rd:
    py_script = True
    rd = os.path.dirname(os.path.join(rd.split('.py', 1)[0]))

########################################################################

class SplashScreen(object):
    """
    A simple splash screen to display before corpkit is loaded.
    """
    
    def __init__( self, tkRoot, imageFilename, minSplashTime=0):
        import os
        from PIL import Image
        from PIL import ImageTk
        self._root = tkRoot
        self._image = ImageTk.PhotoImage(file=os.path.join(rd, imageFilename))
        self._splash = None
        self._minSplashTime = time.time() + minSplashTime
      
    def __enter__(self):
        # Remove the app window from the display
        #self._root.withdraw( )
        
        # Calculate the geometry to center the splash image
        scrnWt = self._root.winfo_screenwidth()
        scrnHt = self._root.winfo_screenheight()
        
        imgWt = self._image.width()
        imgHt = self._image.height()
        
        imgXPos = (scrnWt / 2) - (imgWt / 2)
        imgYPos = (scrnHt / 2) - (imgHt / 2)

        # Create the splash screen      
        self._splash = Toplevel()
        self._splash.overrideredirect(1)
        self._splash.geometry('+%d+%d' % (imgXPos, imgYPos))

        background_label = Label(self._splash, image=self._image)
        background_label.grid(row=1, column=1, sticky=W)

        # this code shows the version number, but it's ugly.
        #import corpkit
        #oldstver = str(corpkit.__version__)
        #txt = 'Loading corpkit v%s ...' % oldstver
        #cnv = Canvas(self._splash, width=200, height=20)
        #cnv.create_text((100, 14), text=txt, font=("Helvetica", 14, "bold"))
        #cnv.grid(row=1, column=1, sticky='SW', padx=20, pady=20)
        
        self._splash.lift()
        self._splash.update( )
   
    def __exit__( self, exc_type, exc_value, traceback ):
        # Make sure the minimum splash time has elapsed
        timeNow = time.time()
        if timeNow < self._minSplashTime:
            time.sleep( self._minSplashTime - timeNow )
      
        # Destroy the splash window
        self._splash.destroy( )

      # Display the application window
      #self._root.deiconify( )

class RedirectText(object):
    """Send text to app from stdout, for the log and the status bar"""

    def __init__(self, text_ctrl, log_text):
        """Constructor"""
        
        def dumfun():
            """to satisfy ipython, sys, which look for a flush method"""
            pass

        self.output = text_ctrl
        self.log = log_text
        self.flush = dumfun
        self.fileno = dumfun
 
    def write(self, string):
        """Add stdout and stderr to log and/or to console""" 
        import re
        # don't show blank lines
        show_reg = re.compile(r'^\s*$')
        # delete lobal abs paths from traceback
        del_reg = re.compile(r'^/*(Users|usr).*/(site-packages|corpkit/corpkit/)')
        if 'Parsing file' not in string and 'Initialising parser' not in string \
            and not 'Interrogating subcorpus' in string:
            if not re.match(show_reg, string):
                string = re.sub(del_reg, '', string)
                self.log.append(string.rstrip('\n'))
        if not re.match(show_reg, string):
            if not string.lstrip().startswith('#') and not string.lstrip().startswith('import'):
                string = re.sub(del_reg, '', string).rstrip('\n').rstrip()
                string = string.split('\n')[-1]
                self.output.set(string.lstrip().rstrip('\n').rstrip())

class HyperlinkManager:
    """Hyperlinking for About"""
    def __init__(self, text):
        self.text=text
        self.text.tag_config("hyper", foreground="blue", underline=1)
        self.text.tag_bind("hyper", "<Enter>", self._enter)
        self.text.tag_bind("hyper", "<Leave>", self._leave)
        self.text.tag_bind("hyper", "<Button-1>", self._click)
        self.reset()
    def reset(self):
        self.links = {}
    def add(self, action):
        # add an action to the manager.  returns tags to use in
        # associated text widget
        tag = "hyper-%d" % len(self.links)
        self.links[tag] = action
        return "hyper", tag
    def _enter(self, event):
        self.text.config(cursor="hand2")
    def _leave(self, event):
        self.text.config(cursor="")
    def _click(self, event):
        for tag in self.text.tag_names(CURRENT):
            if tag[:6] == "hyper-":
                self.links[tag]()
                return

class Notebook(Frame):
    """Notebook Widget"""
    def __init__(self, parent, activerelief = RAISED, inactiverelief = FLAT, 
                xpad = 4, ypad = 6, activefg = 'black', inactivefg = 'black', 
                activefc = ("Helvetica", 14, "bold"), inactivefc = ("Helvetica", 14), **kw):
        """Construct a Notebook Widget

        Notebook(self, parent, activerelief = RAISED, inactiverelief = RIDGE, 
                 xpad = 4, ypad = 6, activefg = 'black', inactivefg = 'black', **kw)        
    
        Valid resource names: background, bd, bg, borderwidth, class,
        colormap, container, cursor, height, highlightbackground,
        highlightcolor, highlightthickness, relief, takefocus, visual, width, activerelief,
        inactiverelief, xpad, ypad.

        xpad and ypad are values to be used as ipady and ipadx
        with the Label widgets that make up the tabs. activefg and inactivefg define what
        color the text on the tabs when they are selected, and when they are not

        """
        self.activefg = activefg                                                           
        self.inactivefg = inactivefg
        self.activefc = activefc
        self.inactivefc = inactivefc
        self.deletedTabs = []        
        self.xpad = xpad
        self.ypad = ypad
        self.activerelief = activerelief
        self.inactiverelief = inactiverelief                                               
        self.kwargs = kw                                                                   
        self.tabVars = {}                                 
        self.tabs = 0                                                                              
        self.progvar = DoubleVar()
        self.progvar.set(0)
        self.style = Style()
        self.style.theme_use("default")
        self.style.configure("TProgressbar", thickness=15, foreground = '#347DBE', background = '#347DBE')
        self.kwargs = kw                                                                   
        self.tabVars = {}                                                                  #This dictionary holds the label and frame instances of each tab
        self.tabs = 0                                                                      #Keep track of the number of tabs                                                                             
        # the notebook, with its tabs, middle, status bars
        self.noteBookFrame = Frame(parent, bg='#c5c5c5')                                 #Create a frame to hold everything together
        self.BFrame = Frame(self.noteBookFrame, bg='#c5c5c5')
        self.statusbar = Frame(self.noteBookFrame, bd=2, height=25, bg='#F4F4F4')    #Create a frame to put the "tabs" in
        self.progbarspace = Frame(self.noteBookFrame, relief=RAISED, bd=2, height=25)
        self.noteBook = Frame(self.noteBookFrame, relief=RAISED, bd=2, **kw)           #Create the frame that will parent the frames for each tab
        self.noteBook.grid_propagate(0)
        # status bar text and log
        self.status_text=StringVar()
        self.log_stream = []
        #self.imagewatched = StringVar()

        self.text=Label(self.statusbar, textvariable=self.status_text, 
                         height=1, font=("Courier New", 13), width=135, 
                         anchor=W, bg='#F4F4F4')
        self.text.grid(sticky=W)
        self.progbar = Progressbar(self.progbarspace, orient='horizontal', 
                           length = 500, mode='determinate', variable=self.progvar, 
                           style="TProgressbar")
        self.progbar.grid(sticky=E)
        
        # redirect stdout for log
        self.redir = RedirectText(self.status_text, self.log_stream)
        sys.stdout = self.redir
        sys.stderr = self.redir

        Frame.__init__(self)
        self.noteBookFrame.grid()
        self.BFrame.grid(row=0, column=0, columnspan=27, sticky=N) # ", column=13)" puts the tabs in the middle!
        self.noteBook.grid(row=1, column=0, columnspan=27)
        self.statusbar.grid(row=2, column=0, padx=(0, 273))
        self.progbarspace.grid(row=2, column=0, padx=(273, 0), sticky=E)

    def change_tab(self, IDNum):
        """Internal Function"""
        
        for i in (a for a in range(0, len(list(self.tabVars.keys())))):
            if not i in self.deletedTabs:                                                  #Make sure tab hasen't been deleted
                if i != IDNum:                                                             #Check to see if the tab is the one that is currently selected
                    self.tabVars[i][1].grid_remove()                                       #Remove the Frame corresponding to each tab that is not selected
                    self.tabVars[i][0]['relief'] = self.inactiverelief                     #Change the relief of all tabs that are not selected to "Groove"
                    self.tabVars[i][0]['fg'] = self.inactivefg                             #Set the fg of the tab, showing it is selected, default is black
                    self.tabVars[i][0]['font'] = self.inactivefc
                    self.tabVars[i][0]['bg'] = '#c5c5c5'
                else:                                                                      #When on the tab that is currently selected...
                    self.tabVars[i][1].grid()                                              #Re-grid the frame that corresponds to the tab                      
                    self.tabVars[IDNum][0]['relief'] = self.activerelief                   #Change the relief to "Raised" to show the tab is selected
                    self.tabVars[i][0]['fg'] = self.activefg
                    self.tabVars[i][0]['font'] = self.activefc
                    self.tabVars[i][0]['bg'] = 'white'                               #Set the fg of the tab, showing it is not selected, default is black

    def add_tab(self, width=2, **kw):
        import tkinter
        """Creates a new tab, and returns its corresponding frame
        """
        
        temp = self.tabs
        self.tabVars[self.tabs] = [Label(self.BFrame, relief = RIDGE, **kw)]               #Create the tab
        self.tabVars[self.tabs][0].bind("<Button-1>", lambda Event:self.change_tab(temp))  #Makes the tab "clickable"
        self.tabVars[self.tabs][0].pack(side = LEFT, ipady=self.ypad, ipadx=self.xpad) #Packs the tab as far to the left as possible
        self.tabVars[self.tabs].append(Frame(self.noteBook, **self.kwargs))                #Create Frame, and append it to the dictionary of tabs
        self.tabVars[self.tabs][1].grid(row=0, column=0)                               #Grid the frame ontop of any other already existing frames
        self.change_tab(0)                                                                 #Set focus to the first tab
        self.tabs += 1                                                                     #Update the tab count
        return self.tabVars[temp][1]                                                       #Return a frame to be used as a parent to other widgets

    def destroy_tab(self, tab):
        """Delete a tab from the notebook, as well as it's corresponding frame
        """
        
        self.iteratedTabs = 0                                                              #Keep track of the number of loops made
        for b in list(self.tabVars.values()):                                                    #Iterate through the dictionary of tabs
            if b[1] == tab:                                                                #Find the NumID of the given tab
                b[0].destroy()                                                             #Destroy the tab's frame, along with all child widgets
                self.tabs -= 1                                                             #Subtract one from the tab count
                self.deletedTabs.append(self.iteratedTabs)                                 #Apend the NumID of the given tab to the list of deleted tabs
                break                                                                      #Job is done, exit the loop
            self.iteratedTabs += 1                                                         #Add one to the loop count
    
    def focus_on(self, tab):
        """Locate the IDNum of the given tab and use
        change_tab to give it focus
        """
        self.iteratedTabs = 0                                                              #Keep track of the number of loops made
        for b in list(self.tabVars.values()):                                                    #Iterate through the dictionary of tabs
            if b[1] == tab:                                                                #Find the NumID of the given tab
                self.change_tab(self.iteratedTabs)                                         #send the tab's NumID to change_tab to set focus, mimicking that of each tab's event bindings
                break                                                                      #Job is done, exit the loop
            self.iteratedTabs += 1                                                         #Add one to the loop count

def corpkit_gui():
    
    # make app
    root=Tk()
    #minimise it
    root.withdraw( )
    # generate splash
    with SplashScreen(root, 'loading_image.png', 1.0):
        # set app size
        root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
        import warnings
        warnings.filterwarnings("ignore")
        import traceback
        import dateutil
        import sys
        import os
        import corpkit
        from corpkit.process import get_gui_resource_dir, get_fullpath_to_jars
        from tkintertable import TableCanvas, TableModel
        from nltk.draw.table import MultiListbox, Table
        from collections import OrderedDict
        from pandas import Series, DataFrame
        
        # stop warning when insecure download is performed
        import requests
        requests.packages.urllib3.disable_warnings()
        
        # unused in the gui, dummy imports for pyinstaller
        #import seaborn
        import locale
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        from hashlib import md5
        import chardet
        import pyparsing
        # a try statement in case not bundling scipy, which
        # tends to bloat the .app
        try:
            from scipy.stats import linregress
        except:
            pass

        ## add tregex and some other bits to path
        paths = ['', 'dictionaries', 'corpkit', 'nltk_data']
        for p in paths:
            fullp = os.path.join(rd, p).rstrip('/')
            if not fullp in sys.path:
                sys.path.append(fullp)

        # add nltk data to path
        import nltk
        nltk_data_path = os.path.join(rd, 'nltk_data')
        if nltk_data_path not in nltk.data.path:
            nltk.data.path.append(os.path.join(rd, 'nltk_data'))

        # not sure if needed anymore: more path setting        
        corpath = os.path.dirname(corpkit.__file__)
        baspat = os.path.dirname(os.path.dirname(corpkit.__file__))
        dicpath = os.path.join(baspat, 'dictionaries')
        os.environ["PATH"] += os.pathsep + corpath + os.pathsep + dicpath
        sys.path.append(corpath)
        sys.path.append(dicpath)
        sys.path.append(baspat)

        root.title("corpkit")
        root.imagewatched = StringVar()
        #root.overrideredirect(True)
        root.resizable(FALSE,FALSE)
        note=Notebook(root, width= 1365, height=660, activefg = '#000000', inactivefg = '#585555')  #Create a Note book Instance
        note.grid()
        tab0 = note.add_tab(text="Build")
        tab1 = note.add_tab(text="Interrogate")
        tab2 = note.add_tab(text="Edit")       
        tab3 = note.add_tab(text="Visualise")  
        tab4 = note.add_tab(text="Concordance")
        note.text.update_idletasks()

        ###################     ###################     ###################     ###################
        #    VARIABLES    #     #    VARIABLES    #     #    VARIABLES    #     #    VARIABLES    #
        ###################     ###################     ###################     ###################

        # in this section, some recurring, empty variables are defined
        # to do: compress most of the dicts into one

        # round up text so we can bind keys to them later
        all_text_widgets = []

        # for the build tab (could be cleaned up)
        chosen_f = []
        sentdict = {}
        boxes = []
        buildbits = {}
        most_recent_projects = []

        # some variables that will get used throughout the gui
        # a dict of the editor frame names and models
        editor_tables = {}
        currently_in_each_frame = {}
        # for conc sort toggle
        sort_direction = True

        subc_sel_vals = []
        subc_sel_vals_build = []

        # store every interrogation and conc in this session    
        all_interrogations = OrderedDict()
        all_conc = OrderedDict()
        all_images = []
        all_interrogations['None'] = 'None'

        # corpus path setter
        corpus_fullpath = StringVar()
        corpus_fullpath.set('')
        corenlppath = StringVar()
        corenlppath.set(os.path.join(os.path.expanduser("~"), 'corenlp'))

        # visualise
        # where to put the current figure and frame
        thefig = []
        oldplotframe = []

        # for visualise, this holds a list of subcorpora or entries,
        # so that the title will dynamically change at the right time
        single_entry_or_subcorpus = {}
        
        # conc
        # to do: more consistent use of globals!
        itemcoldict = {}
        current_conc = ['None']
        global conc_saved
        conc_saved = False
        import itertools
        try:
            toggle = itertools.cycle([True, False]).__next__
        except AttributeError:
            toggle = itertools.cycle([True, False]).next

        # manage pane: obsolete
        manage_box = {}

        # custom lists
        custom_special_dict = {}
        # just the ones on the hd
        saved_special_dict = {}

        # not currently using this sort feature---should use in conc though
        import itertools
        try:
            direct = itertools.cycle([0,1]).__next__
        except AttributeError:
            direct = itertools.cycle([0,1]).next
        corpus_names_and_speakers = {}

        # datatype of current corpus
        datatype = StringVar()
        datatype.set('-parsed')
        singlefile = IntVar()
        singlefile.set(0)
            
        ###################     ###################     ###################     ###################
        #  DICTIONARIES   #     #  DICTIONARIES   #     #  DICTIONARIES   #     #  DICTIONARIES   #
        ###################     ###################     ###################     ###################

        qd = {'Subjects': r'__ >># @NP',
              'Processes': r'/VB.?/ >># ( VP >+(VP) (VP !> VP $ NP))',
              'Modals': r'MD < __',
              'Participants': r'/(NN|PRP|JJ).?/ >># (/(NP|ADJP)/ $ VP | > VP)',
              'Entities': r'NP <# NNP',
              'Any': 'any'}

        # concordance colours
        colourdict = {1: '#fbb4ae',
                      2: '#b3cde3',
                      3: '#ccebc5',
                      4: '#decbe4',
                      5: '#fed9a6',
                      6: '#ffffcc',
                      7: '#e5d8bd',
                      8: '#D9DDDB',
                      9: '#000000',
                      0: '#F4F4F4'}

        # translate search option for interrogator()
        transdict = {
                'Get distance from root for regex match':           'a',
                'Get tag and word of match':                        'b',
                'Count matches':                                    'c',
                'Get role of match':                                'f',
                'Get "role:dependent", matching governor':          'd',
                'Get ngrams from tokens':                           'j',
                'Get "role:governor", matching dependent':          'g',
                'Get lemmata matching regex':                       'l',
                'Get tokens by role':                               'm',
                'Get ngrams from trees':                            'n',
                'Get part-of-speech tag':                           'p',
                'Regular expression search':                        'r',
                'Get tokens matching regex':                        't',
                'Get stats':                                        's',
                'Get words':                                        'w',
                'Get tokens by regex':                              'h',
                'Get tokens matching list':                         'e'}

        # kinds of search for kinds of data
        option_dict = {'Trees': ['Get words', 
                                 'Get tag and word of match', 
                                 'Count matches', 
                                 'Get part-of-speech tag',
                                 #'Get stats',
                                 'Get ngrams from trees'],
                       'Tokens': ['Get tokens by regex', 
                                 'Get tokens matching list',
                                 'Get ngrams from tokens'], 
                       'Dependencies':
                                ['Get role of match',
                                 'Get lemmata matching regex',
                                 'Get tokens matching regex',
                                 'Get tokens by role',
                                 'Get "role:dependent", matching governor',
                                 'Get "role:governor", matching dependent',
                                 'Get distance from root for regex match'],
                       'Plaintext': 
                                ['Regular expression search', 
                                 'Simple search string search']}

        # translate sort_by for editor
        sort_trans = {'None':           False,
                      'Total':          'total',
                      'Inverse total':  'infreq',
                      'Name':           'name',
                      'Increase':       'increase',
                      'Decrease':       'decrease',
                      'Static':         'static',
                      'Turbulent':      'turbulent',
                      'P value':        'p'}

        # translate special queries for interrogator()
        spec_quer_translate = {'Participants': 'w',
                               'Any':          'any',
                               'Processes':    'w',
                               'Subjects':     'w',
                               'Entities':     'w'}

        convert_name_to_query = {'Trees': 't',
                                'Words': 'w',
                                'POS': 'p',
                                'Lemmata': 'l',
                                'Governor lemmata': 'gl',
                                'Governor functions': 'gf',
                                'Governor POS': 'gp',
                                'Dependent lemmata': 'gl',
                                'Dependent functions': 'gf',
                                'Dependent POS': 'gp',
                                'Functions': 'f',
                                'Governors': 'g',
                                'Dependents': 'd',
                                'N-grams': 'n',
                                'Stats': 's',
                                'Index': 'i'}

        # dependency search names
        depdict = {'Basic': 'basic-dependencies', 
                   'Collapsed': 'collapsed-dependencies', 
                   'CC-processed': 'collapsed-ccprocessed-dependencies'}

        ###################     ###################     ###################     ###################
        #    FUNCTIONS    #     #    FUNCTIONS    #     #    FUNCTIONS    #     #    FUNCTIONS    #
        ###################     ###################     ###################     ###################

        # some functions used throughout the gui

        def focus_next_window(event):
            """tab to next widget"""
            event.widget.tk_focusNext().focus()
            try:
                event.widget.tk_focusNext().selection_range(0, END)
            except:
                pass
            return "break"

        def runner(button, command, conc = False):
            """runs the command of a button, disabling the button till it is done,
            whether it returns early or not"""
            try:
                if button == interrobut or button == interrobut_conc:
                    command(conc)
                else:
                    command()
            except Exception as err:
                import traceback
                print(traceback.format_exc())
                note.progvar.set(0)
            button.config(state=NORMAL)

        def refresh_images(*args):
            """get list of images saved in images folder"""
            import os
            if os.path.isdir(image_fullpath.get()):
                image_list = sorted([f for f in os.listdir(image_fullpath.get()) if f.endswith('.png')])
                for iname in image_list:
                    if iname.replace('.png', '') not in all_images:
                        all_images.append(iname.replace('.png', ''))
            else:
                for i in all_images:
                    all_images.pop(i)
            #refresh()

        # if the dummy variable imagewatched is changed, refresh images
        # this connects to matplotlib's save button, if the modified
        # matplotlib is installed. a better way to do this would be good!
        root.imagewatched.trace("w", refresh_images)

        def timestring(input):
            """print with time prepended"""
            from time import localtime, strftime
            thetime = strftime("%H:%M:%S", localtime())
            print('%s: %s' % (thetime, input.lstrip()))

        def conmap(cnfg, section):
            """helper for load settings"""
            dict1 = {}
            options = cnfg.options(section)
            for option in options:
                try:
                    dict1[option] = cnfg.get(section, option)
                    if dict1[option] == -1:
                        DebugPrint("skip: %s" % option)
                except:
                    print(("exception on %s!" % option))
                    dict1[option] = None
            return dict1

        def convert_pandas_dict_to_ints(dict_obj):
            """try to turn pandas as_dict into ints, for tkintertable

               the huge try statement is to stop errors when there
               is a single corpus --- need to find source of problem
               earlier, though"""
            vals = []
            try:
                for a, b in list(dict_obj.items()):
                    # c = year, d = count
                    for c, d in list(b.items()):
                        vals.append(d)
                if all([float(x).is_integer() for x in vals if is_number(x)]):
                    for a, b in list(dict_obj.items()):
                        for c, d in list(b.items()):
                            if is_number(d):
                                b[c] = int(d)
            except TypeError:
                pass

            return dict_obj

        def update_spreadsheet(frame_to_update, df_to_show=None, model = False, 
                               height=140, width=False, indexwidth=70):
            """refresh a spreadsheet"""
            from collections import OrderedDict
            import pandas

            # colours for tkintertable
            kwarg = {'cellbackgr':              '#F7F7FA',
                      'grid_color':             '#c5c5c5',
                      'entrybackgr':            '#F4F4F4',
                      'selectedcolor':          'white',
                      'rowselectedcolor':       '#b3cde3',
                      'multipleselectioncolor': '#fbb4ae'}
            if width:
                kwarg['width'] = width
            if model and not df_to_show:
                df_to_show = make_df_from_model(model)
                #if need_make_totals:
                df_to_show = make_df_totals(df_to_show)
            if df_to_show is not None:
                # for abs freq, make total
                model = TableModel()
                df_to_show = pandas.DataFrame(df_to_show, dtype = object)
                #if need_make_totals(df_to_show):
                df_to_show = make_df_totals(df_to_show)
                
                # turn pandas into dict
                raw_data = df_to_show.to_dict()
                
                # convert to int if possible
                raw_data = convert_pandas_dict_to_ints(raw_data)
                        
                table = TableCanvas(frame_to_update, model=model, 
                                    showkeynamesinheader=True, 
                                    height=height,
                                    rowheaderwidth=row_label_width.get(), cellwidth=cell_width.get(), **kwarg)
                table.createTableFrame()
                model = table.model
                model.importDict(raw_data)
                # move columns into correct positions
                for index, name in enumerate(list(df_to_show.index)):
                    model.moveColumn(model.getColumnIndex(name), index)
                table.createTableFrame()
                # sort the rows
                if 'tkintertable-order' in list(df_to_show.index):
                    table.sortTable(columnName = 'tkintertable-order')
                    ind = model.columnNames.index('tkintertable-order')
                    try:
                        model.deleteColumn(ind)
                    except:
                        pass
                if 'Total' in list(df_to_show.index):
                    table.sortTable(columnName = 'Total', reverse = True)
                elif len(df_to_show.index) == 1:
                    table.sortTable(columnIndex = 0, reverse = True)

                else:
                    #nm = os.path.basename(corpus_fullpath.get().rstrip('/'))
                    ind = len(df_to_show.columns) - 1
                    table.sortTable(columnIndex = ind, reverse = 1)
                    #pass

                table.redrawTable()
                editor_tables[frame_to_update] = model
                currently_in_each_frame[frame_to_update] = df_to_show
                return

            if model:
                table = TableCanvas(frame_to_update, model=model, 
                                    showkeynamesinheader=True, 
                                    height=height,
                                    rowheaderwidth=row_label_width.get(), cellwidth=cell_width.get(),
                                    **kwarg)
                table.createTableFrame()
                try:
                    table.sortTable(columnName = 'Total', reverse = direct())
                except:
                    direct()           
                    table.sortTable(reverse = direct())
                table.createTableFrame()
                table.redrawTable()
            else:
                table = TableCanvas(frame_to_update, height=height, cellwidth=cell_width.get(), 
                    showkeynamesinheader=True, rowheaderwidth=row_label_width.get(), **kwarg)
                table.createTableFrame()            # sorts by total freq, ok for now
                table.redrawTable()

        def remake_special_query(query, return_list = False):
            """turn special queries (LIST:NAME) into appropriate regexes, lists, etc"""
            # for custom queries
            from collections import namedtuple

            def convert(dictionary):
                """convert dict to named tuple"""
                return namedtuple('outputnames', list(dictionary.keys()))(**dictionary)

            # possible identifiers of special queries---some obsolete or undocumented
            lst_of_specials = ['PROCESSES:',
                               'ROLES:',
                               'WORDLISTS:',
                               'CUSTOM:',
                               'LIST:']

            if any([special in query for special in lst_of_specials]):
                #timestring('Special query detected. Loading wordlists ... ')
                
                # get all our lists, and a regex maker for them
                from dictionaries.process_types import processes
                from dictionaries.roles import roles
                from dictionaries.wordlists import wordlists
                from corpkit.other import as_regex

                customs = convert(custom_special_dict)

                # map the special query type to the named tuple ... largely obsolete
                dict_of_specials = {'PROCESSES:': processes,
                                    'ROLES:': roles, 
                                    'WORDLISTS:': wordlists,
                                    'CUSTOM:': customs,
                                    'LIST:': customs}

                for special in lst_of_specials:
                    if special in query:
                        # possible values after colon
                        types = [k for k in list(dict_of_specials[special].__dict__.keys())]
                        # split up the query by the first part of the special query
                        reg = re.compile('(^.*)(%s)(:)([A-Z0-9_]+)(.*$)' % special[:-1])
                        # split the query into parts
                        divided = re.search(reg, query)
                        # set the right boundaries: line only
                        the_bound = 'l'
                        try:
                            # when custom, the keys *are* capitalised :)
                            if special != 'CUSTOM:' and special != 'LIST:':
                                lst_of_matches = dict_of_specials[special].__dict__[divided.group(4).lower()]
                            else:
                                lst_of_matches = dict_of_specials[special].__dict__[divided.group(4)]
                            if return_list:
                                return lst_of_matches
                            asr = as_regex(lst_of_matches, 
                                           boundaries = the_bound, 
                                           case_sensitive = bool(case_sensitive.get()), 
                                           inverse = False)
                            query = divided.group(1) + asr + divided.group(5)
                        except:
                            timestring('"%s" not found in wordlists.' % divided.group(4))
                            return False                
            return query

        def ignore():
            """turn this on when buttons should do nothing"""
            return "break"

        def need_make_totals(df):
            """check if a df needs totals"""
            if len(list(df.index)) < 3:
                return False
            try:
                x = df.iloc[0,0]
            except:
                return False
            # if was_series, basically
            try:
                vals = [i for i in list(df.iloc[0,].values) if is_number(i)]
            except TypeError:
                return False
            if len(vals) == 0:
                return False
            if all([float(x).is_integer() for x in vals]):
                return True
            else:
                return False

        def make_df_totals(df):
            """make totals for a dataframe"""   
            df = df.drop('Total', errors = 'ignore')
            # add new totals
            df.ix['Total'] = df.drop('tkintertable-order', errors = 'ignore').sum().astype(object)
            return df

        def make_df_from_model(model):
            """generate df from spreadsheet"""
            import pandas
            from io import StringIO
            recs = model.getAllCells()
            colnames = model.columnNames
            collabels = model.columnlabels
            row=[]
            csv_data = []
            for c in colnames:
                row.append(collabels[c])
            try:
                csv_data.append(','.join([str(s, errors = 'ignore') for s in row]))
            except TypeError:
                csv_data.append(','.join([str(s) for s in row]))
            #csv_data.append('\n')
            for row in list(recs.keys()):
                rowname = model.getRecName(row)
                try:
                    csv_data.append(','.join([str(rowname, errors = 'ignore')] + [str(s, errors = 'ignore') for s in recs[row]]))
                except TypeError:
                    csv_data.append(','.join([str(rowname)] + [str(s) for s in recs[row]]))

                #csv_data.append('\n')
                #writer.writerow(recs[row])
            csv = '\n'.join(csv_data)
            uc = unicode(csv, errors = 'ignore')
            newdata = pandas.read_csv(StringIO(uc), index_col=0, header=0)
            newdata = pandas.DataFrame(newdata, dtype = object)
            newdata = newdata.T
            newdata = newdata.drop('Total', errors = 'ignore')
            newdata = add_tkt_index(newdata)
            if need_make_totals(newdata):
                newdata = make_df_totals(newdata)
            return newdata

        def color_saved(lb, savepath = False, colour1 = '#D9DDDB', colour2 = 'white', 
                        ext = '.p', lists = False):
            """make saved items in listbox have colour background

            lb: listbox to colour
            savepath: where to look for existing files
            colour1, colour2: what to colour foundd and not found
            ext: what to append to filenames when searching for them
            lists: if working with wordlists, things need to be done differently, more colours"""
            all_items = [lb.get(i) for i in range(len(lb.get(0, END)))]

            # define colours for permanent lists in wordlists
            if lists:
                colour3 = '#ffffcc'
                colour4 = '#fed9a6'
            for index, item in enumerate(all_items):
                # check if saved
                if not lists:
                    issavedfile = os.path.isfile(os.path.join(savepath, urlify(item) + ext))
                    issaveddir = os.path.isdir(os.path.join(savepath, urlify(item)))
                    if issaveddir or issavedfile:
                        issaved = True
                    else:
                        issaved = False
                # for lists, check if permanently stored
                else:
                    issaved = False
                    if item in list(saved_special_dict.keys()):
                        issaved = True
                    if current_corpus.get() + '-' + item in list(saved_special_dict.keys()):
                        issaved = True
                if issaved:
                    lb.itemconfig(index, {'bg':colour1})
                else:
                    lb.itemconfig(index, {'bg':colour2})
                if lists:
                    if item in list(predict.keys()):

                        if item.endswith('_ROLE'):
                            lb.itemconfig(index, {'bg':colour3})
                        else:
                            lb.itemconfig(index, {'bg':colour4})
            lb.selection_clear(0, END)

        def paste_into_textwidget(*args):
            """paste function for widgets ... doesn't seem to work as expected"""
            try:
                start = args[0].widget.index("sel.first")
                end = args[0].widget.index("sel.last")
                args[0].widget.delete(start, end)
            except TclError as e:
                # nothing was selected, so paste doesn't need
                # to delete anything
                pass
            # for some reason, this works with the error.
            try:
                args[0].widget.insert("insert", clipboard.rstrip('\n'))
            except NameError:
                pass

        def copy_from_textwidget(*args):
            """more commands for textwidgets"""
            #args[0].widget.clipboard_clear()
            text=args[0].widget.get("sel.first", "sel.last").rstrip('\n')
            args[0].widget.clipboard_append(text)

        def cut_from_textwidget(*args):
            """more commands for textwidgets"""
            text=args[0].widget.get("sel.first", "sel.last")
            args[0].widget.clipboard_append(text)
            args[0].widget.delete("sel.first", "sel.last")

        def select_all_text(*args):
            """more commands for textwidgets"""
            try:
                args[0].widget.selection_range(0, END)
            except:
                args[0].widget.tag_add("sel","1.0","end")

        def update_available_corpora(delete = False):
            """updates corpora in project, and returns a list of them"""
            import os
            fp = corpora_fullpath.get()
            all_corpora = sorted([d for d in os.listdir(fp) if os.path.isdir(os.path.join(fp, d)) and '/' not in d])
            for om in [available_corpora, available_corpora_build]:
                om.config(state=NORMAL)
                om['menu'].delete(0, 'end')
                if not delete:
                    for corp in all_corpora:
                        om['menu'].add_command(label=corp, command=_setit(current_corpus, corp))

            return all_corpora

        def refresh():
            """refreshes the list of dataframes in the editor and plotter panes"""
            import os
            # Reset name_of_o_ed_spread and delete all old options
            # get the latest only after first interrogation
            if len(list(all_interrogations.keys())) == 1:
                selected_to_edit.set(list(all_interrogations.keys())[-1])
            dataframe1s['menu'].delete(0, 'end')
            dataframe2s['menu'].delete(0, 'end')
            every_interrogation['menu'].delete(0, 'end')
            #every_interro_listbox.delete(0, 'end')
            #every_image_listbox.delete(0, 'end')
            new_choices = []
            for interro in list(all_interrogations.keys()):
                new_choices.append(interro)
            new_choices = tuple(new_choices)
            dataframe2s['menu'].add_command(label='Self', command=_setit(data2_pick, 'Self'))
            if project_fullpath.get() != '' and project_fullpath.get() != rd:
                dpath = os.path.join(project_fullpath.get(), 'dictionaries')
                if os.path.isdir(dpath):
                    dicts = sorted([f.replace('.p', '') for f in os.listdir(dpath) if os.path.isfile(os.path.join(dpath, f)) and f.endswith('.p')])
                    for d in dicts:
                        dataframe2s['menu'].add_command(label=d, command=_setit(data2_pick, d))
            for choice in new_choices:
                dataframe1s['menu'].add_command(label=choice, command=_setit(selected_to_edit, choice))
                dataframe2s['menu'].add_command(label=choice, command=_setit(data2_pick, choice))
                every_interrogation['menu'].add_command(label=choice, command=_setit(data_to_plot, choice))

            refresh_images()

            # refresh 
            prev_conc_listbox.delete(0, 'end')
            for i in sorted(all_conc.keys()):
                prev_conc_listbox.insert(END, i)

        def add_tkt_index(df):
            """add order to df for tkintertable"""
            import pandas
            df = df.T
            df = df.drop('tkintertable-order', errors = 'ignore', axis = 1)
            df['tkintertable-order'] = pandas.Series([index for index, data in enumerate(list(df.index))], index = list(df.index))
            df = df.T
            return df

        def namer(name_box_text, type_of_data = 'interrogation'):
            """returns a name to store interrogation/editor result as"""
            if name_box_text.lower() == 'untitled' or name_box_text == '':
                c = 0
                the_name = '%s-%s' % (type_of_data, str(c).zfill(2))
                while any(x.startswith(the_name) for x in list(all_interrogations.keys())):
                    c += 1
                    the_name = '%s-%s' % (type_of_data, str(c).zfill(2))
            else:
                the_name = name_box_text
            return the_name

        def show_prev():
            """show previous interrogation"""
            import pandas
            currentname = name_of_interro_spreadsheet.get()
            # get index of current index
            if not currentname:
                prev.configure(state=DISABLED)
                return
            ind = list(all_interrogations.keys()).index(currentname)
            # if it's higher than zero
            if ind > 0:
                if ind == 1:
                    prev.configure(state=DISABLED)
                    nex.configure(state=NORMAL)
                else:
                    if ind + 1 < len(list(all_interrogations.keys())):
                        nex.configure(state=NORMAL)
                    prev.configure(state=NORMAL)

                newname = list(all_interrogations.keys())[ind - 1]
                newdata = all_interrogations[newname]
                name_of_interro_spreadsheet.set(newname)
                i_resultname.set('Interrogation results: %s' % str(name_of_interro_spreadsheet.get()))
                if isinstance(newdata, pandas.DataFrame):
                    toshow = newdata
                    toshowt = newdata.sum()
                elif hasattr(newdata, 'results') and newdata.results is not None:
                    toshow = newdata.results
                    if hasattr(newdata, 'totals') and newdata.results is not None:
                        toshowt = pandas.DataFrame(newdata.totals, dtype = object)
                update_spreadsheet(interro_results, toshow, height=340)
                update_spreadsheet(interro_totals, toshowt, height=10)
                refresh()
            else:
                prev.configure(state=DISABLED)
                nex.configure(state=NORMAL)

        def show_next():
            """show next interrogation"""
            import pandas
            currentname = name_of_interro_spreadsheet.get()
            if currentname:
                ind = list(all_interrogations.keys()).index(currentname)
            else:
                ind = 0
            if ind > 0:
                prev.configure(state=NORMAL)
            if ind + 1 < len(list(all_interrogations.keys())):
                if ind + 2 == len(list(all_interrogations.keys())):
                    nex.configure(state=DISABLED)
                    prev.configure(state=NORMAL)
                else:
                    nex.configure(state=NORMAL)
                newname = list(all_interrogations.keys())[ind + 1]
                newdata = all_interrogations[newname]
                name_of_interro_spreadsheet.set(newname)
                i_resultname.set('Interrogation results: %s' % str(name_of_interro_spreadsheet.get()))
                if isinstance(newdata, pandas.DataFrame):
                    toshow = newdata
                    toshowt = newdata.sum()
                elif hasattr(newdata, 'results') and newdata.results is not None:
                    toshow = newdata.results
                    if hasattr(newdata, 'totals') and newdata.results is not None:
                        toshowt = newdata.totals
                update_spreadsheet(interro_results, toshow, height=340)
                totals_as_df = pandas.DataFrame(toshowt, dtype = object)
                update_spreadsheet(interro_totals, toshowt, height=10)
                refresh()
            else:
                nex.configure(state=DISABLED)
                prev.configure(state=NORMAL)

        def save_as_dictionary():
            """save a word frequency dict of current interrogation for 
               use as reference corpus"""
            import os
            import pandas
            import pickle
            
            dpath = os.path.join(project_fullpath.get(), 'dictionaries')
            dataname = name_of_interro_spreadsheet.get()
            fname = urlify(dataname)
            if fname.startswith('interrogation') or fname.startswith('edited'):
                fname = simpledialog.askstring('Dictionary name', 'Choose a name for your dictionary:')
            if fname == '' or fname is False:
                return
            else:
                fname = fname
            if not fname.endswith('.p'):
                fname += '.p'
            fpn = os.path.join(dpath, fname)
            data = all_interrogations[dataname]
            if data.results is not None:
                as_series = data.results.sum()
                with open(fpn, 'w') as fo: 
                    pickle.dump(as_series, fo)
                timestring('Dictionary created: %s' % (os.path.join('dictionaries', fname)))
                refresh()
            else:
                timestring('No results branch found, sorry.')
                return

        def exchange_interro_branch(namedtupname, newdata, branch = 'results'):
            """replaces a namedtuple results/totals with newdata
               --- such a hack, should upgrade to recordtype"""
            namedtup = all_interrogations[namedtupname]
            the_branch = getattr(namedtup, branch)
            if branch == 'results':
                the_branch.drop(the_branch.index, inplace = True)
                the_branch.drop(the_branch.columns, axis = 1, inplace = True)
                for i in list(newdata.columns):
                    the_branch[i] = i
                for index, i in enumerate(list(newdata.index)):
                    the_branch.loc[i] = newdata.ix[index]
            elif branch == 'totals':
                the_branch.drop(the_branch.index, inplace = True)
                for index, datum in zip(newdata.index, newdata.iloc[:,0].values):
                    the_branch.set_value(index, datum)
            all_interrogations[namedtupname] = namedtup

        def update_interrogation(table_id, id, is_total = False):
            """takes any changes made to spreadsheet and saves to the interrogation
            id: 0 = interrogator
                1 = old editor window
                2 = new editor window"""

            model=editor_tables[table_id]
            newdata = make_df_from_model(model)
            if need_make_totals(newdata):
                newdata = make_df_totals(newdata)

            if id == 0:
                name_of_interrogation = name_of_interro_spreadsheet.get()
            if id == 1:
                name_of_interrogation = name_of_o_ed_spread.get()
            if id == 2:
                name_of_interrogation = name_of_n_ed_spread.get()
            if not is_total:
                exchange_interro_branch(name_of_interrogation, newdata, branch = 'results')
            else:
                exchange_interro_branch(name_of_interrogation, newdata, branch = 'totals')

        def update_all_interrogations(pane = 'interrogate'):
            import pandas
            """update all_interrogations within spreadsheet data
            need a very serious cleanup!"""
            # to do: only if they are there!
            if pane == 'interrogate':
                update_interrogation(interro_results, id = 0)
                update_interrogation(interro_totals, id = 0, is_total = True)
            if pane == 'edit':
                update_interrogation(o_editor_results, id = 1)
                update_interrogation(o_editor_totals, id = 1, is_total = True)
                # update new editor sheet if it's there
                if name_of_n_ed_spread.get() != '':
                    update_interrogation(n_editor_results, id = 2)
                    update_interrogation(n_editor_totals, id = 2, is_total = True)
            timestring('Updated interrogations with manual data.')
            if pane == 'interrogate':
                the_data = all_interrogations[name_of_interro_spreadsheet.get()]
                tot = pandas.DataFrame(the_data.totals, dtype = object)
                
                if the_data.results is not None:
                    update_spreadsheet(interro_results, the_data.results, height=340)
                else:
                    update_spreadsheet(interro_results, df_to_show=None, height=340)

                update_spreadsheet(interro_totals, tot, height=10)
            if pane == 'edit':
                the_data = all_interrogations[name_of_o_ed_spread.get()]
                there_is_new_data = False
                try:
                    newdata = all_interrogations[name_of_n_ed_spread.get()]
                    there_is_new_data = True
                except:
                    pass
                if the_data.results is not None:
                    update_spreadsheet(o_editor_results, the_data.results, height=140)
                update_spreadsheet(o_editor_totals, pandas.DataFrame(the_data.totals, dtype = object), height=10)
                if there_is_new_data:
                    if newdata != 'None' and newdata != '':
                        if the_data.results is not None:
                            update_spreadsheet(n_editor_results, newdata.results, height=140)
                        update_spreadsheet(n_editor_totals, pandas.DataFrame(newdata.totals, dtype = object), height=10)
                if name_of_o_ed_spread.get() == name_of_interro_spreadsheet.get():
                    the_data = all_interrogations[name_of_interro_spreadsheet.get()]
                    tot = pandas.DataFrame(the_data.totals, dtype = object)
                    if the_data.results is not None:
                        update_spreadsheet(interro_results, the_data.results, height=340)
                    update_spreadsheet(interro_totals, tot, height=10)
            
            timestring('Updated spreadsheet display in edit window.')

        from corpkit.process import is_number

        ###################     ###################     ###################     ###################
        #PREFERENCES POPUP#     #PREFERENCES POPUP#     #PREFERENCES POPUP#     #PREFERENCES POPUP#
        ###################     ###################     ###################     ###################

        # make variables with default values

        do_auto_update = IntVar()
        do_auto_update.set(1)

        do_auto_update_this_session = IntVar()
        do_auto_update_this_session.set(1)

        #conc_when_int = IntVar()
        #conc_when_int.set(1)

        only_format_match = IntVar()
        only_format_match.set(0)

        files_as_subcorpora = IntVar()
        files_as_subcorpora.set(0)

        do_concordancing = IntVar()
        do_concordancing.set(1)

        noregex = IntVar()
        noregex.set(0)

        parser_memory = StringVar()
        parser_memory.set(str(2000))

        truncate_conc_after = IntVar()
        truncate_conc_after.set(1000)

        truncate_spreadsheet_after = IntVar()
        truncate_spreadsheet_after.set(9999)

        corenlppath = StringVar()
        corenlppath.set(os.path.join(os.path.expanduser("~"), 'corenlp'))

        row_label_width=IntVar()
        row_label_width.set(100)

        cell_width=IntVar()
        cell_width.set(50)

        p_val = DoubleVar()
        p_val.set(0.05)        

        # a place for the toplevel entry info
        entryboxes = OrderedDict()

        # fill it with null data
        for i in range(10):
            tmp = StringVar()
            tmp.set('')
            entryboxes[i] = tmp

        def preferences_popup():
            try:
                global toplevel
                toplevel.destroy()
            except:
                pass

            from tkinter import Toplevel
            pref_pop = Toplevel()
            #pref_pop.config(background = '#F4F4F4')
            pref_pop.geometry('+300+100')
            pref_pop.title("Preferences")
            #pref_pop.overrideredirect(1)
            pref_pop.wm_attributes('-topmost', 1)
            Label(pref_pop, text='').grid(row=0, column=0, pady=2)
            
            def quit_coding(*args):
                save_tool_prefs(printout = True)
                pref_pop.destroy()

            tmp = Checkbutton(pref_pop, text='Automatically check for updates', variable=do_auto_update, onvalue=1, offvalue=0)
            if do_auto_update.get() == 1:
                tmp.select()
            all_text_widgets.append(tmp)
            tmp.grid(row=0, column=0, sticky=W)
            
            Label(pref_pop, text='Truncate concordance lines').grid(row=1, column=0, sticky=W)
            tmp = Entry(pref_pop, textvariable=truncate_conc_after, width=7)
            all_text_widgets.append(tmp)
            tmp.grid(row=1, column=1, sticky=E)

            Label(pref_pop, text='Truncate spreadsheets').grid(row=2, column=0, sticky=W)
            tmp = Entry(pref_pop, textvariable=truncate_spreadsheet_after, width=7)
            all_text_widgets.append(tmp)
            tmp.grid(row=2, column=1, sticky=E)

            Label(pref_pop, text='CoreNLP memory allocation (MB)').grid(row=3, column=0, sticky=W)
            tmp = Entry(pref_pop, textvariable=parser_memory, width=7)
            all_text_widgets.append(tmp)
            tmp.grid(row=3, column=1, sticky=E)

            Label(pref_pop, text='Spreadsheet cell width').grid(row=4, column=0, sticky=W)
            tmp = Entry(pref_pop, textvariable=cell_width, width=7)
            all_text_widgets.append(tmp)
            tmp.grid(row=4, column=1, sticky=E)

            Label(pref_pop, text='Spreadsheet row header width').grid(row=5, column=0, sticky=W)
            tmp = Entry(pref_pop, textvariable=row_label_width, width=7)
            all_text_widgets.append(tmp)
            tmp.grid(row=5, column=1, sticky=E)

            Label(pref_pop, text='P value').grid(row=6, column=0, sticky=W)
            tmp = Entry(pref_pop, textvariable=p_val, width=7)
            all_text_widgets.append(tmp)
            tmp.grid(row=6, column=1, sticky=E)

            Label(pref_pop, text='CoreNLP path:', justify=LEFT).grid(row=7, column=0, sticky=W, rowspan = 1)
            Button(pref_pop, text='Change', command=set_corenlp_path, width =5).grid(row=7, column=1, sticky=E)
            Label(pref_pop, textvariable=corenlppath, justify=LEFT).grid(row=8, column=0, sticky=W)
            #set_corenlp_path

            tmp = Checkbutton(pref_pop, text='Treat files as subcorpora', variable=files_as_subcorpora, onvalue=1, offvalue=0)
            tmp.grid(row=9, column=0, pady=(0,0), sticky=W)

            tmp = Checkbutton(pref_pop, text='Disable regex for plaintext', variable=noregex, onvalue=1, offvalue=0)
            tmp.grid(row=9, column=1, pady=(0,0), sticky=W)

            tmp = Checkbutton(pref_pop, text='Do concordancing', variable=do_concordancing, onvalue=1, offvalue=0)
            tmp.grid(row=10, column=0, pady=(0,0), sticky=W)

            tmp = Checkbutton(pref_pop, text='Format concordance context', variable=only_format_match, onvalue=1, offvalue=0)
            tmp.grid(row=10, column=1, pady=(0,0), sticky=W)

            stopbut = Button(pref_pop, text='Done', command=quit_coding)
            stopbut.grid(row=12, column=0, columnspan=2, pady=15)        

            pref_pop.bind("<Return>", quit_coding)
            pref_pop.bind("<Tab>", focus_next_window)

        ###################     ###################     ###################     ###################
        # INTERROGATE TAB #     # INTERROGATE TAB #     # INTERROGATE TAB #     # INTERROGATE TAB #
        ###################     ###################     ###################     ###################

        # hopefully weighting the two columns, not sure if works

        interro_opt = Frame(tab1)
        interro_opt.grid(row=0, column=0)

        tab1.grid_columnconfigure(2, weight=5)

        def do_interrogation(conc = True):
            """the main function: calls interrogator()"""
            import pandas
            from corpkit.interrogator import interrogator
            from corpkit.interrogation import Interrogation, Interrodict
            doing_concondancing = True
            # no pressing while running
            #if not conc:
            interrobut.config(state=DISABLED)
            #else:
            interrobut_conc.config(state=DISABLED)
            recalc_but.config(state=DISABLED)
            # progbar to zero
            note.progvar.set(0)
            for i in list(itemcoldict.keys()):
                del itemcoldict[i]
            
            # spelling conversion?
            conv = (spl.var).get()
            if conv == 'Convert spelling' or conv == 'Off':
                conv = False
            
            # lemmatag: do i need to add as button if trees?
            lemmatag = False

            # just in case
            query = False

            # special queries via dropdown
            if special_queries.get() != 'Off' and special_queries.get() != 'Stats':
                query = qd[special_queries.get()]
                datatype_picked.set('Trees')

            else:
                if special_queries.get() != 'Stats':
                    query = qa.get(1.0, END)
                    query = query.replace('\n', '')
                    # allow list queries
                    if query.startswith('[') and query.endswith(']') and ',' in query:
                        query = query.lstrip('[').rstrip(']').replace("'", '').replace('"', '').replace(' ', '').split(',')
                    #elif transdict[searchtype()] in ['e', 's']:
                        #query = query.lstrip('[').rstrip(']').replace("'", '').replace('"', '').replace(' ', '').split(',')
                    else:
                        # convert special stuff
                        query = remake_special_query(query)
                        if query is False:
                            return

            # make name for interrogation
            the_name = namer(nametext.get(), type_of_data='interrogation')
            
            selected_option = datatype_picked.get().lower()[0]

            if selected_option == '':
                timestring('You need to select a search type.')
                return

            queryd = {}
            for k, v in list(additional_criteria.items()):
                queryd[k] = v
            queryd[selected_option] = query

            if selected_option == 's':
                queryd = {'s': 'any'}
                doing_concondancing = False

            # to do: make this order customisable for the gui too
            poss_returns = [return_function, return_pos, return_lemma, return_token, \
                            return_gov, return_dep, return_tree, return_index, return_distance, \
                            return_count, return_gov_lemma, return_gov_pos, return_gov_func, \
                            return_dep_lemma, return_dep_pos, return_dep_func, \
                            return_ngm_lemma, return_ngm_pos, return_ngm_func, return_ngm]

            to_show = [i.get() for i in poss_returns if i.get() != '']
            if not to_show and not selected_option == 's':
                timestring('Interrogation must return something.')
                return
            
            if 'c' in to_show:
                doing_concondancing = False

            if not do_concordancing.get():
                doing_concondancing = False

            if noregex.get() == 1:
                regex = False
            else:
                regex = True

            # default interrogator args: root and note pass the gui itself for updating
            # progress bar and so on.
            interrogator_args = {'search': queryd,
                                 'show': to_show,
                                 'case_sensitive': bool(case_sensitive.get()),
                                 'spelling': conv,
                                 'root': root,
                                 'note': note,
                                 'df1_always_df': True,
                                 'do_concordancing': doing_concondancing,
                                 'only_format_match': not bool(only_format_match.get()),
                                 'dep_type': depdict[kind_of_dep.get()],
                                 'nltk_data_path': nltk_data_path,
                                 'regex': regex,
                                 'files_as_subcorpora': bool(files_as_subcorpora.get())}

            excludes = {}
            for k, v in list(ex_additional_criteria.items()):
                if k != 'None':
                    excludes[k.lower()[0]] = v
            if exclude_op.get() != 'None':
                q = remake_special_query(exclude_str.get(), return_list=True)
                if q:
                    excludes[exclude_op.get().lower()[0]] = q

            if excludes:
                interrogator_args['exclude'] = excludes

            try:
                interrogator_args['searchmode'] = anyall.get()
            except:
                pass
            try:
                interrogator_args['excludemode'] = excludemode.get()
            except:
                pass

            # speaker ids
            if only_sel_speakers.get():
                ids = [int(i) for i in speaker_listbox.curselection()]
                jspeak = [speaker_listbox.get(i) for i in ids]
                # in the gui, we can't do 'each' queries (right now)
                if 'ALL' in jspeak:
                    jspeak = 'each'
                interrogator_args['just_speakers'] = jspeak
            
            # translate lemmatag
            tagdict = {'Noun': 'n',
                       'Adjective': 'a',
                       'Verb': 'v',
                       'Adverb': 'r',
                       'None': False,
                       '': False,
                       'Off': False}

            interrogator_args['lemmatag'] = tagdict[lemtag.get()]

            if corpus_fullpath.get() == '':
                timestring('You need to select a corpus.')
                return

            # stats preset is actually a search type
            if special_queries.get() == 'Stats':
                selected_option = 's'
                interrogator_args['query'] = 'any'

            # if ngramming, there are two extra options
            if selected_option.startswith('n') or any(x.startswith('n') for x in to_show):
                global ngmsize
                if (ngmsize.var).get() != 'Size':
                    interrogator_args['gramsize'] = int((ngmsize.var).get())

                global split_contract
                interrogator_args['split_contractions'] = split_contract.get()

            if subc_pick.get() == "Subcorpus" or subc_pick.get().lower() == 'all' or \
                selected_corpus_has_no_subcorpora.get() == 1:
                corp_to_search = corpus_fullpath.get()
            else:
                corp_to_search = os.path.join(corpus_fullpath.get(), subc_pick.get())

            # do interrogation, return if empty
            interrodata = interrogator(corp_to_search, **interrogator_args)
            if isinstance(interrodata, Interrogation):
                if hasattr(interrodata, 'results') and interrodata.results is not None:
                    if interrodata.results.empty:
                        timestring('No results found, sorry.')
                        return 

            if selected_option == 's':
                featfile = os.path.join(savedinterro_fullpath.get(), current_corpus.get() + '-' + 'features.p')
                if not os.path.isfile(featfile):
                    interrodata.save('features', savedir=savedinterro_fullpath.get())
            
            # make sure we're redirecting stdout again
            sys.stdout = note.redir

            # update spreadsheets
            if not isinstance(interrodata, (Interrogation, Interrodict)):
                update_spreadsheet(interro_results, df_to_show=None, height=340)
                update_spreadsheet(interro_totals, df_to_show=None, height=10)            
                return

            # make non-dict results into dict, so we can iterate no matter
            # if there were multiple results or not
            interrogation_returned_dict = False
            from collections import OrderedDict
            if isinstance(interrodata, Interrogation):
                dict_of_results = OrderedDict({the_name: interrodata})
            else:
                dict_of_results = interrodata
                interrogation_returned_dict = True

            # remove dummy entry from master
            all_interrogations.pop('None', None)

            # post-process each result and add to master list
            for nm, r in sorted(dict_of_results.items(), key=lambda x: x[0]):
                # drop over 9999
                # type check probably redundant now
                if r.results is not None:
                    large = [n for i, n in enumerate(list(r.results.columns)) if i > truncate_spreadsheet_after.get()]
                    r.results.drop(large, axis=1, inplace=True)
                    r.results.drop('Total', errors='ignore', inplace=True)
                    r.results.drop('Total', errors='ignore', inplace=True, axis=1)

                # add interrogation to master list
                if interrogation_returned_dict:
                    all_interrogations[the_name + '-' + nm] = r
                    all_conc[the_name + '-' + nm] = r.concordance
                    dict_of_results[the_name + '-' + nm] = dict_of_results.pop(nm)
                    # make multi for conc...
                else:
                    all_interrogations[nm] = r
                    all_conc[nm] = r.concordance

            # show most recent (alphabetically last) interrogation spreadsheet
            recent_interrogation_name = dict_of_results.keys()[0]
            recent_interrogation_data = dict_of_results.values()[0]

            if queryd == {'s': 'any'}:
                conc = False
            if doing_concondancing:
                conc_to_show = recent_interrogation_data.concordance
                if conc_to_show is not None:
                    numresults = len(conc_to_show.index)
                    if numresults > truncate_conc_after.get() - 1:
                        truncate = messagebox.askyesno("Long results list", 
                                     "%d unique concordance results! Truncate to %s?" % (numresults, str(truncate_conc_after.get())))
                        if truncate:
                            conc_to_show = conc_to_show.head(truncate_conc_after.get())
                    add_conc_lines_to_window(conc_to_show, preserve_colour=False)
                else:
                    timestring('No concordance results generated.')
                global conc_saved
                conc_saved = False

            name_of_interro_spreadsheet.set(recent_interrogation_name)
            i_resultname.set('Interrogation results: %s' % str(name_of_interro_spreadsheet.get()))

            # total in a way that tkintertable likes
            if isinstance(recent_interrogation_data.totals, int):
                recent_interrogation_data.totals = Series(recent_interrogation_data.totals)
            totals_as_df = pandas.DataFrame(recent_interrogation_data.totals, dtype=object)

            # update spreadsheets
            if recent_interrogation_data.results is not None:
                update_spreadsheet(interro_results, recent_interrogation_data.results, height=340)
            else:
                update_spreadsheet(interro_results, df_to_show=None, height=340)

            update_spreadsheet(interro_totals, totals_as_df, height=10)
            
            ind = list(all_interrogations.keys()).index(name_of_interro_spreadsheet.get())
            if ind == 0:
                prev.configure(state=DISABLED)
            else:
                prev.configure(state=NORMAL)

            if ind + 1 == len(list(all_interrogations.keys())):
                nex.configure(state=DISABLED)
            else:
                nex.configure(state=NORMAL)
            refresh()

            if recent_interrogation_data.results is not None:
                subs = r.results.index
            else:
                subs = r.totals.index

            subc_listbox.delete(0, 'end')
            for e in list(subs):
                if e != 'tkintertable-order':
                    subc_listbox.insert(END, e)

            #reset name
            nametext.set('untitled')
        
            if interrogation_returned_dict:
                timestring('Interrogation finished, with multiple results.')

            interrobut.config(state=NORMAL)
            interrobut_conc.config(state=NORMAL)
            recalc_but.config(state=NORMAL)

        class MyOptionMenu(OptionMenu):
            """Simple OptionMenu for things that don't change."""
            def __init__(self, tab1, status, *options):
                self.var = StringVar(tab1)
                self.var.set(status)
                OptionMenu.__init__(self, tab1, self.var, *options)
                self.config(font=('calibri',(12)),width=20)
                self['menu'].config(font=('calibri',(10)))
            
        def corpus_callback(*args):
            """on selecting a corpus, set everything appropriately.
            also, disable some kinds of search based on the name"""
            if current_corpus.get() == '':
                return
            corpus_name = current_corpus.get()

            fp = os.path.join(corpora_fullpath.get(), corpus_name)
            corpus_fullpath.set(fp)

            # find out what kind of corpus it is
            from corpkit.process import determine_datatype
            datat, singlef = determine_datatype(fp)
            datatype.set(datat)
            singlefile.set(singlef)

            subdrs = sorted([d for d in os.listdir(corpus_fullpath.get()) \
                            if os.path.isdir(os.path.join(corpus_fullpath.get(),d))])
            
            if len(subdrs) == 0:
                charttype.set('bar')
            pick_subcorpora['menu'].delete(0, 'end')
            if len(subdrs) > 0:
                pick_subcorpora.config(state=NORMAL)
                pick_subcorpora['menu'].add_command(label='All', command=_setit(subc_pick, 'All'))
                for choice in subdrs:
                    pick_subcorpora['menu'].add_command(label=choice, command=_setit(subc_pick, choice))
            else:
                pick_subcorpora.config(state=NORMAL)
                pick_subcorpora['menu'].add_command(label='None', command=_setit(subc_pick, 'None'))
                pick_subcorpora.config(state=DISABLED)

            pick_a_datatype['menu'].delete(0, 'end')

            path_to_new_unparsed_corpus.set(fp)
            #add_corpus_button.set('Added: "%s"' % os.path.basename(fp))
            # why is it setting itself? #
            #current_corpus.set(os.path.basename(fp))
            if not corpus_name.endswith('-parsed') and not corpus_name.endswith('-tokenised'):
                parsebut.config(state=NORMAL)
                tokbut.config(state=NORMAL)
                parse_button_text.set('Parse: %s' % os.path.basename(fp))
                tokenise_button_text.set('Tokenise: %s' % corpus_name)
            else:
                parsebut.config(state=NORMAL)
                tokbut.config(state=NORMAL)
                parse_button_text.set('Parse corpus')
                tokenise_button_text.set('Tokenise corpus')
                parsebut.config(state=DISABLED)
                tokbut.config(state=DISABLED)
            if not corpus_name.endswith('-parsed'):
                pick_dep_type.config(state=DISABLED)
                #parsebut.config(state=NORMAL)
                #speakcheck_build.config(state=NORMAL)
                interrobut_conc.config(state=DISABLED)
                recalc_but.config(state=DISABLED)
                #sensplitbut.config(state=NORMAL)
            else:
                if datatype_picked.get() not in ['Trees', 'N-grams']:
                    pick_dep_type.config(state=NORMAL)
                    #q.config(state=NORMAL)
                #else:
                    #q.config(state=DISABLED)
                #sensplitbut.config(state=DISABLED)
                interrobut_conc.config(state=DISABLED)
                recalc_but.config(state=DISABLED)
                for i in ['Trees', 'Words', 'POS', 'Lemmata', \
                          'Governor lemmata', 'Governor functions', 'Governor POS', 'Dependent lemmata', 'Dependent functions', 'Dependent POS', \
                          'Functions', 'Governors', 'Dependents', 'N-grams', 'Stats', 'Index']:
                    pick_a_datatype['menu'].add_command(label = i, command=_setit(datatype_picked, i))
                #parsebut.config(state=DISABLED)
                #speakcheck_build.config(state=DISABLED)
                datatype_picked.set('Words')
            if not corpus_name.endswith('-tokenised'):
                if not corpus_name.endswith('-parsed'):
                    pick_a_datatype['menu'].add_command(label = 'Words', command=_setit(datatype_picked, 'Words'))
                    datatype_picked.set('Words')
                    
            else:
                for i in ['Words', 'N-grams']:
                    pick_a_datatype['menu'].add_command(label = i, command=_setit(datatype_picked, i))
                #tokbut.config(state=DISABLED)
                datatype_picked.set('Words')
            
            add_subcorpora_to_build_box(fp)

            note.progvar.set(0)
            #lab.set('Concordancing: %s' % corpus_name)
            
            if corpus_name in list(corpus_names_and_speakers.keys()):
                togglespeaker()
                speakcheck.config(state=NORMAL)
            else:
                speakcheck.config(state=DISABLED)
            interrobut.config(state=NORMAL)
            interrobut_conc.config(state=NORMAL)
            recalc_but.config(state=NORMAL)
            timestring('Set corpus directory: "%s"' % corpus_name)
            editf.set('Edit file: ')
            parse_only = [ck3, ck4, ck5, ck6, ck7, ck9, ck10, ck11, ck12, ck13, ck14, ck15, ck16]
            non_parsed = [ck1, ck2, ck8]

            if not corpus_name.endswith('-parsed'):
                for but in parse_only:
                    desel_and_turn_off(but)
                for but in non_parsed:
                    turnon(but)                
            else:
                for but in parse_only:
                    turnon(but)
                for but in non_parsed:
                    turnon(but)  

            if datatype_picked.get() == 'Trees':
                ck4.config(state=NORMAL)
            else:
                ck4.config(state=DISABLED)


            featfile = os.path.join(savedinterro_fullpath.get(), current_corpus.get() + '-' + 'features.p')
            shortname = current_corpus.get() + '-' + 'features'
            if os.path.isfile(featfile) and shortname not in all_interrogations.keys():
                all_interrogations[shortname] = load(featfile)

        Label(interro_opt, text='Corpus:').grid(row=0, column=0, sticky=W)
        current_corpus = StringVar()
        current_corpus.set('Corpus')
        available_corpora = OptionMenu(interro_opt, current_corpus, *tuple(('Select corpus')))
        available_corpora.config(width=21, state=DISABLED, justify=CENTER)
        current_corpus.trace("w", corpus_callback)
        available_corpora.grid(row=0, column=0, columnspan=2, padx=(0, 33))

        # todo: implement this
        subc_pick = StringVar()
        subc_pick.set('Subcorpus')
        if os.path.isdir(corpus_fullpath.get()):
            current_subcorpora = sorted([d for d in os.listdir(corpus_fullpath.get()) if os.path.isdir(os.path.join(corpus_fullpath.get(),d))])
        else:
            current_subcorpora = []
        pick_subcorpora = OptionMenu(interro_opt, subc_pick, *tuple(['All'] + current_subcorpora))
        pick_subcorpora.configure(width=12)
        pick_subcorpora.grid(row=0, column=1, sticky=E)

        # for build tab
        #Label(interro_opt, text='Corpus:').grid(row=0, column=0, sticky=W)
        #current_corpus = StringVar()
        #current_corpus.set('Select corpus')

        available_corpora_build = OptionMenu(tab0, current_corpus, *tuple(('Select corpus')))
        available_corpora_build.config(width=25, justify=CENTER, state=DISABLED)
        available_corpora_build.grid(row=4, column=0, sticky=W)

        # Secondary match
        #secondary_op = StringVar()
        #secondary_op.set('None')
        #Label(interro_opt, text='Refine:').grid(row=10, column=0, sticky=W)
        #sec_match = OptionMenu(interro_opt, secondary_op, *tuple(('None', 'Word', 'POS', 'Lemma', 'Function', 'Index')))
        #sec_match.grid(row=10, column=0, sticky=W, padx=(90, 0))
        #secondary_str = StringVar()
        #secondary_str.set('')
        #q = Entry(interro_opt, textvariable=secondary_str, width=22, state=DISABLED)
        #q.grid(row=10, column=0, columnspan=2, sticky=E)
        #all_text_widgets.append(q)

        ex_additional_criteria = {}
        ex_anyall = StringVar()
        ex_anyall.set('any')

        ex_objs = OrderedDict()
        # fill it with null data
        for i in range(20):
            tmp = StringVar()
            tmp.set('')
            ex_objs[i] = [None, None, None, tmp]

        ex_permref = []

        exclude_str = StringVar()
        exclude_str.set('')
        Label(interro_opt, text='Exclude:').grid(row=5, column=0, sticky=W, pady=(0, 10))
        exclude_op = StringVar()
        exclude_op.set('None')
        exclude = OptionMenu(interro_opt, exclude_op, *tuple(('None', 'Words', 'POS', 'Lemmata', 'Functions', 'Dependents', 'Governors', 'Index', \
                             'Governor lemmata', 'Governor functions', 'Governor POS', 'Dependent lemmata', 'Dependent functions', 'Dependent POS')))
        exclude.config(width=14)
        exclude.grid(row=5, column=0, sticky=W, padx=(60, 0), pady=(0, 10))
        qr = Entry(interro_opt, textvariable=exclude_str, width=18, state=DISABLED)
        qr.grid(row=5, column=0, columnspan=2, sticky=E, padx=(0,40), pady=(0, 10))
        all_text_widgets.append(qr)
        ex_plusbut = Button(interro_opt, text='+', \
                        command=lambda: add_criteria(ex_objs, ex_permref, ex_anyall, ex_additional_criteria, \
                                                       exclude_op, exclude_str, title = 'Exclude from interrogation'), \
                        state=DISABLED)
        ex_plusbut.grid(row=5, column=1, sticky=E, pady=(0, 10))

        #blklst = StringVar()
        #Label(interro_opt, text='Blacklist:').grid(row=12, column=0, sticky=W)
        ##blklst.set(r'^n')
        #blklst.set(r'')
        #bkbx = Entry(interro_opt, textvariable=blklst, width=22)
        #bkbx.grid(row=12, column=0, columnspan=2, sticky=E)
        #all_text_widgets.append(bkbx)

        # lemma tags
        lemtags = tuple(('Off', 'Noun', 'Verb', 'Adjective', 'Adverb'))
        lemtag = StringVar(root)
        lemtag.set('')
        Label(interro_opt, text='Result word class:').grid(row=13, column=0, columnspan=2, sticky=E, padx=(0, 120))
        lmt = OptionMenu(interro_opt, lemtag, *lemtags)
        lmt.config(state=NORMAL, width=10)
        lmt.grid(row=13, column=1, sticky=E)
        #lemtag.trace("w", d_callback)

        def togglespeaker(*args):
            """this adds names to the speaker listboxes when it's switched on
            it gets the info from settings.ini, via corpus_names_and_speakers"""
            import os
            if os.path.isdir(corpus_fullpath.get()):
                ns = corpus_names_and_speakers[os.path.basename(corpus_fullpath.get())]
            else:
                return

            # figure out which list we need to add to, and which we should del from
            lbs = []
            delfrom = []
            if int(only_sel_speakers.get()) == 1:
                lbs.append(speaker_listbox)
            else:
                delfrom.append(speaker_listbox)
            # add names
            for lb in lbs:
                lb.configure(state=NORMAL)
                lb.delete(0, END)
                lb.insert(END, 'ALL')
                for id in ns:
                    lb.insert(END, id)
            # or delete names
            for lb in delfrom:
                lb.configure(state=NORMAL)
                lb.delete(0, END)
                lb.configure(state=DISABLED)

        # speaker names
        # button
        only_sel_speakers = IntVar()
        speakcheck = Checkbutton(interro_opt, text='Speakers:', variable=only_sel_speakers, command=togglespeaker)
        speakcheck.grid(column=0, row=14, sticky=W, pady=(15, 0))
        # add data on press
        only_sel_speakers.trace("w", togglespeaker)
        # frame to hold speaker names listbox
        spk_scrl = Frame(interro_opt)
        spk_scrl.grid(row=14, column=0, rowspan = 2, columnspan=2, sticky=E, pady=10)
        # scrollbar for the listbox
        spk_sbar = Scrollbar(spk_scrl)
        spk_sbar.pack(side=RIGHT, fill=Y)
        # listbox itself
        speaker_listbox = Listbox(spk_scrl, selectmode = EXTENDED, width=32, height=4, relief = SUNKEN, bg='#F4F4F4',
                                  yscrollcommand=spk_sbar.set, exportselection = False)
        speaker_listbox.pack()
        speaker_listbox.configure(state=DISABLED)
        spk_sbar.config(command=speaker_listbox.yview)

        # dep type
        dep_types = tuple(('Basic', 'Collapsed', 'CC-processed'))
        kind_of_dep = StringVar(root)
        kind_of_dep.set('CC-processed')
        Label(interro_opt, text='Dependency type:').grid(row=16, column=0, sticky=W)
        pick_dep_type = OptionMenu(interro_opt, kind_of_dep, *dep_types)
        pick_dep_type.config(state=DISABLED)
        pick_dep_type.grid(row=16, column=1, sticky=E)
        #kind_of_dep.trace("w", d_callback)

        # query
        entrytext=StringVar()

        Label(interro_opt, text='Query:').grid(row=3, column=0, sticky='NW', pady=(5,0))
        entrytext.set(r'\b(m.n|wom.n|child(ren)?)\b')
        qa = Text(interro_opt, width=40, height=4, borderwidth=0.5, 
                  font=("Courier New", 14), undo = True, relief = SUNKEN, wrap = WORD, highlightthickness=0)
        qa.insert(END, entrytext.get())
        qa.grid(row=3, column=0, columnspan=2, sticky=E, pady=(5,0), padx=(0, 4))
        all_text_widgets.append(qa)

        additional_criteria = {}

        anyall = StringVar()
        anyall.set('all')

        objs = OrderedDict()
        # fill it with null data
        for i in range(20):
            tmp = StringVar()
            tmp.set('')
            objs[i] = [None, None, None, tmp]

        permref = []

        def add_criteria(objs, permref, anyalltoggle, output_dict,
                         optvar, enttext, title = "Additional criteria"):
            """this is a popup for adding additional search criteria.

            it's also used for excludes"""
            if title == 'Additional criteria':
                enttext.set(qa.get(1.0, END).strip('\n').strip())
            from tkinter import Toplevel
            try:
                more_criteria = permref[0]
                more_criteria.deiconify()
                return
            except:
                pass
            more_criteria = Toplevel()
            more_criteria.geometry('+500+100')
            more_criteria.title(title)

            more_criteria.wm_attributes('-topmost', 1)

            total = 0
            n_items = []
            
            def quit_q(total, *args):
                """exit popup, saving entries"""
                poss_keys = []
                for index, (option, optvar, entbox, entstring) in enumerate(list(objs.values())[:total]):
                    if index == 0:
                        enttext.set(entstring.get())
                        optvar.set(optvar.get())
                        datatype_picked.set(optvar.get())
                    if optvar is not None:
                        o = convert_name_to_query[optvar.get()]
                        q = entstring.get().strip()
                        q = remake_special_query(q, return_list = True)
                        output_dict[o] = q
                # may not work on mac ...
                if title == 'Additional criteria':
                    if len(list(objs.values())[:total]) > 0:
                        plusbut.config(bg='#F4F4F4')
                    else:
                        plusbut.config(bg='white')
                else:
                    if len(list(objs.values())[:total]) > 0:
                        ex_plusbut.config(bg='#F4F4F4')
                    else:
                        ex_plusbut.config(bg='white')
                more_criteria.withdraw()

            def remove_prev():
                """delete last added criteria line"""
                if len([k for k, v in objs.items() if v[0] is not None]) < 2:
                    pass
                else:
                    ans = 0
                    for k, (a, b, c, d) in reversed(list(objs.items())):
                        if a is not None:
                            ans = k
                            break
                    if objs[ans][0] is not None:
                        objs[ans][0].destroy()
                    optvar = objs[ans][1].get()
                    try:
                        del output_dict[convert_name_to_query[optvar]]
                    except:
                        pass
                    objs[ans][1] = StringVar()
                    if objs[ans][2] is not None:
                        objs[ans][2].destroy()
                    objs[ans][3] = StringVar()
                    objs.pop(ans, None)
                

            def clear_q():
                """clear the popup"""
                for optmenu, optvar, entbox, entstring in list(objs.values()):
                    if optmenu is not None:
                        optvar.set('Words')
                        entstring.set('')

            def new_item(total, optvar, enttext, init = False):
                """add line to popup"""
                for i in n_items:
                    i.destroy()
                for i in n_items:
                    n_items.remove(i)
                chosen = StringVar()
                poss = tuple(('None', 'Words', 'POS', 'Lemmata', \
                             'Governor lemmata', 'Governor functions', 'Governor POS', 'Dependent lemmata', \
                             'Dependent functions', 'Dependent POS', \
                             'Functions', 'Dependents', 'Governors', 'Index'))
                chosen.set('Words')
                opt = OptionMenu(more_criteria, chosen, *poss)
                opt.config(width=16)
                t = total + 1
                opt.grid(row=total, column=0, sticky=W)
                text_str = StringVar()
                text_str.set('')
                text=Entry(more_criteria, textvariable=text_str, width=40, font=("Courier New", 13))
                all_text_widgets.append(text)
                text.grid(row=total, column=1)  
                objs[total] = [opt, chosen, text, text_str]
                minuser = Button(more_criteria, text='-', command=remove_prev)
                minuser.grid(row=total + 2, column=0, sticky=W, padx=(38,0))
                plusser = Button(more_criteria, text='+', command=lambda : new_item(t, optvar, enttext))
                plusser.grid(row=total + 2, column=0, sticky=W)
                stopbut = Button(more_criteria, text='Done', command=lambda : quit_q(t))
                stopbut.grid(row=total + 2, column=1, sticky=E)
                clearbut = Button(more_criteria, text='Clear', command=clear_q)
                clearbut.grid(row=total + 2, column=1, sticky=E, padx=(0, 60))
                r1 = Radiobutton(more_criteria, text='Match any', variable=anyalltoggle, value= 'any')
                r1.grid(row=total + 2, column=0, columnspan=2, sticky=E, padx=(0,150))
                r2 = Radiobutton(more_criteria, text='Match all', variable=anyalltoggle, value= 'all')
                r2.grid(row=total + 2, column=0, columnspan=2, sticky=E, padx=(0,250))
                n_items.append(plusser)
                n_items.append(stopbut)
                n_items.append(minuser)
                n_items.append(clearbut)
                n_items.append(r1)
                n_items.append(r2)
                if init:
                    text_str.set(enttext.get())
                    chosen.set(optvar.get())
                    minuser.config(state=DISABLED)
                else:
                    minuser.config(state=NORMAL)
                return t

                if objs:
                    for optmenu, optvar, entbox, entstring in list(objs.values()):
                        optmenu.grid()
                        entbox.grid()

            # make the first button with defaults
            total = new_item(total, optvar, enttext, init = True)
            if more_criteria not in permref:
                permref.append(more_criteria)

        plusbut = Button(interro_opt, text='+', \
                        command=lambda: add_criteria(objs, permref, anyall, \
                                            additional_criteria, datatype_picked, entrytext), \
                        state=DISABLED)
        plusbut.grid(row=1, column=0, columnspan=2, padx=(0,200))

        def entry_callback(*args):
            """when entry is changed, add it to the textbox"""
            qa.config(state=NORMAL)
            qa.delete(1.0, END)
            qa.insert(END, entrytext.get())
        entrytext.trace("w", entry_callback)

        # these are example queries for each data type
        def_queries = {'Trees': r'JJ > (NP <<# /NN.?/)',
                       'Plaintext': r'\b(m.n|wom.n|child(ren)?)\b',
                       'Governors': r'\b(m.n|wom.n|child(ren)?)\b',
                       'Dependents': r'\b(m.n|wom.n|child(ren)?)\b',
                       'Words': r'\b(m.n|wom.n|child(ren)?)\b',
                       'Lemmata': r'\b(want|desire|need)\b',
                       'Governor lemmata': r'\b(want|desire|need)\b',
                       'Dependent lemmata': r'\b(want|desire|need)\b',
                       'Dependencies': r'\b(m.n|wom.n|child(ren)?)\b',
                       'Tokens': r'\b(m.n|wom.n|child(ren)?)\b',
                       'Other': r'[cat,cats,mouse,mice,cheese]',
                       'other2': r'\b(amod|nn|advm|vmod|tmod)\b',
                       'Functions': r'\b(amod|nn|advm|vmod|tmod)\b',
                       'Governor functions': r'\b(amod|nn|advm|vmod|tmod)\b',
                       'Dependent functions': r'\b(amod|nn|advm|vmod|tmod)\b',
                       'N-grams': r'any',
                       'Stats': r'any',
                       'Index': r'[012345]',
                       'POS': r'^[NJR]',
                       'Governor POS': r'^[NJR]',
                       'Dependent POS': r'^[NJR]',
                       'Functions': r'\b(amod|nn|advm|vmod|tmod)',
                       'other3': 'any'}

        # these are more specific examples for particular options
        special_examples = {'Get tokens by role': r'\b(amod|nn|advm|vmod|tmod)\b',
                                'Simple search string search': r'[cat,cats,mouse,mice,cheese]',
                                'Regular expression search': r'(m.n|wom.n|child(ren)?)',
                                'Get tokens by regex': r'(m.n|wom.n|child(ren)?)',
                                'Get tokens matching list': r'[cat,cats,mouse,mice,cheese]',
                                'Get ngrams from tokens': 'any',
                                'Get ngrams from trees': 'any'}

        def onselect(evt):
            """when an option is selected, add the example query
            for ngrams, add the special ngram options"""
            w = evt.widget
            index = int(w.curselection()[0])
            value = w.get(index)
            w.see(index)
            #datatype_chosen_option.set(value)
            #datatype_listbox.select_set(index)
            #datatype_listbox.see(index)
            if qa.get(1.0, END).strip('\n').strip() in list(def_queries.values()) + list(special_examples.values()):
                if qa.get(1.0, END).strip('\n').strip() not in list(qd.values()):
                    try:
                        entrytext.set(special_examples[value])
                    except KeyError:
                        entrytext.set(def_queries[datatype_picked.get()])

                #try:
                #    ngmsize.destroy()
                #except:
                #    pass
                #try:
                #    split_contract.destroy()
                #except:
                #    pass

        # boolean interrogation arguments need fixing, right now use 0 and 1
        #lem = IntVar()
        #lbut = Checkbutton(interro_opt, text="Lemmatise", variable=lem, onvalue = True, offvalue = False)
        #lbut.grid(column=0, row=8, sticky=W)
        #phras = IntVar()
        #mwbut = Checkbutton(interro_opt, text="Multiword results", variable=phras, onvalue = True, offvalue = False)
        #mwbut.grid(column=1, row=8, sticky=E)
        #tit_fil = IntVar()
        #tfbut = Checkbutton(interro_opt, text="Filter titles", variable=tit_fil, onvalue = True, offvalue = False)
        #tfbut.grid(row=9, column=0, sticky=W)
        case_sensitive = IntVar()
        Checkbutton(interro_opt, text="Case sensitive", variable=case_sensitive, onvalue = True, offvalue = False).grid(row=13, column=0, sticky=W)

        global ngmsize
        Label(interro_opt, text='Ngrams:').grid(row=7, column=0, sticky=W) 
        ngmsize = MyOptionMenu(interro_opt, 'Size','2','3','4','5','6','7','8')
        ngmsize.configure(width=12)
        ngmsize.grid(row=7, column=0, sticky=W, padx=(60, 0))
        ngmsize.config(state=DISABLED)
        global split_contract
        split_contract = IntVar(root)
        split_contract.set(False)
        split_contract_but = Checkbutton(interro_opt, text='Split contractions', variable=split_contract, onvalue = True, offvalue = False)
        split_contract_but.grid(row=7, column=1, sticky=E) 

        Label(interro_opt, text='Spelling:').grid(row=6, column=1, sticky=E, padx=(0, 75))
        spl = MyOptionMenu(interro_opt, 'Off','UK','US')
        spl.configure(width=7)
        spl.grid(row=6, column=1, sticky=E, padx=(2, 0))

        def desel_and_turn_off(but):
            pass
            but.config(state=NORMAL)
            but.deselect()
            but.config(state=DISABLED)

        def turnon(but):
            but.config(state=NORMAL)

        def ngram_callback(*args):
            ngmshows = [return_ngm, return_ngm_lemma, return_ngm_func, return_ngm_pos]
            ngmbuts = [ck17, ck18, ck19, ck20]
            non_ngram = [ck1, ck2, ck3, ck4, ck5, ck6, ck7, ck8, ck9, ck10, \
                ck11, ck12, ck13, ck14, ck15, ck16]
            if any(ngmshow.get() for ngmshow in ngmshows):
                for but in ngmbuts:
                    turnon(but)
                for but in non_ngram:
                    desel_and_turn_off(but)
                ngmsize.config(state=NORMAL)
                split_contract_but.config(state=NORMAL)
            if all(not ngmshow.get() for ngmshow in ngmshows):
                if return_count.get() != 'c':
                    for but in non_ngram:
                        turnon(but)
                    ngmsize.config(state=DISABLED)
                    split_contract_but.config(state=DISABLED)

        def callback(*args):
            """if the drop down list for data type changes, fill options"""
            #datatype_listbox.delete(0, 'end')
            chosen = datatype_picked.get()
            #lst = option_dict[chosen]
            #for e in lst:
            #    datatype_listbox.insert(END, e)

            if chosen == 'Trees':
                for but in [ck5, ck6, ck7, ck9, ck10, ck11, ck12, ck13, ck14, ck15, ck16, \
                            ck17, ck18, ck19, ck20]:
                    desel_and_turn_off(but)

                for but in [ck1, ck2, ck4, ck4, ck8]:
                    turnon(but)
                ck1.select()

                #q.config(state=DISABLED)
                #qr.config(state=DISABLED)
                #exclude.config(state=DISABLED)
                #sec_match.config(state=DISABLED)
                plusbut.config(state=DISABLED) 
                ex_plusbut.config(state=DISABLED) 

            elif chosen in ['Words', 'Functions', 'Governors', 'Dependents', \
                            'Governor lemmata', 'Governor functions', 'Governor POS', \
                            'Dependent lemmata', 'Dependent functions', 'Dependent POS', \
                            'Index', 'Distance', 'POS', 'Lemmata']:
                if current_corpus.get().endswith('-parsed'):     
                    for but in [ck1, ck2, ck3, ck5, ck6, ck7, ck8, ck9, ck10, \
                                ck11, ck12, ck13, ck14, ck15, ck16, \
                                ck17, ck18, ck19, ck20, \
                                plusbut, ex_plusbut, exclude, qr]:
                        turnon(but)
                    desel_and_turn_off(ck4)

            if chosen == 'Stats':
                nametext.set('features')
                nametexter.config(state=DISABLED)
            else:
                nametexter.config(state=NORMAL)
                nametext.set('untitled')

            if chosen == 'Stats' or chosen == 'N-grams':
                for but in [ck2, ck3, ck4, ck5, ck6, ck7, ck8, ck9, ck10, \
                                ck11, ck12, ck13, ck14, ck15, ck16]:
                    desel_and_turn_off(but)
                turnon(ck1)
                ck1.select()
                ngmshows = [return_ngm, return_ngm_lemma, return_ngm_func, return_ngm_pos]
                if chosen == 'N-grams' or any(ngmshow.get() for ngmshow in ngmshows):
                    #lbut.config(state=DISABLED)
                    ngmsize.config(state=NORMAL)
                    split_contract_but.config(state=NORMAL)
                else:
                    ngmsize.config(state=DISABLED)
                    split_contract_but.config(state=DISABLED)
            
            #if qa.get(1.0, END).strip('\n').strip() in def_queries.values() + special_examples.values():
            clean_query = qa.get(1.0, END).strip('\n').strip()
            if clean_query not in list(qd.values()) and clean_query in list(def_queries.values()):
                try:
                    entrytext.set(def_queries[chosen])
                except:
                    pass
            if not clean_query:
                try:
                    entrytext.set(def_queries[chosen])
                except:
                    pass

        datatype_picked = StringVar(root)
        Label(interro_opt, text='Search: ').grid(row=1, column=0, sticky=W, pady=10)
        pick_a_datatype = OptionMenu(interro_opt, datatype_picked, *tuple(('Trees', 'Words', 'POS', \
                            'Lemmata', 'Functions', 'Dependents', 'Governors', 'N-grams', 'Index', \
                             'Stats', 'Governor lemmata', 'Governor functions', 'Governor POS', 'Dependent lemmata', 'Dependent functions', 'Dependent POS')))
        pick_a_datatype.configure(width=30, justify=CENTER)
        datatype_picked.set('Words')
        pick_a_datatype.grid(row=1, column=0, columnspan=2, sticky=W, padx=(136,0))
        datatype_picked.trace("w", callback)
        
        # trees, words, functions, governors, dependents, pos, lemma, count
        interro_return_frm = Frame(interro_opt)

        Label(interro_return_frm, text='   Return', font=("Courier New", 13, "bold")).grid(row=0, column=0, sticky=E)
        interro_return_frm.grid(row=4, column=0, columnspan=2, sticky=W, pady=10, padx=(10,0))

        Label(interro_return_frm, text='    Token', font=("Courier New", 13)).grid(row=0, column=1, sticky=E)
        Label(interro_return_frm, text='    Lemma', font=("Courier New", 13)).grid(row=0, column=2, sticky=E)
        Label(interro_return_frm, text='  POS tag', font=("Courier New", 13)).grid(row=0, column=3, sticky=E)
        Label(interro_return_frm, text= 'Function', font=("Courier New", 13)).grid(row=0, column=4, sticky=E)
        Label(interro_return_frm, text='    Match', font=("Courier New", 13)).grid(row=1, column=0, sticky=E)
        Label(interro_return_frm, text=' Governor', font=("Courier New", 13)).grid(row=2, column=0, sticky=E)
        Label(interro_return_frm, text='Dependent', font=("Courier New", 13)).grid(row=3, column=0, sticky=E)
        Label(interro_return_frm, text=   'N-gram', font=("Courier New", 13)).grid(row=4, column=0, sticky=E)
        Label(interro_return_frm, text='    Other', font=("Courier New", 13)).grid(row=5, column=0, sticky=E)
        Label(interro_return_frm, text='    Count', font=("Courier New", 13)).grid(row=5, column=1, sticky=E)
        Label(interro_return_frm, text='    Index', font=("Courier New", 13)).grid(row=5, column=2, sticky=E)
        Label(interro_return_frm, text=' Distance', font=("Courier New", 13)).grid(row=5, column=3, sticky=E)
        Label(interro_return_frm, text='     Tree', font=("Courier New", 13)).grid(row=5, column=4, sticky=E)
        return_token = StringVar()
        return_token.set('')
        ck1 = Checkbutton(interro_return_frm, variable=return_token, onvalue = 'w', offvalue = '')
        ck1.select()
        ck1.grid(row=1, column=1, sticky=E)

        def return_token_callback(*args):
            if datatype_picked.get() == 'Trees':
                if return_token.get():
                    for but in [ck3, ck4, ck8]:
                        but.config(state=NORMAL)
                        but.deselect()
        return_token.trace("w", return_token_callback)

        return_lemma = StringVar()
        return_lemma.set('')
        ck2 = Checkbutton(interro_return_frm, anchor=E, variable=return_lemma, onvalue = 'l', offvalue = '')
        ck2.grid(row=1, column=2, sticky=E)

        def return_lemma_callback(*args):
            if datatype_picked.get() == 'Trees':
                if return_lemma.get():
                    for but in [ck3, ck4, ck8]:
                        but.config(state=NORMAL)
                        but.deselect()
                    lmt.configure(state=NORMAL)
                else:
                    lmt.configure(state=DISABLED)
        return_lemma.trace("w", return_lemma_callback)

        return_pos = StringVar()
        return_pos.set('')
        ck3 = Checkbutton(interro_return_frm, variable=return_pos, onvalue = 'p', offvalue = '')
        ck3.grid(row=1, column=3, sticky=E)

        def return_pos_callback(*args):
            if datatype_picked.get() == 'Trees':
                if return_pos.get():
                    for but in [ck1, ck2, ck4, ck8]:
                        but.config(state=NORMAL)
                        but.deselect()
        return_pos.trace("w", return_pos_callback)

        return_function = StringVar()
        return_function.set('')
        ck7 = Checkbutton(interro_return_frm, variable=return_function, onvalue = 'f', offvalue = '')
        ck7.grid(row=1, column=4, sticky=E)

        return_tree = StringVar()
        return_tree.set('')
        ck4 = Checkbutton(interro_return_frm, anchor=E, variable=return_tree, onvalue = 't', offvalue = '')
        ck4.grid(row=6, column=4, sticky=E)

        def return_tree_callback(*args):
            if datatype_picked.get() == 'Trees':
                if return_tree.get():
                    for but in [ck1, ck2, ck3, ck8]:
                        but.config(state=NORMAL)
                        but.deselect()
        return_tree.trace("w", return_tree_callback)

        return_tree.trace("w", return_tree_callback)

        return_index = StringVar()
        return_index.set('')
        ck5 = Checkbutton(interro_return_frm, anchor=E, variable=return_index, onvalue = 'i', offvalue = '')
        ck5.grid(row=6, column=2, sticky=E)

        return_distance = StringVar()
        return_distance.set('')
        ck6 = Checkbutton(interro_return_frm, anchor=E, variable=return_distance, onvalue = 'r', offvalue = '')
        ck6.grid(row=6, column=3, sticky=E)

        return_count = StringVar()
        return_count.set('')
        ck8 = Checkbutton(interro_return_frm, variable=return_count, onvalue = 'c', offvalue = '')
        ck8.grid(row=6, column=1, sticky=E)

        def countmode(*args):
            ngmshows = [return_ngm, return_ngm_lemma, return_ngm_func, return_ngm_pos]
            ngmbuts = [ck17, ck18, ck19, ck20]
            if any(ngmshow.get() for ngmshow in ngmshows):
                return
            if datatype_picked.get() != 'Trees':
                buttons = [ck1, ck2, ck3, ck4, ck5, ck6, ck7, ck9, 
                           ck10, ck11, ck12, ck13, ck14, ck15, ck16,
                           ck17, ck18, ck19, ck20]
                if return_count.get() == 'c':
                    for b in buttons:
                        desel_and_turn_off(b)
                    ck8.config(state=NORMAL)
                else:
                    for b in buttons:
                        b.config(state=NORMAL)
                    callback()
            else:
                if return_count.get():
                    for but in [ck1, ck2, ck3, ck4]:
                        but.config(state=NORMAL)
                        but.deselect()

        return_count.trace("w", countmode)

        return_gov = StringVar()
        return_gov.set('')
        ck9 = Checkbutton(interro_return_frm, variable=return_gov, 
                          onvalue = 'g', offvalue = '')
        ck9.grid(row=2, column=1, sticky=E)

        return_gov_lemma = StringVar()
        return_gov_lemma.set('')
        ck10 = Checkbutton(interro_return_frm, variable=return_gov_lemma, 
                          onvalue = 'gl', offvalue = '')
        ck10.grid(row=2, column=2, sticky=E)

        return_gov_pos = StringVar()
        return_gov_pos.set('')
        ck11 = Checkbutton(interro_return_frm, variable=return_gov_pos, 
                          onvalue = 'gp', offvalue = '')
        ck11.grid(row=2, column=3, sticky=E)

        return_gov_func = StringVar()
        return_gov_func.set('')
        ck12 = Checkbutton(interro_return_frm, variable=return_gov_func, 
                          onvalue = 'gf', offvalue = '')
        ck12.grid(row=2, column=4, sticky=E)

        return_dep = StringVar()
        return_dep.set('')
        ck13 = Checkbutton(interro_return_frm, variable=return_dep, 
                          onvalue = 'd', offvalue = '')
        ck13.grid(row=3, column=1, sticky=E)

        return_dep_lemma = StringVar()
        return_dep_lemma.set('')
        ck14 = Checkbutton(interro_return_frm, variable=return_dep_lemma, 
                          onvalue = 'dl', offvalue = '')
        ck14.grid(row=3, column=2, sticky=E)

        return_dep_pos = StringVar()
        return_dep_pos.set('')
        ck15 = Checkbutton(interro_return_frm, variable=return_dep_pos, 
                          onvalue = 'dp', offvalue = '')
        ck15.grid(row=3, column=3, sticky=E)

        return_dep_func = StringVar()
        return_dep_func.set('')
        ck16 = Checkbutton(interro_return_frm, variable=return_dep_func, 
                          onvalue = 'df', offvalue = '')
        ck16.grid(row=3, column=4, sticky=E)

        return_ngm = StringVar()
        return_ngm.set('')
        ck17 = Checkbutton(interro_return_frm, variable=return_ngm, 
                          onvalue = 'n', offvalue = '')
        ck17.grid(row=4, column=1, sticky=E)

        return_ngm_lemma = StringVar()
        return_ngm_lemma.set('')
        ck18 = Checkbutton(interro_return_frm, variable=return_ngm_lemma, 
                          onvalue = 'nl', offvalue = '')
        ck18.grid(row=4, column=2, sticky=E)

        return_ngm_pos = StringVar()
        return_ngm_pos.set('')
        ck19 = Checkbutton(interro_return_frm, variable=return_ngm_pos, 
                          onvalue = 'np', offvalue = '')
        ck19.grid(row=4, column=3, sticky=E)

        return_ngm_func = StringVar()
        return_ngm_func.set('')
        ck20 = Checkbutton(interro_return_frm, variable=return_ngm_func, 
                          onvalue = 'npl', offvalue = '', state=DISABLED)
        ck20.grid(row=4, column=4, sticky=E)

        return_ngm.trace("w", ngram_callback)
        return_ngm_lemma.trace("w", ngram_callback)
        return_ngm_pos.trace("w", ngram_callback)
        return_ngm_func.trace("w", ngram_callback)

        def q_callback(*args):

            if special_queries.get() == 'Off':
                #q.configure(state=NORMAL)
                qa.configure(state=NORMAL)
                qr.configure(state=NORMAL)
            else:
                entrytext.set(qd[special_queries.get()])
                #q.configure(state=DISABLED)
                qa.configure(state=DISABLED)
                qr.configure(state=DISABLED)
                if special_queries.get() == 'Stats':
                    datatype_picked.set('Stats')
                else:
                    datatype_picked.set('Trees')
                #almost everything should be disabled ..

        queries = tuple(('Off', 'Any', 'Participants', 'Processes', 'Subjects', 'Stats'))
        special_queries = StringVar(root)
        special_queries.set('Off')
        Label(interro_opt, text='Preset:').grid(row=6, column=0, sticky=W)
        pick_a_query = OptionMenu(interro_opt, special_queries, *queries)
        pick_a_query.config(width=11, state=DISABLED)
        pick_a_query.grid(row=6, column=0, padx=(60, 0), columnspan=2, sticky=W)
        special_queries.trace("w", q_callback)

        # Interrogation name
        nametext=StringVar()
        nametext.set('untitled')
        Label(interro_opt, text='Interrogation name:').grid(row=17, column=0, sticky=W)
        nametexter = Entry(interro_opt, textvariable=nametext, width=15)
        nametexter.grid(row=17, column=1, sticky=E)
        all_text_widgets.append(nametexter)

        def show_help(kind):
            kindict = {'h': 'http://interrogator.github.io/corpkit/doc_help.html',
                       'q': 'http://interrogator.github.io/corpkit/doc_interrogate.html#trees',
                       't': 'http://interrogator.github.io/corpkit/doc_troubleshooting.html'}
            import webbrowser
            webbrowser.open_new(kindict[kind])

        # query help, interrogate button
        #Button(interro_opt, text='Query help', command=query_help).grid(row=14, column=0, sticky=W)
        interrobut = Button(interro_opt, text='Interrogate')
        interrobut.config(command=lambda: runner(interrobut, do_interrogation, conc = True), state=DISABLED)
        interrobut.grid(row=18, column=1, sticky=E)

        # name to show above spreadsheet 0
        i_resultname = StringVar()

        def change_interro_spread(*args):
            if name_of_interro_spreadsheet.get():
                savdict.config(state=NORMAL)
                updbut.config(state=NORMAL)
            else:
                savdict.config(state=DISABLED)
                updbut.config(state=DISABLED)

        name_of_interro_spreadsheet = StringVar()
        name_of_interro_spreadsheet.set('')
        name_of_interro_spreadsheet.trace("w", change_interro_spread)
        i_resultname.set('Interrogation results: %s' % str(name_of_interro_spreadsheet.get()))  
        
        # make spreadsheet frames for interrogate pane
        interro_results = Frame(tab1, height=45, width=25, borderwidth=2)
        interro_results.grid(column=2, row=0, rowspan=5, padx=20, pady=(20,0), sticky='N')

        interro_totals = Frame(tab1, height=1, width=20, borderwidth=2)
        interro_totals.grid(column=2, row=0, rowspan=1, padx=20, pady=(530,0), sticky='N')

        llab = Label(tab1, textvariable=i_resultname, 
              font=("Helvetica", 13, "bold"))
        llab.grid(row=0, 
               column=2, sticky='NW', padx=20, pady=0)
        llab.lift()

        # show nothing in them yet
        update_spreadsheet(interro_results, df_to_show=None, height=450, width=760)
        update_spreadsheet(interro_totals, df_to_show=None, height=10, width=760)

        #global prev
        prev = Button(tab1, text='Previous', command=show_prev)
        prev.grid(row=0, column=2, sticky=W, padx=(120, 0), pady=(607,0))
        #global nex
        nex = Button(tab1, text='Next', command=show_next)
        nex.grid(row=0, column=2, sticky=W, padx=(220, 0), pady=(607,0))
        if len(list(all_interrogations.keys())) < 2:
            nex.configure(state=DISABLED)
            prev.configure(state=DISABLED)

        savdict = Button(tab1, text='Save as dictionary', command=save_as_dictionary)
        savdict.config(state=DISABLED)
        savdict.grid(row=0, column=2, sticky=W, padx=(500,0), pady=(607,0))

        updbut = Button(tab1, text='Update interrogation', command=lambda: update_all_interrogations(pane = 'interrogate'))
        updbut.grid(row=0, column=2, sticky=W, padx=(650,0), pady=(607,0))
        updbut.config(state=DISABLED)

        ##############    ##############     ##############     ##############     ############## 
        # EDITOR TAB #    # EDITOR TAB #     # EDITOR TAB #     # EDITOR TAB #     # EDITOR TAB # 
        ##############    ##############     ##############     ##############     ############## 


        editor_buttons = Frame(tab2)
        editor_buttons.grid(row=0, column=0, sticky='NW')

        def do_editing():
            """what happens when you press edit"""
            import os
            edbut.config(state=DISABLED)
            import pandas
            from corpkit.editor import editor
            
            # translate operation into interrogator input
            operation_text=opp.get()
            if operation_text == 'None' or operation_text == 'Select an operation':
                operation_text=None
            else:
                operation_text=opp.get()[0]
            if opp.get() == u"\u00F7":
                operation_text='/'
            if opp.get() == u"\u00D7":
                operation_text='*'
            if opp.get() == '%-diff':
                operation_text='d'
            if opp.get() == 'rel. dist.':
                operation_text='a'

            using_dict = False
            # translate dataframe2 into interrogator input
            data2 = data2_pick.get()
            if data2 == 'None' or data2 == '' or data2 == 'Self':
                data2 = False
            # check if it's a dict
            elif data2_pick.get() not in list(all_interrogations.keys()):
                dpath = os.path.join(project_fullpath.get(), 'dictionaries')
                dfile = os.path.join(dpath, data2_pick.get() + '.p')
                import pickle
                data2 = pickle.load(open(dfile, 'rb'))
                #if type(data2) == list:
                #    if len(data2) == 1:
                #        data2 = data2[0]
                if type(data2) != pandas.core.series.Series:
                    data2 = pandas.Series(data2)
                using_dict = True

            if data2 is not False:
                if not using_dict:
                    if df2branch.get() == 'results':
                        try:
                            data2 = all_interrogations[data2].results
                        except AttributeError:
                            timestring('Denominator has no results branch.')
                            
                            return
                    elif df2branch.get() == 'totals':
                        try:
                            data2 = all_interrogations[data2].totals
                        except AttributeError:
                            timestring('Denominator has no totals branch.')
                            
                            return
                    if transpose.get():
                        data2 = data2.T

            the_data = all_interrogations[name_of_o_ed_spread.get()]
            if df1branch.get() == 'results':
                try:
                    data1 = the_data.results
                except AttributeError:
                    timestring('Interrogation has no results branch.')
                    
                    return
            elif df1branch.get() == 'totals':
                data1 = the_data.totals

            if (spl_editor.var).get() == 'Off' or (spl_editor.var).get() == 'Convert spelling':
                spel = False
            else:
                spel = (spl_editor.var).get()

            # editor kwargs
            editor_args = {'operation': operation_text,
                           'dataframe2': data2,
                           'spelling': spel,
                           'sort_by': sort_trans[sort_val.get()],
                           'df1_always_df': True,
                           'root': root,
                           'note': note,
                           'packdir': rd,
                           'p': p_val.get()}

            if do_sub.get() == 'Merge':
                editor_args['merge_subcorpora'] = subc_sel_vals
            elif do_sub.get() == 'Keep':
                editor_args['just_subcorpora'] = subc_sel_vals
            elif do_sub.get() == 'Span':
                editor_args['span_subcorpora'] = subc_sel_vals
            elif do_sub.get() == 'Skip':
                editor_args['skip_subcorpora'] = subc_sel_vals

            if toreplace_string.get() != '':
                if replacewith_string.get() == '':
                    replacetup = toreplace_string.get()
                else:
                    replacetup = (toreplace_string.get(), replacewith_string.get())
                editor_args['replace_names'] = replacetup

            # special query: add to this list!
            #if special_queries.get() != 'Off':
                #query = spec_quer_translate[special_queries.get()]
            
            entry_do_with = entry_regex.get()
            # allow list queries
            if entry_do_with.startswith('[') and entry_do_with.endswith(']') and ',' in entry_do_with:
                entry_do_with = entry_do_with.lower().lstrip('[').rstrip(']').replace("'", '').replace('"', '').replace(' ', '').split(',')
            else:
                # convert special stuff
                re.compile(entry_do_with)
                entry_do_with = remake_special_query(entry_do_with, return_list = True)
                if entry_do_with is False:
                    return

            if do_with_entries.get() == 'Merge':
                editor_args['merge_entries'] = entry_do_with
                nn = newname_var.get()
                if nn == '':
                    editor_args['newname'] = False
                elif is_number(nn):
                    editor_args['newname'] = int(nn)
                else:
                    editor_args['newname'] = nn
            elif do_with_entries.get() == 'Keep':
                editor_args['just_entries'] = entry_do_with
            elif do_with_entries.get() == 'Skip':
                editor_args['skip_entries'] = entry_do_with
            
            if new_subc_name.get() != '':
                editor_args['new_subcorpus_name'] = new_subc_name.get()
            if newname_var.get() != '':
                editor_args['new_subcorpus_name'] = newname_var.get()
                
            if keep_stats_setting.get() == 1:
                editor_args['keep_stats'] = True

            if rem_abv_p_set.get() == 1:
                editor_args['remove_above_p'] = True

            if just_tot_setting.get() == 1:
                editor_args['just_totals'] = True

            if transpose.get():
                data1 = data1.T

            if keeptopnum.get() != 'all':
                try:
                    numtokeep = int(keeptopnum.get())
                except ValueError:
                    timestring('Keep top n results value must be number.')
                    
                    return
                editor_args['keep_top'] = numtokeep
            
            # do editing
            r = the_data.edit(branch = df1branch.get(), **editor_args)
            
            if type(r) == str:
                if r == 'linregress':
                    return
            if not r:
                timestring('Editing caused an error.')
                return

            if len(list(r.results.columns)) == 0:
                timestring('Editing removed all results.')
                return

            # drop over 1000?
            # results should now always be dataframes, so this if is redundant
            if type(r.results) == pandas.core.frame.DataFrame:
                large = [n for i, n in enumerate(list(r.results.columns)) if i > 9999]
                r.results.drop(large, axis = 1, inplace = True)

            timestring('Result editing completed successfully.')
            
            # name the edit
            the_name = namer(edit_nametext.get(), type_of_data = 'edited')

            # add edit to master dict
            all_interrogations[the_name] = r

            # update edited results speadsheet name
            name_of_n_ed_spread.set(list(all_interrogations.keys())[-1])
            editoname.set('Edited results: %s' % str(name_of_n_ed_spread.get()))
            
            # add current subcorpora to editor menu
            for subcl in [subc_listbox]:
                #subcl.configure(state=NORMAL)
                subcl.delete(0, 'end')
                for e in list(r.results.index):
                    if e != 'tkintertable-order':
                        subcl.insert(END, e)
                #subcl.configure(state=DISABLED)

            # update edited spreadsheets
            most_recent = all_interrogations[list(all_interrogations.keys())[-1]]
            if most_recent.results is not None:
                update_spreadsheet(n_editor_results, most_recent.results, height=140)
            update_spreadsheet(n_editor_totals, pandas.DataFrame(most_recent.totals, dtype = object), height=10)
                        
            # finish up
            refresh()
            # reset some buttons that the user probably wants reset
            opp.set('None')
            data2_pick.set('Self')
            # restore button
            

        def df2_callback(*args):
            try:
                thisdata = all_interrogations[data2_pick.get()]
            except KeyError:
                return

            if thisdata.results is not None:
                df2box.config(state=NORMAL)
            else:
                df2box.config(state=NORMAL)
                df2branch.set('totals')
                df2box.config(state=DISABLED)

        def df_callback(*args):
            """show names and spreadsheets for what is selected as result to edit
               also, hide the edited results section"""
            if selected_to_edit.get() != 'None':
                edbut.config(state=NORMAL)
                name_of_o_ed_spread.set(selected_to_edit.get())
                thisdata = all_interrogations[selected_to_edit.get()]
                resultname.set('Results to edit: %s' % str(name_of_o_ed_spread.get()))
                if thisdata.results is not None:
                    update_spreadsheet(o_editor_results, thisdata.results, height=140)
                    df1box.config(state=NORMAL)
                else:
                    df1box.config(state=NORMAL)
                    df1branch.set('totals')
                    df1box.config(state=DISABLED)
                    update_spreadsheet(o_editor_results, df_to_show=None, height=140)
                if thisdata.totals is not None:
                    update_spreadsheet(o_editor_totals, thisdata.totals, height=10)
                    #df1box.config(state=NORMAL)
                #else:
                    #update_spreadsheet(o_editor_totals, df_to_show=None, height=10)
                    #df1box.config(state=NORMAL)
                    #df1branch.set('results')
                    #df1box.config(state=DISABLED)
            else:
                edbut.config(state=DISABLED)
            name_of_n_ed_spread.set('')
            editoname.set('Edited results: %s' % str(name_of_n_ed_spread.get()))
            update_spreadsheet(n_editor_results, df_to_show=None, height=140)
            update_spreadsheet(n_editor_totals, df_to_show=None, height=10)
            for subcl in [subc_listbox]:
                subcl.configure(state=NORMAL)
                subcl.delete(0, 'end')
                if name_of_o_ed_spread.get() != '':
                    if thisdata.results is not None:
                        cols = list(thisdata.results.index)
                    else:
                        cols = list(thisdata.totals.index)
                    for e in cols:
                        if e != 'tkintertable-order':
                            subcl.insert(END, e) 
            do_sub.set('Off')
            do_with_entries.set('Off')
      
        # result to edit
        tup = tuple([i for i in list(all_interrogations.keys())])    
        selected_to_edit = StringVar(root)
        selected_to_edit.set('None')
        x = Label(editor_buttons, text='To edit', font=("Helvetica", 13, "bold"))
        x.grid(row=0, column=0, sticky=W)
        dataframe1s = OptionMenu(editor_buttons, selected_to_edit, *tup)
        dataframe1s.config(width=25)
        dataframe1s.grid(row=1, column=0, columnspan=2, sticky=W)
        selected_to_edit.trace("w", df_callback)

        # DF1 branch selection
        df1branch = StringVar()
        df1branch.set('results')
        df1box = OptionMenu(editor_buttons, df1branch, 'results', 'totals')
        df1box.config(width=11, state=DISABLED)
        df1box.grid(row=1, column=1, sticky=E)

        def op_callback(*args):
            if opp.get() != 'None':
                dataframe2s.config(state=NORMAL)
                df2box.config(state=NORMAL)
                if opp.get() == 'keywords' or opp.get() == '%-diff':
                    df2branch.set('results')
            elif opp.get() == 'None':
                dataframe2s.config(state=DISABLED)
                df2box.config(state=DISABLED)

        # operation for editor
        opp = StringVar(root)
        opp.set('None')
        operations = ('None', '%', u"\u00D7", u"\u00F7", '-', '+', 'combine', 'keywords', '%-diff', 'rel. dist.')
        Label(editor_buttons, text='Operation and denominator', font=("Helvetica", 13, "bold")).grid(row=2, column=0, sticky=W, pady=(15,0))
        ops = OptionMenu(editor_buttons, opp, *operations)
        ops.grid(row=3, column=0, sticky=W)
        opp.trace("w", op_callback)

        # DF2 option for editor
        tups = tuple(['Self'] + [i for i in list(all_interrogations.keys())])
        data2_pick = StringVar(root)
        data2_pick.set('Self')
        #Label(tab2, text='Denominator:').grid(row=3, column=0, sticky=W)
        dataframe2s = OptionMenu(editor_buttons, data2_pick, *tups)
        dataframe2s.config(state=DISABLED, width=16)
        dataframe2s.grid(row=3, column=0, columnspan=2, sticky='NW', padx=(110,0))
        data2_pick.trace("w", df2_callback)

        # DF2 branch selection
        df2branch = StringVar(root)
        df2branch.set('totals')
        df2box = OptionMenu(editor_buttons, df2branch, 'results', 'totals')
        df2box.config(state=DISABLED, width=11)
        df2box.grid(row=3, column=1, sticky=E)

        # sort by
        Label(editor_buttons, text='Sort results by', font=("Helvetica", 13, "bold")).grid(row=4, column=0, sticky=W, pady=(15,0))
        sort_val = StringVar(root)
        sort_val.set('None')
        sorts = OptionMenu(editor_buttons, sort_val, 'None', 'Total', 'Inverse total', 'Name','Increase', 'Decrease', 'Static', 'Turbulent', 'P value')
        sorts.config(width=11)
        sorts.grid(row=4, column=1, sticky=E, pady=(15,0))

        # spelling again
        Label(editor_buttons, text='Spelling:').grid(row=5, column=0, sticky=W, pady=(15,0))
        spl_editor = MyOptionMenu(editor_buttons, 'Off','UK','US')
        spl_editor.grid(row=5, column=1, sticky=E, pady=(15,0))
        spl_editor.configure(width=10)

        # keep_top
        Label(editor_buttons, text='Keep top results:').grid(row=6, column=0, sticky=W)
        keeptopnum = StringVar()
        keeptopnum.set('all')
        keeptopbox = Entry(editor_buttons, textvariable=keeptopnum, width=5)
        keeptopbox.grid(column=1, row=6, sticky=E)
        all_text_widgets.append(keeptopbox)


        # currently broken: just totals button
        just_tot_setting = IntVar()
        just_tot_but = Checkbutton(editor_buttons, text="Just totals", variable=just_tot_setting, state=DISABLED)
        #just_tot_but.select()
        just_tot_but.grid(column=0, row=7, sticky=W)

        keep_stats_setting = IntVar()
        keep_stat_but = Checkbutton(editor_buttons, text="Keep stats", variable=keep_stats_setting)
        #keep_stat_but.select()
        keep_stat_but.grid(column=1, row=7, sticky=E)

        rem_abv_p_set = IntVar()
        rem_abv_p_but = Checkbutton(editor_buttons, text="Remove above p", variable=rem_abv_p_set)
        #rem_abv_p_but.select()
        rem_abv_p_but.grid(column=0, row=8, sticky=W)

        # transpose
        transpose = IntVar()
        trans_but = Checkbutton(editor_buttons, text="Transpose", variable=transpose, onvalue = True, offvalue = False)
        trans_but.grid(column=1, row=8, sticky=E)

        # entries + entry field for regex, off, skip, keep, merge
        Label(editor_buttons, text='Edit entries', font=("Helvetica", 13, "bold")).grid(row=9, column=0, sticky=W, pady=(15, 0))
        
        # edit entries regex box
        entry_regex = StringVar()
        entry_regex.set(r'.*ing$')
        edit_box = Entry(editor_buttons, textvariable=entry_regex, width=23, state=DISABLED, font=("Courier New", 13))
        edit_box.grid(row=10, column=1, sticky=E)
        all_text_widgets.append(edit_box)

        # merge entries newname
        Label(editor_buttons, text='Merge name:').grid(row=11, column=0, sticky=W)
        newname_var = StringVar()
        newname_var.set('')
        mergen = Entry(editor_buttons, textvariable=newname_var, width=23, state=DISABLED, font=("Courier New", 13))
        mergen.grid(row=11, column=1, sticky=E)
        all_text_widgets.append(mergen)

        Label(editor_buttons, text='Replace in entry names:').grid(row=12, column=0, sticky=W)
        Label(editor_buttons, text='Replace with:').grid(row=12, column=1, sticky=W)
        toreplace_string = StringVar()
        toreplace_string.set('')
        replacewith_string = StringVar()
        replacewith_string.set('')
        toreplace = Entry(editor_buttons, textvariable=toreplace_string, font=("Courier New", 13))
        toreplace.grid(row=13, column=0, sticky=W)
        all_text_widgets.append(toreplace)
        replacewith = Entry(editor_buttons, textvariable=replacewith_string, font=("Courier New", 13), width=23)
        replacewith.grid(row=13, column=1, sticky=E)
        all_text_widgets.append(replacewith)    
        
        def do_w_callback(*args):
            """if not merging entries, diable input fields"""
            if do_with_entries.get() != 'Off':
                edit_box.configure(state=NORMAL)
            else:
                edit_box.configure(state=DISABLED)
            if do_with_entries.get() == 'Merge':
                mergen.configure(state=NORMAL)
            else:
                mergen.configure(state=DISABLED)

        # options for editing entries
        do_with_entries = StringVar(root)
        do_with_entries.set('Off')
        edit_ent_op = ('Off', 'Skip', 'Keep', 'Merge')
        ed_op = OptionMenu(editor_buttons, do_with_entries, *edit_ent_op)
        ed_op.grid(row=10, column=0, sticky=W)
        do_with_entries.trace("w", do_w_callback)

        def onselect_subc(evt):
            """get selected subcorpora: this probably doesn't need to be
               a callback, as they are only needed during do_edit"""
            for i in subc_sel_vals:
                subc_sel_vals.pop()
            wx = evt.widget
            indices = wx.curselection()
            for index in indices:
                value = wx.get(index)
                if value not in subc_sel_vals:
                    subc_sel_vals.append(value)

        def do_s_callback(*args):
            """hide subcorpora edit options if off"""
            if do_sub.get() != 'Off':
                pass
                #subc_listbox.configure(state=NORMAL)
            else:
                pass
                #subc_listbox.configure(state=DISABLED)
            if do_sub.get() == 'Merge':
                merge.configure(state=NORMAL)
            else:
                merge.configure(state=DISABLED)

        # subcorpora + optionmenu off, skip, keep
        Label(editor_buttons, text='Edit subcorpora', font=("Helvetica", 13, "bold")).grid(row=14, column=0, sticky=W, pady=(15,0))
        
        edit_sub_f = Frame(editor_buttons)
        edit_sub_f.grid(row=14, column=1, rowspan = 5, sticky=E, pady=(20,0))
        edsub_scbr = Scrollbar(edit_sub_f)
        edsub_scbr.pack(side=RIGHT, fill=Y)
        subc_listbox = Listbox(edit_sub_f, selectmode = EXTENDED, height=5, relief = SUNKEN, bg='#F4F4F4',
                               yscrollcommand=edsub_scbr.set, exportselection = False)
        subc_listbox.pack(fill=BOTH)
        edsub_scbr.config(command=subc_listbox.yview)

        xx = subc_listbox.bind('<<ListboxSelect>>', onselect_subc)
        subc_listbox.select_set(0)

        # subcorpora edit options
        do_sub = StringVar(root)
        do_sub.set('Off')
        do_with_subc = OptionMenu(editor_buttons, do_sub, *('Off', 'Skip', 'Keep', 'Merge', 'Span'))
        do_with_subc.grid(row=15, column=0, sticky=W)
        do_sub.trace("w", do_s_callback)

        # subcorpora merge name    
        Label(editor_buttons, text='Merge name:').grid(row=16, column=0, sticky='NW')
        new_subc_name = StringVar()
        new_subc_name.set('')
        merge = Entry(editor_buttons, textvariable=new_subc_name, state=DISABLED, font=("Courier New", 13))
        merge.grid(row=17, column=0, sticky='SW', pady=(0, 10))
        all_text_widgets.append(merge)
        
        # name the edit
        edit_nametext=StringVar()
        edit_nametext.set('untitled')
        Label(editor_buttons, text='Edit name', font=("Helvetica", 13, "bold")).grid(row=19, column=0, sticky=W)
        msn = Entry(editor_buttons, textvariable=edit_nametext, width=18)
        msn.grid(row=20, column=0, sticky=W)
        all_text_widgets.append(msn)

        # edit button
        edbut = Button(editor_buttons, text='Edit')
        edbut.config(command=lambda: runner(edbut, do_editing), state=DISABLED)
        edbut.grid(row=20, column=1, sticky=E)

        def editor_spreadsheet_showing_something(*args):
            """if there is anything in an editor window, allow spreadsheet edit button"""
            if name_of_o_ed_spread.get():
                upd_ed_but.config(state=NORMAL)
            else:
                upd_ed_but.config(state=DISABLED)


        # show spreadsheets
        editor_sheets = Frame(tab2)
        editor_sheets.grid(column=1, row=0, sticky='NE')
        resultname = StringVar()
        name_of_o_ed_spread = StringVar()
        name_of_o_ed_spread.set('')
        name_of_o_ed_spread.trace("w", editor_spreadsheet_showing_something)
        resultname.set('Results to edit: %s' % str(name_of_o_ed_spread.get()))
        o_editor_results = Frame(editor_sheets, height=28, width=20)
        o_editor_results.grid(column=1, row=1, rowspan=1, padx=(20, 0), sticky=N)
        Label(editor_sheets, textvariable=resultname, 
              font=("Helvetica", 13, "bold")).grid(row=0, 
               column=1, sticky='NW', padx=(20,0))    
        #Label(editor_sheets, text='Totals to edit:', 
              #font=("Helvetica", 13, "bold")).grid(row=4, 
               #column=1, sticky=W, pady=0)
        o_editor_totals = Frame(editor_sheets, height=1, width=20)
        o_editor_totals.grid(column=1, row=1, rowspan=1, padx=(20,0), sticky=N, pady=(220,0))
        update_spreadsheet(o_editor_results, df_to_show=None, height=160, width=800)
        update_spreadsheet(o_editor_totals, df_to_show=None, height=10, width=800)
        editoname = StringVar()
        name_of_n_ed_spread = StringVar()
        name_of_n_ed_spread.set('')
        editoname.set('Edited results: %s' % str(name_of_n_ed_spread.get()))
        Label(editor_sheets, textvariable=editoname, 
              font=("Helvetica", 13, "bold")).grid(row=1, 
               column=1, sticky='NW', padx=(20,0), pady=(290,0))        
        n_editor_results = Frame(editor_sheets, height=28, width=20)
        n_editor_results.grid(column=1, row=1, rowspan=1, sticky=N, padx=(20,0), pady=(310,0))
        #Label(editor_sheets, text='Edited totals:', 
              #font=("Helvetica", 13, "bold")).grid(row=15, 
               #column=1, sticky=W, padx=20, pady=0)
        n_editor_totals = Frame(editor_sheets, height=1, width=20)
        n_editor_totals.grid(column=1, row=1, rowspan=1, padx=(20,0), pady=(500,0))
        update_spreadsheet(n_editor_results, df_to_show=None, height=160, width=800)
        update_spreadsheet(n_editor_totals, df_to_show=None, height=10, width=800)

        # add button to update
        upd_ed_but = Button(editor_sheets, text='Update interrogation(s)', command=lambda: update_all_interrogations(pane = 'edit'))
        upd_ed_but.grid(row=1, column=1, sticky=E, padx=(0, 40), pady=(594, 0))
        upd_ed_but.config(state=DISABLED)

        #################       #################      #################      #################  
        # VISUALISE TAB #       # VISUALISE TAB #      # VISUALISE TAB #      # VISUALISE TAB #  
        #################       #################      #################      #################  

        plot_option_frame = Frame(tab3)
        plot_option_frame.grid(row=0, column=0, sticky='NW')

        def do_plotting():
            """when you press plot"""
            plotbut.config(state=DISABLED)
            # junk for showing the plot in tkinter
            for i in oldplotframe:
                i.destroy()
            import matplotlib
            matplotlib.use('TkAgg')
            #from numpy import arange, sin, pi
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
            # implement the default mpl key bindings
            from matplotlib.backend_bases import key_press_handler
            from matplotlib.figure import Figure
            from corpkit.plotter import plotter

            if data_to_plot.get() == 'None':
                timestring('No data selected to plot.')            
                return

            if plotbranch.get() == 'results':
                if all_interrogations[data_to_plot.get()].results is None:
                    timestring('No results branch to plot.')   
                    return
                what_to_plot = all_interrogations[data_to_plot.get()].results

            elif plotbranch.get() == 'totals':
                if all_interrogations[data_to_plot.get()].totals is None: 
                    timestring('No totals branch to plot.')
                    return

                what_to_plot = all_interrogations[data_to_plot.get()].totals

            if single_entry.get() != 'All':
                what_to_plot = what_to_plot[single_entry.get()]

            if single_sbcp.get() != 'All':
                what_to_plot = what_to_plot.ix[single_sbcp.get()]
            
            if transpose_vis.get():
                if plotbranch.get() != 'totals':
                    what_to_plot = what_to_plot.T

            # determine num to plot
            def determine_num_to_plot(num):
                """translate num to num_to_plot"""
                try:
                    num = int(num)
                except:
                    if num.lower() == 'all':
                        num = 'all'
                    else:
                        num = 7
                        number_to_plot.set('7')
                return num

            num = determine_num_to_plot(number_to_plot.get())

            the_kind = charttype.get()
            if the_kind == 'Type of chart':
                the_kind = 'line'
            # plotter options
            d = {'num_to_plot': num,
                 'kind': the_kind,
                 'indices': False}

            #the_style = 
            #if the_style == 'matplotlib':
            #lgd = plt.legend(handles[:    the_style = False
            d['style'] = plot_style.get()

            # explode option
            if explbox.get() != '' and charttype.get() == 'pie':
                if explbox.get().startswith('[') and explbox.get().endswith(']') and ',' in explbox.get():
                    explval = explbox.get().lstrip('[').rstrip(']').replace("'", '').replace('"', '').replace(' ', '').split(',')
                else:
                    explval = explbox.get().strip()
                    explval = remake_special_query(explval)
                d['explode'] = explval
            
            texu = texuse.get()
            if texu == 0:
                d['tex'] = False
            else:
                d['tex'] = True

            d['black_and_white'] = bw.get()

            if rl.get() == 1:
                d['reverse_legend'] = True
            
            if sbplt.get() == 1:
                d['subplots'] = True
                d['layout'] = (int(lay1.get()), int(lay2.get()))

            if gridv.get() == 1:
                d['grid'] = True
            else:
                d['grid'] = False

            if stackd.get() == 1:
                d['stacked'] = True

            if part_pie.get() == 1:
                d['partial_pie'] = True

            if filledvar.get() == 1:
                d['filled'] = True

            if log_x.get() == 1:
                d['logx'] = True
            if log_y.get() == 1:
                d['logy'] = True

            if x_axis_l.get() != '':
                d['x_label'] = x_axis_l.get()
            if x_axis_l.get() == 'None':
                d['x_label'] = False
            if y_axis_l.get() != '':
                d['y_label'] = y_axis_l.get()
            if y_axis_l.get() == 'None':
                d['y_label'] = False

            if cumul.get():
                d['cumulative'] = True

            d['colours'] = chart_cols.get()

            legend_loc = legloc.get()
            if legend_loc == 'none':
                d['legend'] = False
            else:
                d['legend_pos'] = legend_loc

            show_totals_in_plot = showtot.get()
            if show_totals_in_plot == 'plot':
                d['show_totals'] = 'plot'
            if show_totals_in_plot == 'legend':
                d['show_totals'] = 'legend'
            if show_totals_in_plot == 'legend + plot':
                d['show_totals'] = 'both'

            d['figsize'] = (int(figsiz1.get()), int(figsiz2.get()))
            f = plotter(what_to_plot, plotnametext.get(), **d)
            
            # latex error
            #except RuntimeError as e:
            #    s = str(e)
            #    print(s)
            #    split_report = s.strip().split('Here is the full report generated by LaTeX:')
            #    try:
            #        if len(split_report) > 0 and split_report[1] != '':
            #            timestring('LaTeX error: %s' % split_report[1])
            #    except:
            #        timestring('LaTeX error: %s' % split_report)
            #    else:
            #        timestring('No TeX distribution found. Disabling TeX option.')
            #        texuse.set(0)
            #        tbut.config(state=DISABLED)
            #    
            #    return

            timestring('%s plotted.' % plotnametext.get())
            
            del oldplotframe[:]

            def getScrollingCanvas(frame):
                """
                    Adds a new canvas with scroll bars to the argument frame
                    NB: uses grid layout
                    @return: the newly created canvas
                """

                frame.grid(column=1, row=0, rowspan = 1, padx=(15, 15), pady=(40, 0), columnspan=3, sticky='NW')
                #frame.rowconfigure(0, weight=9)
                #frame.columnconfigure(0, weight=9)
                canvas = Canvas(frame, width=980, height=500)
                xScrollbar = Scrollbar(frame, orient=HORIZONTAL)
                yScrollbar = Scrollbar(frame)
                xScrollbar.pack(side=BOTTOM,fill=X)
                yScrollbar.pack(side=RIGHT,fill=Y)
                canvas.config(xscrollcommand=xScrollbar.set)
                xScrollbar.config(command=canvas.xview)
                canvas.config(yscrollcommand=yScrollbar.set)
                yScrollbar.config(command=canvas.yview)
                canvas.pack(side=LEFT,expand=True,fill=BOTH)
                return canvas

            frame_for_fig = Frame(tab3)
            #frame_for_fig
            scrollC = getScrollingCanvas(frame_for_fig) 
            mplCanvas = FigureCanvasTkAgg(f.gcf(), frame_for_fig)
            mplCanvas._tkcanvas.config(highlightthickness=0)
            canvas = mplCanvas.get_tk_widget()
            canvas.grid(sticky=NSEW)
            if frame_for_fig not in boxes:
                boxes.append(frame_for_fig)

            scrollC.create_window(0, 0, window=canvas)
            scrollC.config(scrollregion=scrollC.bbox(ALL)) 

            #hbar=Scrollbar(frame_for_fig,orient=HORIZONTAL)
            #hbar.pack(side=BOTTOM,fill=X)
            #hbar.config(command=canvas.get_tk_widget().xview)
            #vbar=Scrollbar(frame_for_fig,orient=VERTICAL)
            #vbar.pack(side=RIGHT,fill=Y)
            #vbar.config(command=canvas.get_tk_widget().yview)
            ##canvas.config(width=300,height=300)
            #canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
            #canvas.pack(side=LEFT,expand=True,fill=BOTH)
            try:
                mplCanvas.show()
            except RuntimeError as e:
                s = str(e)
                print(s)
                split_report = s.strip().split('Here is the full report generated by LaTeX:')
                if len(split_report) > 0 and split_report[1] != '':
                    timestring('LaTeX error: %s' % split_report[1])
                else:
                    timestring('No TeX distribution found. Disabling TeX option.')
                    texuse.set(0)
                    tbut.config(state=DISABLED)
                return
                
            oldplotframe.append(mplCanvas.get_tk_widget())

            del thefig[:]
            
            toolbar_frame = Frame(tab3, borderwidth=0)
            toolbar_frame.grid(row=0, column=1, columnspan=3, sticky='NW', padx=(400,0), pady=(600,0))
            toolbar_frame.lift()

            oldplotframe.append(toolbar_frame)
            toolbar = NavigationToolbar2TkAgg(mplCanvas,toolbar_frame)
            toolbar.update()

            thefig.append(f.gcf())
            savedplot.set('Saved image: ')

        images = {'the_current_fig': -1}

        def move(direction = 'forward'):
            import os
            from PIL import Image
            from PIL import ImageTk
            
            import tkinter

            for i in oldplotframe:
                i.destroy()
            del oldplotframe[:]

            # maybe sort by date added?
            image_list = [i for i in all_images]
            if len(image_list) == 0:
                timestring('No images found in images folder.')
                return
            
            # figure out where we're up to 
            if images['the_current_fig'] != -1:
                ind = image_list.index(images['the_current_fig'])
            else:
                ind = -1

            if direction == 'forward':
                newind = ind + 1
            else:
                newind = ind - 1

            if newind < 1:
                pbut.configure(state=DISABLED)
            else:
                pbut.configure(state=NORMAL)
            if newind + 1 == len(image_list):
                nbut.configure(state=DISABLED)
            else:
                nbut.configure(state=NORMAL)

            imf = image_list[newind]
            if not imf.endswith('.png'):
                imf = imf + '.png'
            image = Image.open(os.path.join(image_fullpath.get(), imf))
            image_to_measure = ImageTk.PhotoImage(image)
            old_height=image_to_measure.height()
            old_width=image_to_measure.width()

            def determine_new_dimensions(height, width):
                maxh = 500
                maxw = 1000
                diff = float(height) / float(width)
                if diff > 1:
                    # make height max
                    newh = maxh
                    # figure out level of magnification
                    prop = maxh / float(height)
                    neww = width * prop
                elif diff < 1:
                    neww = maxw
                    prop = maxw / float(width)
                    newh = height * prop
                elif diff == 1:
                    newh = maxh
                    neww = maxw
                return (int(neww), int(newh))
            # calculate new dimensions
            newdimensions = determine_new_dimensions(old_height, old_width)
            
            # determine left  padding
            padxright = 20
            if newdimensions[0] != 1000:
                padxleft = ((1000 - newdimensions[0]) / 2) + 40
            else:
                padxleft = 40
            padytop = (500 - newdimensions[1]) / 2
            
            def makezero(n):
                if n < 0:
                    return 0
                else:
                    return n
            
            padxright = makezero(padxright)
            padxleft = makezero(padxleft)
            padytop = makezero(padytop)

            image = image.resize(newdimensions)
            image = ImageTk.PhotoImage(image)
            frm = Frame(tab3, height=500, width=1000)
            frm.grid(column=1, row=0, rowspan = 1, padx=(padxleft, padxright), \
                      pady=padytop, columnspan=3)
            gallframe = Label(frm, image = image, justify=CENTER)
            gallframe.pack(anchor='center', fill=BOTH)
            oldplotframe.append(frm)
            images[image_list[newind]] = image
            images['the_current_fig'] = image_list[newind]
            savedplot.set('Saved image: %s' % os.path.splitext(image_list[newind])[0])
            
            timestring('Viewing %s' % os.path.splitext(image_list[newind])[0])

        savedplot = StringVar()
        savedplot.set('View saved images: ')
        Label(tab3, textvariable=savedplot, font=("Helvetica", 13, "bold")).grid(row=0, column=1, padx=(40,0), pady=(566,0), sticky=W)
        pbut = Button(tab3, text='Previous', command=lambda: move(direction = 'back'))
        pbut.grid(row=0, column=1, padx=(40,0), pady=(616,0), sticky=W)
        pbut.config(state=DISABLED)
        nbut = Button(tab3, text='Next', command=lambda: move(direction = 'forward'))
        nbut.grid(row=0, column=1, padx=(160,0), pady=(616,0), sticky=W)
        nbut.config(state=DISABLED)

        # not in use while using the toolbar instead...
        #def save_current_image():
        #    import os
        #    # figre out filename
        #    filename = namer(plotnametext.get(), type_of_data = 'image') + '.png'
        #    import sys
        #    defaultextension = '.png' if sys.platform == 'darwin' else ''
        #    kwarg = {'defaultextension': defaultextension,
        #             #'filetypes': [('all files', '.*'), 
        #                           #('png file', '.png')],
        #             'initialfile': filename}
        #    imagedir = image_fullpath.get()
        #    if imagedir:
        #        kwarg['initialdir'] = imagedir
        #    fo = tkFileDialog.asksaveasfilename(**kwarg)
        #    if fo is None: # asksaveasfile return `None` if dialog closed with "cancel".
        #        return
        #    thefig[0].savefig(os.path.join(image_fullpath.get(), fo))
        #    timestring('%s saved to %s.' % (fo, image_fullpath.get()))

        # title tab

        Label(plot_option_frame, text='Image title:').grid(row=0, column=0, sticky='W', pady=(10, 0))
        plotnametext=StringVar()
        plotnametext.set('Untitled')
        image_title_entry = Entry(plot_option_frame, textvariable=plotnametext)
        image_title_entry.grid(row=0, column=1, pady=(10, 0))
        all_text_widgets.append(image_title_entry)

        def plot_callback(*args):
            """enable/disable based on selected dataset for plotting"""
            if data_to_plot.get() == 'None':
                plotbut.config(state=DISABLED)
            else:
                plotbut.config(state=NORMAL)
            try:
                thisdata = all_interrogations[data_to_plot.get()]
            except KeyError:
                return
            single_entry.set('All')
            single_sbcp.set('All')

            subdrs = sorted(set([d for d in os.listdir(corpus_fullpath.get()) \
                            if os.path.isdir(os.path.join(corpus_fullpath.get(),d))]))
            
            single_sbcp_optmenu.config(state=NORMAL)
            single_sbcp_optmenu['menu'].delete(0, 'end')
            single_sbcp_optmenu['menu'].add_command(label='All', command=_setit(single_sbcp, 'All'))
            lst = []
            if len(subdrs) > 0:
                for c in subdrs:
                    lst.append(c)
                    single_sbcp_optmenu['menu'].add_command(label=c, command=_setit(single_sbcp, c))
                single_entry_or_subcorpus['subcorpora'] = lst
            else:
                single_sbcp_optmenu.config(state=NORMAL)
                single_sbcp_optmenu['menu'].delete(0, 'end')
                single_sbcp_optmenu['menu'].add_command(label='All', command=_setit(single_sbcp, 'All'))
                single_sbcp_optmenu.config(state=DISABLED)

            if thisdata.results is not None:
                plotbox.config(state=NORMAL)
                single_ent_optmenu.config(state=NORMAL)
                single_ent_optmenu['menu'].delete(0, 'end')
                single_ent_optmenu['menu'].add_command(label='All', command=_setit(single_entry, 'All'))
                lst = []
                for corp in list(thisdata.results.columns)[:200]:
                    lst.append(corp)
                    single_ent_optmenu['menu'].add_command(label=corp, command=_setit(single_entry, corp))
                single_entry_or_subcorpus['entries'] = lst
            else:
                single_ent_optmenu.config(state=NORMAL)
                single_ent_optmenu['menu'].delete(0, 'end')
                single_ent_optmenu['menu'].add_command(label='All', command=_setit(single_entry, 'All'))
                single_ent_optmenu.config(state=DISABLED)
                plotbox.config(state=NORMAL)
                plotbranch.set('totals')
                plotbox.config(state=DISABLED)

        Label(plot_option_frame, text='Data to plot:').grid(row=1, column=0, sticky=W)
        # select result to plot
        data_to_plot = StringVar(root)
        most_recent = all_interrogations[list(all_interrogations.keys())[-1]]
        data_to_plot.set(most_recent)
        every_interrogation = OptionMenu(plot_option_frame, data_to_plot, *tuple([i for i in list(all_interrogations.keys())]))
        every_interrogation.config(width=20)
        every_interrogation.grid(column=0, row=2, sticky=W, columnspan=2)
        data_to_plot.trace("w", plot_callback)
        Label(plot_option_frame, text='Entry:').grid(row=3, column=0, sticky=W)
        single_entry = StringVar(root)
        single_entry.set('All')
        #most_recent = all_interrogations[all_interrogations.keys()[-1]]
        #single_entry.set(most_recent)
        single_ent_optmenu = OptionMenu(plot_option_frame, single_entry, *tuple(['']))
        single_ent_optmenu.config(width=20, state=DISABLED)
        single_ent_optmenu.grid(column=1, row=3, sticky=E)

        def single_entry_plot_callback(*args):
            """turn off things if single entry selected"""
            if single_entry.get() != 'All':
                sbpl_but.config(state=NORMAL)
                sbplt.set(0)
                sbpl_but.config(state=DISABLED)
                num_to_plot_box.config(state=NORMAL)
                number_to_plot.set('1')
                num_to_plot_box.config(state=DISABLED)
                single_sbcp_optmenu.config(state=DISABLED)
                entries = single_entry_or_subcorpus['entries']
                if plotnametext.get() == 'Untitled' or plotnametext.get() in entries:
                    plotnametext.set(single_entry.get())
            else:
                plotnametext.set('Untitled')
                sbpl_but.config(state=NORMAL)
                number_to_plot.set('7')
                num_to_plot_box.config(state=NORMAL)
                single_sbcp_optmenu.config(state=NORMAL)

        single_entry.trace("w", single_entry_plot_callback)

        Label(plot_option_frame, text='Subcorpus:').grid(row=4, column=0, sticky=W)
        single_sbcp = StringVar(root)
        single_sbcp.set('All')
        #most_recent = all_interrogations[all_interrogations.keys()[-1]]
        #single_sbcp.set(most_recent)
        single_sbcp_optmenu = OptionMenu(plot_option_frame, single_sbcp, *tuple(['']))
        single_sbcp_optmenu.config(width=20, state=DISABLED)
        single_sbcp_optmenu.grid(column=1, row=4, sticky=E)

        def single_sbcp_plot_callback(*args):
            """turn off things if single entry selected"""
            if single_sbcp.get() != 'All':
                sbpl_but.config(state=NORMAL)
                sbplt.set(0)
                sbpl_but.config(state=DISABLED)
                num_to_plot_box.config(state=NORMAL)
                #number_to_plot.set('1')
                #num_to_plot_box.config(state=DISABLED)
                single_ent_optmenu.config(state=DISABLED)
                charttype.set('bar')
                entries = single_entry_or_subcorpus['subcorpora']
                if plotnametext.get() == 'Untitled' or plotnametext.get() in entries:
                    plotnametext.set(single_sbcp.get())
            else:
                plotnametext.set('Untitled')
                sbpl_but.config(state=NORMAL)
                #number_to_plot.set('7')
                num_to_plot_box.config(state=NORMAL)
                single_ent_optmenu.config(state=NORMAL)
                charttype.set('line')

        single_sbcp.trace("w", single_sbcp_plot_callback)

        # branch selection
        plotbranch = StringVar(root)
        plotbranch.set('results')
        plotbox = OptionMenu(plot_option_frame, plotbranch, 'results', 'totals')
        #plotbox.config(state=DISABLED)
        plotbox.grid(row=2, column=0, sticky=E, columnspan=2)

        def plotbranch_callback(*args):
            if plotbranch.get() == 'totals':
                single_sbcp_optmenu.config(state=DISABLED)
                single_ent_optmenu.config(state=DISABLED)
                sbpl_but.config(state=NORMAL)
                sbplt.set(0)
                sbpl_but.config(state=DISABLED)
                trans_but_vis.config(state=NORMAL)
                transpose_vis.set(0)
                trans_but_vis.config(state=DISABLED)
            else:
                single_sbcp_optmenu.config(state=NORMAL)
                single_ent_optmenu.config(state=NORMAL)
                sbpl_but.config(state=NORMAL)
                trans_but_vis.config(state=NORMAL)

        plotbranch.trace('w', plotbranch_callback)

        # num_to_plot
        Label(plot_option_frame, text='Results to show:').grid(row=5, column=0, sticky=W)
        number_to_plot = StringVar()
        number_to_plot.set('7')
        num_to_plot_box = Entry(plot_option_frame, textvariable=number_to_plot, width=3)
        num_to_plot_box.grid(row=5, column=1, sticky=E)
        all_text_widgets.append(num_to_plot_box)

        def pie_callback(*args):
            if charttype.get() == 'pie':
                explbox.config(state=NORMAL)
                ppie_but.config(state=NORMAL)
            else:
                explbox.config(state=DISABLED)
                ppie_but.config(state=DISABLED)

            if charttype.get().startswith('bar'):
                stackbut.config(state=NORMAL)
                filledbut.config(state=NORMAL)
            else:
                stackbut.config(state=DISABLED)
                filledbut.config(state=DISABLED)

            # can't do log y with area according to mpl
            if charttype.get() == 'area':
                logybut.unselect()
                logybut.config(state=DISABLED)
                filledbut.config(state=NORMAL)
            else:
                logybut.config(state=NORMAL)
                filledbut.config(state=DISABLED)

        # chart type
        Label(plot_option_frame, text='Kind of chart').grid(row=6, column=0, sticky=W)
        charttype = StringVar(root)
        charttype.set('line')
        kinds_of_chart = ('line', 'bar', 'barh', 'pie', 'area', 'heatmap')
        chart_kind = OptionMenu(plot_option_frame, charttype, *kinds_of_chart)
        chart_kind.config(width=10)
        chart_kind.grid(row=6, column=1, sticky=E)
        charttype.trace("w", pie_callback)

        # axes
        Label(plot_option_frame, text='x axis label:').grid(row=7, column=0, sticky=W)
        x_axis_l = StringVar()
        x_axis_l.set('')
        tmp = Entry(plot_option_frame, textvariable=x_axis_l, font=("Courier New", 14), width=18)
        tmp.grid(row=7, column=1, sticky=E)
        all_text_widgets.append(tmp)

        Label(plot_option_frame, text='y axis label:').grid(row=8, column=0, sticky=W)
        y_axis_l = StringVar()
        y_axis_l.set('')
        tmp = Entry(plot_option_frame, textvariable=y_axis_l, font=("Courier New", 14), width=18)
        tmp.grid(row=8, column=1, sticky=E)
        all_text_widgets.append(tmp)

        Label(plot_option_frame, text='Explode:').grid(row=9, column=0, sticky=W)
        explval = StringVar()
        explval.set('')
        explbox = Entry(plot_option_frame, textvariable=explval, font=("Courier New", 14), width=18)
        explbox.grid(row=9, column=1, sticky=E)
        all_text_widgets.append(explbox)
        explbox.config(state=DISABLED)

        # log options
        log_x = IntVar()
        Checkbutton(plot_option_frame, text="Log x axis", variable=log_x).grid(column=0, row=10, sticky=W)
        log_y = IntVar()
        logybut = Checkbutton(plot_option_frame, text="Log y axis", variable=log_y, width=13)
        logybut.grid(column=1, row=10, sticky=E)

        # transpose
        transpose_vis = IntVar()
        trans_but_vis = Checkbutton(plot_option_frame, text="Transpose", variable=transpose_vis, onvalue = True, offvalue = False, width=13)
        trans_but_vis.grid(column=1, row=11, sticky=E)

        cumul = IntVar()
        cumulbutton = Checkbutton(plot_option_frame, text="Cumulative", variable=cumul, onvalue = True, offvalue = False)
        cumulbutton.grid(column=0, row=11, sticky=W)

        bw = IntVar()
        Checkbutton(plot_option_frame, text="Black and white", variable=bw, onvalue = True, offvalue = False).grid(column=0, row=12, sticky=W)
        texuse = IntVar()
        tbut = Checkbutton(plot_option_frame, text="Use TeX", variable=texuse, onvalue = True, offvalue = False, width=13)
        tbut.grid(column=1, row=12, sticky=E)
        tbut.deselect()
        if not py_script:
            tbut.config(state=DISABLED)

        rl = IntVar()
        Checkbutton(plot_option_frame, text="Reverse legend", variable=rl, onvalue = True, offvalue = False).grid(column=0, row=13, sticky=W)
        sbplt = IntVar()
        sbpl_but = Checkbutton(plot_option_frame, text="Subplots", variable=sbplt, onvalue = True, offvalue = False, width=13)
        sbpl_but.grid(column=1, row=13, sticky=E)

        def sbplt_callback(*args):
            """if subplots are happening, allow layout"""
            if sbplt.get():
                lay1menu.config(state=NORMAL)
                lay2menu.config(state=NORMAL)
            else:
                lay1menu.config(state=DISABLED)
                lay2menu.config(state=DISABLED)

        sbplt.trace("w", sbplt_callback)


        gridv = IntVar()
        gridbut = Checkbutton(plot_option_frame, text="Grid", variable=gridv, onvalue = True, offvalue = False)
        gridbut.select()
        gridbut.grid(column=0, row=14, sticky=W)

        stackd = IntVar()
        stackbut = Checkbutton(plot_option_frame, text="Stacked", variable=stackd, onvalue = True, offvalue = False, width=13)
        stackbut.grid(column=1, row=14, sticky=E)
        stackbut.config(state=DISABLED)

        part_pie = IntVar()
        ppie_but = Checkbutton(plot_option_frame, text="Partial pie", variable=part_pie, onvalue = True, offvalue = False)
        ppie_but.grid(column=0, row=15, sticky=W)
        ppie_but.config(state=DISABLED)

        filledvar = IntVar()
        filledbut = Checkbutton(plot_option_frame, text="Filled", variable=filledvar, onvalue = True, offvalue = False, width=13)
        filledbut.grid(column=1, row=15, sticky=E)
        filledbut.config(state=DISABLED)


        # chart type
        Label(plot_option_frame, text='Colour scheme:').grid(row=16, column=0, sticky=W)
        chart_cols = StringVar(root)
        schemes = tuple(sorted(('Paired', 'Spectral', 'summer', 'Set1', 'Set2', 'Set3', 
                    'Dark2', 'prism', 'RdPu', 'YlGnBu', 'RdYlBu', 'gist_stern', 'cool', 'coolwarm',
                    'gray', 'GnBu', 'gist_ncar', 'gist_rainbow', 'Wistia', 'CMRmap', 'bone', 
                    'RdYlGn', 'spring', 'terrain', 'PuBu', 'spectral', 'rainbow', 'gist_yarg', 
                    'BuGn', 'bwr', 'cubehelix', 'Greens', 'PRGn', 'gist_heat', 'hsv', 
                    'Pastel2', 'Pastel1', 'jet', 'gist_earth', 'copper', 'OrRd', 'brg', 
                    'gnuplot2', 'BuPu', 'Oranges', 'PiYG', 'YlGn', 'Accent', 'gist_gray', 'flag', 
                    'BrBG', 'Reds', 'RdGy', 'PuRd', 'Blues', 'autumn', 'ocean', 'pink', 'binary', 
                    'winter', 'gnuplot', 'hot', 'YlOrBr', 'seismic', 'Purples', 'RdBu', 'Greys', 
                    'YlOrRd', 'PuOr', 'PuBuGn', 'nipy_spectral', 'afmhot', 
                    'viridis', 'magma', 'plasma', 'inferno', 'diverge', 'default')))
        ch_col = OptionMenu(plot_option_frame, chart_cols, *schemes)
        ch_col.config(width=17)
        ch_col.grid(row=16, column=1, sticky=E)
        chart_cols.set('viridis')
        # style
        if not py_script:
            mplsty_path = os.path.join(rd, 'matplotlib', 'mpl-data', 'stylelib')
            stys = tuple(sorted([i.split('.')[0] for i in os.listdir(mplsty_path) if i.endswith('.mplstyle')]))
        else:
            stys = tuple(('ggplot', 'fivethirtyeight', 'bmh', 'matplotlib', \
                          'mpl-white', 'seaborn-dark', 'classic', 'seaborn-talk'))
        plot_style = StringVar(root)
        plot_style.set('ggplot')
        Label(plot_option_frame, text='Plot style:').grid(row=17, column=0, sticky=W)
        pick_a_style = OptionMenu(plot_option_frame, plot_style, *stys)
        pick_a_style.config(width=17)
        pick_a_style.grid(row=17, column=1, sticky=E)

        def ps_callback(*args):
            if plot_style.get().startswith('seaborn'):
                chart_cols.set('Default')
                ch_col.config(state=DISABLED)
            else:
                ch_col.config(state=NORMAL)

        plot_style.trace("w", ps_callback)

        # legend pos
        Label(plot_option_frame, text='Legend position:').grid(row=18, column=0, sticky=W)
        legloc = StringVar(root)
        legloc.set('best')
        locs = tuple(('best', 'upper right', 'right', 'lower right', 'lower left', 'upper left', 'middle', 'none'))
        loc_options = OptionMenu(plot_option_frame, legloc, *locs)
        loc_options.config(width=17)
        loc_options.grid(row=18, column=1, sticky=E)

        # figure size
        Label(plot_option_frame, text='Figure size:').grid(row=19, column=0, sticky=W)
        figsiz1 = StringVar(root)
        figsiz1.set('12')
        figsizes = tuple(('2', '4', '6', '8', '10', '12', '14', '16', '18'))
        fig1 = OptionMenu(plot_option_frame, figsiz1, *figsizes)
        fig1.configure(width=6)
        fig1.grid(row=19, column=1, sticky=W, padx=(27, 0))
        Label(plot_option_frame, text="x").grid(row=19, column=1, padx=(30, 0))
        figsiz2 = StringVar(root)
        figsiz2.set('6')
        fig2 = OptionMenu(plot_option_frame, figsiz2, *figsizes)
        fig2.configure(width=6)
        fig2.grid(row=19, column=1, sticky=E)

        # subplots layout
        Label(plot_option_frame, text='Subplot layout:').grid(row=20, column=0, sticky=W)
        lay1 = StringVar(root)
        lay1.set('3')
        figsizes = tuple([str(i) for i in range(1, 20)])
        lay1menu = OptionMenu(plot_option_frame, lay1, *figsizes)
        lay1menu.configure(width=6)
        lay1menu.grid(row=20, column=1, sticky=W, padx=(27, 0))
        Label(plot_option_frame, text="x").grid(row=20, column=1, padx=(30, 0))
        lay2 = StringVar(root)
        lay2.set('3')
        lay2menu = OptionMenu(plot_option_frame, lay2, *figsizes)
        lay2menu.configure(width=6)
        lay2menu.grid(row=20, column=1, sticky=E)
        lay1menu.config(state=DISABLED)
        lay2menu.config(state=DISABLED)

        # show_totals option
        Label(plot_option_frame, text='Show totals: ').grid(row=21, column=0, sticky=W)
        showtot = StringVar(root)
        showtot.set('Off')
        showtot_options = tuple(('Off', 'legend', 'plot', 'legend + plot'))
        show_tot_menu = OptionMenu(plot_option_frame, showtot, *showtot_options)
        show_tot_menu.grid(row=21, column=1, sticky=E)

        # plot button
        plotbut = Button(plot_option_frame, text='Plot')
        plotbut.grid(row=22, column=1, sticky=E)
        plotbut.config(command=lambda: runner(plotbut, do_plotting), state=DISABLED)

        ###################     ###################     ###################     ###################
        # CONCORDANCE TAB #     # CONCORDANCE TAB #     # CONCORDANCE TAB #     # CONCORDANCE TAB #
        ###################     ###################     ###################     ###################

        def add_conc_lines_to_window(data, loading = False, preserve_colour=True):
            import pandas as pd
            import re
            #pd.set_option('display.height', 1000)
            #pd.set_option('display.width', 1000)
            pd.set_option('display.max_colwidth', 200)
            import corpkit
            from corpkit.interrogation import Concordance
            if data.__class__ == Concordance:
                current_conc[0] = data

            elif type(data) == pd.core.frame.DataFrame:
                data = Concordance(data)
                current_conc[0] = data
            else:
                current_conc[0] = data.concordance
                data = data.concordance
            if win.get() == 'Window':
                window = 70
            else:
                window = int(win.get())

            fnames = show_filenames.get()
            them = show_themes.get()
            spk = show_speaker.get()
            subc = show_subcorpora.get()

            if not fnames:
                data = data.drop('f', axis = 1, errors = 'ignore')
            if not them:
                data = data.drop('t', axis = 1, errors = 'ignore')
            if not spk:
                data = data.drop('s', axis = 1, errors = 'ignore')
            if not subc:
                data = data.drop('c', axis = 1, errors = 'ignore')

            if them:
                data = data.drop('t', axis = 1, errors = 'ignore')
                themelist = get_list_of_themes(data)
                if any(t != '' for t in themelist):
                    data.insert(0, 't', themelist)

            # only do left align when long result ...
            # removed because it's no big deal if always left aligned, and this
            # copes when people search for 'root' or something.

            def resize_by_window_size(df, window):
                df['l'] = df['l'].str.slice(start=-window, stop=None)
                df['l'] = df['l'].str.rjust(window)
                df['r'] = df['r'].str.slice(start = 0, stop = window)
                df['r'] = df['r'].str.ljust(window)
                df['m'] = df['m'].str.ljust(df['m'].str.len().max())
                return df

            moddata = resize_by_window_size(data, window)
            lines = moddata.to_string(header = False, index = show_index.get()).splitlines()
            #lines = [re.sub('\s*\.\.\.\s*$', '', s) for s in lines]
            conclistbox.delete(0, END)
            for line in lines:
                conclistbox.insert(END, line)
            if preserve_colour:
                # itemcoldict has the NUMBER and COLOUR
                index_regex = re.compile(r'^([0-9]+)')
                # make dict for NUMBER:INDEX 
                index_dict = {}
                lines = conclistbox.get(0, END)
                for index, line in enumerate(lines):
                    index_dict[int(re.search(index_regex, conclistbox.get(index)).group(1))] = index
                todel = []
                for item, colour in list(itemcoldict.items()):
                    try:
                        conclistbox.itemconfig(index_dict[item], {'bg':colour})
                    except KeyError:
                        todel.append(item)
                for i in todel:
                    del itemcoldict[i]

            if loading:
                timestring('Concordances loaded.')
            else:
                timestring('Concordancing done: %d results.' % len(lines))

        
        
        def delete_conc_lines(*args):
            if type(current_conc[0]) == str:
                return
            items = conclistbox.curselection()
            #current_conc[0].results.drop(current_conc[0].results.iloc[1,].name)
            r = current_conc[0].drop([current_conc[0].iloc[int(n),].name for n in items])
            add_conc_lines_to_window(r)
            if len(items) == 1:
                timestring('%d line removed.' % len(items))
            if len(items) > 1:
                timestring('%d lines removed.' % len(items))
            global conc_saved
            conc_saved = False

        def delete_reverse_conc_lines(*args):   
            
            if type(current_conc[0]) == str:
                return
            items = [int(i) for i in conclistbox.curselection()]
            r = current_conc[0].iloc[items,]
            add_conc_lines_to_window(r)
            conclistbox.select_set(0, END)
            if len(conclistbox.get(0, END)) - len(items) == 1:
                timestring('%d line removed.' % ((len(conclistbox.get(0, END)) - len(items))))
            if len(conclistbox.get(0, END)) - len(items) > 1:
                timestring('%d lines removed.' % ((len(conclistbox.get(0, END)) - len(items))))
            global conc_saved
            conc_saved = False

        def conc_export(data = 'default'):
            """export conc lines to csv"""
            import os
            import pandas
            
            if type(current_conc[0]) == str:
                timestring('Nothing to export.')
                return
            if in_a_project.get() == 0:
                home = os.path.expanduser("~")
                docpath = os.path.join(home, 'Documents')
            else:
                docpath = project_fullpath.get()
            if data == 'default':
                thedata = current_conc[0]
                thedata = thedata.to_csv(header = False, sep = '\t')
            else:
                thedata = all_conc[data]
                thedata = thedata.to_csv(header = False, sep = '\t')
            if sys.platform == 'darwin':
                the_kwargs = {'message': 'Choose a name and place for your exported data.'}
            else:
                the_kwargs = {}
            savepath = filedialog.asksaveasfilename(title = 'Save file',
                                           initialdir = exported_fullpath.get(),
                                           defaultextension = '.csv',
                                           initialfile = 'data.csv',
                                           **the_kwargs)
            if savepath == '':
                return
            with open(savepath, "w") as fo:
                fo.write(thedata)
            timestring('Concordance lines exported.')
            global conc_saved
            conc_saved = False

        def get_list_of_colours(df):
            flipped_colour={v: k for k, v in list(colourdict.items())}
            colours = []
            for i in list(df.index):
                # if the item has been coloured
                if i in list(itemcoldict.keys()):
                    itscolour=itemcoldict[i]
                    colournumber = flipped_colour[itscolour]
                    # append the number of the colour code, with some corrections
                    if colournumber == 0:
                        colournumber = 10
                    if colournumber == 9:
                        colournumber = 99
                    colours.append(colournumber)
                else:
                    colours.append(10)
            return colours

        def get_list_of_themes(df):
            flipped_colour={v: k for k, v in list(colourdict.items())}
            themes = []
            for i in list(df.index):
                # if the item has been coloured
                if i in list(itemcoldict.keys()):
                    itscolour=itemcoldict[i]
                    colournumber = flipped_colour[itscolour]
                    theme = entryboxes[list(entryboxes.keys())[colournumber]].get()
                    # append the number of the colour code, with some corrections
                    if theme is not False and theme != '':
                        themes.append(theme)
                    else:
                        themes.append('')
                else:
                    themes.append('')
            if all(i == '' for i in themes):
                timestring('Warning: no scheme defined.')
            return themes

        def conc_sort(*args):
            """various sorting for conc, by updating dataframe"""
            import re
            import pandas
            import itertools
            sort_way = True
            if type(current_conc[0]) == str:
                return
            if prev_sortval[0] == sortval.get():
                # if subcorpus is the same, etc, as well
                sort_way = toggle()
            df = current_conc[0]
            prev_sortval[0] = sortval.get()
            # sorting by first column is easy, so we don't need pandas
            if sortval.get() == 'M1':
                low = [l.lower() for l in df['m']]
                df['tosorton'] = low
            elif sortval.get() == 'File':
                low = [l.lower() for l in df['f']]
                df['tosorton'] = low
            elif sortval.get() == 'Colour':
                colist = get_list_of_colours(df)
                df['tosorton'] = colist
            elif sortval.get() == 'Scheme':
                themelist = get_list_of_themes(df)
                #df.insert(1, 't', themelist)
                df.insert(1, 'tosorton', themelist)
            elif sortval.get() == 'Index':
                df = df.sort(ascending = sort_way)
            elif sortval.get() == 'Subcorpus':
                sbs = [l.lower() for l in df['c']]
                df['tosorton'] = sbs
            elif sortval.get() == 'Random':
                import pandas
                import numpy as np
                df = df.reindex(np.random.permutation(df.index))

            elif sortval.get() == 'Speaker':
                try:
                    low = [l.lower() for l in df['s']]
                except:
                    timestring('No speaker information to sort by.')
                    return
                df['tosorton'] = low
            # if sorting by other columns, however, it gets tough.
            else:
                from nltk import word_tokenize as tokenise
                td = {}
                #if 'note' in kwargs.keys():
                #    td['note'] = kwargs['note']
                #    add_nltk_data_to_nltk_path(**td)
                timestring('Tokenising concordance lines ... ')
                # tokenise the right part of each line
                # get l or r column
                col = sortval.get()[0].lower()
                tokenised = [tokenise(s) for s in list(df[col].values)]
                if col == 'm':
                    repeats = 2
                else:
                    repeats  = 6
                for line in tokenised:
                    for i in range(6 - len(line)):
                        if col == 'l':
                            line.insert(0, '')
                        if col == 'r':
                            line.append('')

                # get 1-5 and convert it
                num = int(sortval.get().lstrip('LMR'))
                if col == 'l':
                    num = -num
                if col == 'r':
                    num = num - 1

                just_sortword = []
                for l in tokenised:    
                    if col != 'm':
                        just_sortword.append(l[num].lower())
                    else:
                        # horrible
                        if len(l) == 1:
                            just_sortword.append(l[0].lower())
                        elif len(l) > 1:
                            if num == 2:
                                just_sortword.append(l[1].lower())
                            elif num == -2:
                                just_sortword.append(l[-2].lower())
                            elif num == -1:
                                just_sortword.append(l[-1].lower())

                # append list to df
                df['tosorton'] = just_sortword

            if sortval.get() != 'Index' and sortval.get() != 'Random':
                df = df.sort(['tosorton'], ascending = sort_way)
                df = df.drop(['tosorton'], axis = 1, errors = 'ignore')
            if show_filenames.get() == 0:
                add_conc_lines_to_window(df.drop('f', axis = 1, errors = 'ignore'))
            else:
                add_conc_lines_to_window(df)
            
            timestring('%d concordance lines sorted.' % len(conclistbox.get(0, END)))
            global conc_saved
            conc_saved = False

        def do_inflection(pos = 'v'):
            global tb
            from dictionaries.process_types import get_both_spellings, add_verb_inflections
            
            # get every word
            all_words = [w.strip().lower() for w in tb.get(1.0, END).split()]
            # try to get just selection
            cursel = False
            try:
                lst = [w.strip().lower() for w in tb.get(SEL_FIRST, SEL_LAST).split()]
                cursel = True
            except:
                lst = [w.strip().lower() for w in tb.get(1.0, END).split()]
            lst = get_both_spellings(lst)
            if pos == 'v':
                expanded = add_verb_inflections(lst)
            if pos == 'n':
                from corpkit.inflect import pluralize
                expanded = []
                for w in lst:
                    expanded.append(w)
                    pl = pluralize(w)
                    if pl != w:
                        expanded.append(pl)
            if pos == 'a':
                from corpkit.inflect import grade
                expanded = []
                for w in lst:
                    expanded.append(w)
                    comp = grade(w, suffix = "er")
                    if comp != w:
                        expanded.append(comp)
                    supe = grade(w, suffix = "est")
                    if supe != w:
                        expanded.append(supe)
            if cursel:
                expanded = expanded + all_words
            lst = sorted(set(expanded))
            # delete widget text, reinsrt all
            tb.delete(1.0, END)
            for w in lst:
                tb.insert(END, w + '\n')

        def make_dict_from_existing_wordlists():
            from collections import namedtuple
            def convert(dictionary):
                return namedtuple('outputnames', list(dictionary.keys()))(**dictionary)
            all_preset_types = {}
            from dictionaries.process_types import processes
            from dictionaries.roles import roles
            from dictionaries.wordlists import wordlists
            from corpkit.other import as_regex
            customs = convert(custom_special_dict)
            special_qs = [processes, roles, wordlists]
            for kind in special_qs:
                types = [k for k in list(kind.__dict__.keys())]
                for t in types:
                    if kind == roles:
                        all_preset_types[t.upper() + '_ROLE'] = kind.__dict__[t]
                    else:
                        all_preset_types[t.upper()] = kind.__dict__[t]
            return all_preset_types
        
        predict = make_dict_from_existing_wordlists()

        for k, v in list(predict.items()):
            custom_special_dict[k.upper()] = v

        def store_wordlist():
            global tb
            lst = [w.strip().lower() for w in tb.get(1.0, END).split()]
            global schemename
            if schemename.get() == '<Enter a name>':
                timestring('Wordlist needs a name.')
                return
            specname = ''.join([i for i in schemename.get().upper() if i.isalnum() or i == '_'])
            if specname in list(predict.keys()):
                timestring('Name "%s" already taken, sorry.' % specname)
                return
            else:
                if specname in list(custom_special_dict.keys()):
                    should_continue = messagebox.askyesno("Overwrite list", 
                              "Overwrite existing list named '%s'?" % specname)
                    if not should_continue:
                        return
            custom_special_dict[specname] = lst
            global cust_spec
            cust_spec.delete(0, END)
            for k, v in sorted(custom_special_dict.items()):
                cust_spec.insert(END, k)
            color_saved(cust_spec, colour1 = '#ccebc5', colour2 = '#fbb4ae', lists = True)
            timestring('LIST:%s stored to custom wordlists.' % specname)


        parser_opts = StringVar()
        speakseg = IntVar()

        def parser_options():
            """a popup with corenlp options, to display before parsing.
            this is a good candidate for 'preferences'"""
            from tkinter import Toplevel
            global poptions
            poptions = Toplevel()
            poptions.title('Parser options')
            from collections import OrderedDict

            popt = OrderedDict()
            for k, v in [('Tokenise', 'tokenize'),
                        ('Sentence splitting', 'ssplit'),
                        ('POS tagging', 'pos'),
                        ('Lemmatisation', 'lemma'),
                        ('Named entity recognition', 'ner'),
                        ('Parse', 'parse'),
                        ('Referent tracking', 'dcoref')]:
                        popt[k] = v

            butvar = {}
            butbut = {}

            orders = {'tokenize': 0,
                      'ssplit': 1,
                      'pos': 2,
                      'lemma': 3,
                      'ner': 4,
                      'parse': 5,
                      'dcoref': 6}

            for index, (k, v) in enumerate(popt.items()):
                tmp = StringVar()
                but = Checkbutton(poptions, text=k, variable=tmp, onvalue = v, offvalue = False)
                but.grid(sticky=W)
                if k != 'Referent tracking' and k != 'Named entity recognition':
                    but.select()
                else:
                    but.deselect()
                butbut[index] = but
                butvar[index] = tmp
            
            Checkbutton(poptions, text='Speaker segmentation', variable=speakseg, onvalue = True, offvalue = False).grid(sticky=W)

            def optionspicked(*args):
                vals = [i.get() for i in list(butvar.values()) if i.get() is not False and i.get() != 0 and i.get() != '0']
                vals = sorted(vals, key=lambda x:orders[x])
                the_opts = ','.join(vals)
                poptions.destroy()
                parser_opts.set(the_opts)

            stopbut = Button(poptions, text='Done', command=optionspicked)
            stopbut.grid()

        ##############    ##############     ##############     ##############     ############## 
        # WORDLISTS  #    # WORDLISTS  #     # WORDLISTS  #     # WORDLISTS  #     # WORDLISTS  # 
        ##############    ##############     ##############     ##############     ############## 

        def custom_lists():
            """a popup for defining custom wordlists"""
            from tkinter import Toplevel
            popup = Toplevel()
            popup.title('Custom wordlists')
            popup.wm_attributes('-topmost', 1)
            Label(popup, text='Create wordlist', font=("Helvetica", 13, "bold")).grid(column=0, row=0)
            global schemename
            schemename = StringVar()
            schemename.set('<Enter a name>')
            scheme_name_field = Entry(popup, textvariable=schemename, justify=CENTER, width=21, font=("Courier New", 13))
            #scheme_name_field.bind('<Button-1>', select_all_text)
            scheme_name_field.grid(column=0, row=5, sticky=W, padx=(7, 0))
            global tb
            custom_words = Frame(popup, width=9, height=40)
            custom_words.grid(row=1, column=0, padx=5)
            cwscrbar = Scrollbar(custom_words)
            cwscrbar.pack(side=RIGHT, fill=Y)
            tb = Text(custom_words, yscrollcommand=cwscrbar.set, relief = SUNKEN,
                      bg='#F4F4F4', width=20, height=26, font=("Courier New", 13))
            cwscrbar.config(command=tb.yview)
            bind_textfuncts_to_widgets([tb, scheme_name_field])
            tb.pack(side=LEFT, fill=BOTH)
            tmp = Button(popup, text='Get verb inflections', command=lambda: do_inflection(pos = 'v'), width=17)
            tmp.grid(row=2, column=0, sticky=W, padx=(7, 0))
            tmp = Button(popup, text='Get noun inflections', command=lambda: do_inflection(pos = 'n'), width=17)
            tmp.grid(row=3, column=0, sticky=W, padx=(7, 0))  
            tmp = Button(popup, text='Get adjective forms', command=lambda: do_inflection(pos = 'a'), width=17)
            tmp.grid(row=4, column=0, sticky=W, padx=(7, 0))       
            #Button(text='Inflect as noun', command=lambda: do_inflection(pos = 'n')).grid()
            savebut = Button(popup, text='Store', command=store_wordlist, width=17)
            savebut.grid(row=6, column=0, sticky=W, padx=(7, 0))
            Label(popup, text='Previous wordlists', font=("Helvetica", 13, "bold")).grid(column=1, row=0, padx=15)
            other_custom_queries = Frame(popup, width=9, height=30)
            other_custom_queries.grid(row=1, column=1, padx=15)
            pwlscrbar = Scrollbar(other_custom_queries)
            pwlscrbar.pack(side=RIGHT, fill=Y)
            global cust_spec
            cust_spec = Listbox(other_custom_queries, selectmode = EXTENDED, height=24, relief = SUNKEN, bg='#F4F4F4',
                                        yscrollcommand=pwlscrbar.set, exportselection = False, width=20,
                                        font=("Courier New", 13))
            pwlscrbar.config(command=cust_spec.yview)
            cust_spec.pack()
            cust_spec.delete(0, END)
            
            def colour_the_custom_queries(*args):
                color_saved(cust_spec, colour1 = '#ccebc5', colour2 = '#fbb4ae', lists = True)

            cust_spec.bind('<<Modified>>', colour_the_custom_queries)
            for k, v in sorted(custom_special_dict.items()):
                cust_spec.insert(END, k)

            colour_the_custom_queries()

            def remove_this_custom_query():
                global cust_spec
                indexes = cust_spec.curselection()
                for index in indexes:
                    name = cust_spec.get(index)
                    del custom_special_dict[name]
                    cust_spec.delete(0, END)
                    for k, v in sorted(custom_special_dict.items()):
                        cust_spec.insert(END, k)
                color_saved(cust_spec, colour1 = '#ccebc5', colour2 = '#fbb4ae', lists = True)
                if len(indexes) == 1:
                    timestring('%s forgotten.' % name)
                else:
                    timestring('%d lists forgotten.' % len(indexes))

            def delete_this_custom_query():
                global cust_spec
                indexes = cust_spec.curselection()
                for index in indexes:
                    name = cust_spec.get(index)
                    if name in list(predict.keys()):
                        timestring("%s can't be permanently deleted." % name)
                        return
                    del custom_special_dict[name]
                    try:
                        del saved_special_dict[name]
                    except:
                        pass
                dump_custom_list_json()
                cust_spec.delete(0, END)
                for k, v in sorted(custom_special_dict.items()):
                    cust_spec.insert(END, k)
                color_saved(cust_spec, colour1 = '#ccebc5', colour2 = '#fbb4ae', lists = True)
                
                if len(indexes) == 1:
                    timestring('%s permanently deleted.' % name)
                else:
                    timestring('%d lists permanently deleted.' % len(indexes))

            def show_this_custom_query(*args):
                global cust_spec
                index = cust_spec.curselection()
                if len(index) > 1:
                    timestring("Can only show one list at a time.")
                    return
                name = cust_spec.get(index)
                tb.delete(1.0, END)
                for i in custom_special_dict[name]:
                    tb.insert(END, i + '\n')
                schemename.set(name)

            cust_spec.bind('<Return>', show_this_custom_query)

            def merge_this_custom_query(*args):
                global cust_spec
                indexes = cust_spec.curselection()
                names = [cust_spec.get(i) for i in indexes]
                tb.delete(1.0, END)
                for name in names:
                    for i in custom_special_dict[name]:
                        tb.insert(END, i + '\n')
                schemename.set('Merged')

            def add_custom_query_to_json():
                global cust_spec
                indexes = cust_spec.curselection()
                for index in indexes:
                    name = cust_spec.get(index)
                    saved_special_dict[name] = custom_special_dict[name]
                dump_custom_list_json()
                color_saved(cust_spec, colour1 = '#ccebc5', colour2 = '#fbb4ae', lists = True)
                
                if len(indexes) == 1:
                    timestring('%s saved to file.' % name)
                else:
                    timestring('%d lists saved to file.' % len(indexes))          
            
            Button(popup, text='View/edit', command=show_this_custom_query, width=17).grid(column=1, row=2, sticky=E, padx=(0, 7))
            Button(popup, text='Merge', command=merge_this_custom_query, width=17).grid(column=1, row=3, sticky=E, padx=(0, 7))
            svb = Button(popup, text='Save', command=add_custom_query_to_json, width=17)
            svb.grid(column=1, row=4, sticky=E, padx=(0, 7))
            if in_a_project.get() == 0:
                svb.config(state=DISABLED)
            else:
                svb.config(state=NORMAL)

            Button(popup, text='Remove', command=remove_this_custom_query, width=17).grid(column=1, row=5, sticky=E, padx=(0, 7))
            Button(popup, text='Delete', command=delete_this_custom_query, width=17).grid(column=1, row=6, sticky=E, padx=(0, 7))

            def have_unsaved_list():
                """finds out if there is an unsaved list"""
                global tb
                lst = [w.strip().lower() for w in tb.get(1.0, END).split()]
                if any(lst == l for l in list(custom_special_dict.values())):
                    return False
                else:
                    return True

            def quit_listing(*args):
                if have_unsaved_list():
                    should_continue = messagebox.askyesno("Unsaved data", 
                              "Unsaved list will be forgotten. Continue?")
                    if not should_continue:
                        return        
                popup.destroy()

            stopbut = Button(popup, text='Done', command=quit_listing)
            stopbut.grid(column=0, columnspan=2, row=7, pady=7)

        ##############    ##############     ##############     ##############     ############## 
        # COLSCHEMES #    # COLSCHEMES #     # COLSCHEMES #     # COLSCHEMES #     # COLSCHEMES # 
        ##############    ##############     ##############     ##############     ############## 

        # a place for the toplevel entry info
        entryboxes = OrderedDict()

        # fill it with null data
        for i in range(10):
            tmp = StringVar()
            tmp.set('')
            entryboxes[i] = tmp

        def codingschemer():
            try:
                global toplevel
                toplevel.destroy()
            except:
                pass

            from tkinter import Toplevel
            toplevel = Toplevel()
            toplevel.geometry('+1089+85')
            toplevel.title("Coding scheme")
            toplevel.wm_attributes('-topmost', 1)
            Label(toplevel, text='').grid(row=0, column=0, pady=2)
            def quit_coding(*args):
                toplevel.destroy()
            #Label(toplevel, text=('When concordancing, you can colour code lines using 0-9 keys. '\
            #                        'If you name the colours here, you can export or save the concordance lines with '\
            #                        'names attached.'), font=('Helvetica', 13, 'italic'), wraplength = 250, justify=LEFT).grid(row=0, column=0, columnspan=2)
            stopbut = Button(toplevel, text='Done', command=quit_coding)
            stopbut.grid(row=12, column=0, columnspan=2, pady=15)        
            for index, colour_index in enumerate(colourdict.keys()):
                Label(toplevel, text='Key: %d' % colour_index).grid(row=index + 1, column=0)
                fore = 'black'
                if colour_index == 9:
                    fore = 'white'
                tmp = Entry(toplevel, textvariable=entryboxes[index], bg=colourdict[colour_index], fg = fore)
                all_text_widgets.append(tmp)
                if index == 0:
                    tmp.focus_set()
                tmp.grid(row=index + 1, column=1, padx=10)

            toplevel.bind("<Return>", quit_coding)
            toplevel.bind("<Tab>", focus_next_window)

        # conc box needs to be defined up here
        fsize = IntVar()
        fsize.set(12)
        cfrm = Frame(tab4, height=565, width=1360)
        cfrm.grid(column=0, columnspan=60, row=0)
        cscrollbar = Scrollbar(cfrm)
        cscrollbarx = Scrollbar(cfrm, orient = HORIZONTAL)
        cscrollbar.pack(side=RIGHT, fill=Y)
        cscrollbarx.pack(side=BOTTOM, fill=X)
        conclistbox = Listbox(cfrm, yscrollcommand=cscrollbar.set, relief = SUNKEN, bg='#F4F4F4',
                              xscrollcommand=cscrollbarx.set, height=565, 
                              width=1050, font=('Courier New', fsize.get()), 
                              selectmode = EXTENDED)
        conclistbox.pack(fill=BOTH)
        cscrollbar.config(command=conclistbox.yview)
        cscrollbarx.config(command=conclistbox.xview)
        cfrm.pack_propagate(False)

        def dec_concfont(*args):
            size = fsize.get()
            fsize.set(size - 1)
            conclistbox.configure(font=('Courier New', fsize.get()))

        def inc_concfont(*args):
            size = fsize.get()
            fsize.set(size + 1)
            conclistbox.configure(font=('Courier New', fsize.get()))

        def select_all_conclines(*args):
            conclistbox.select_set(0, END)

        def color_conc(colour=0, *args):
            import re
            """color a conc line"""
            index_regex = re.compile(r'^([0-9]+)')
            col = colourdict[colour]
            if type(current_conc[0]) == str:
                return
            items = conclistbox.curselection()
            for index in items:
                conclistbox.itemconfig(index, {'bg':col})
                ind = int(re.search(index_regex, conclistbox.get(index)).group(1))
                itemcoldict[ind] = col
            conclistbox.selection_clear(0, END)

        conclistbox.bind("<BackSpace>", delete_conc_lines)
        conclistbox.bind("<Shift-KeyPress-BackSpace>", delete_reverse_conc_lines)
        conclistbox.bind("<Shift-KeyPress-Tab>", conc_sort)
        conclistbox.bind("<%s-minus>" % key, dec_concfont)
        conclistbox.bind("<%s-equal>" % key, inc_concfont)
        conclistbox.bind("<%s-a>" % key, select_all_conclines)
        conclistbox.bind("<%s-s>" % key, lambda x: concsave())
        conclistbox.bind("<%s-e>" % key, lambda x: conc_export())
        conclistbox.bind("<%s-t>" % key, lambda x: toggle_filenames())
        conclistbox.bind("<%s-A>" % key, select_all_conclines)
        conclistbox.bind("<%s-S>" % key, lambda x: concsave())
        conclistbox.bind("<%s-E>" % key, lambda x: conc_export())
        conclistbox.bind("<%s-T>" % key, lambda x: toggle_filenames())
        conclistbox.bind("0", lambda x: color_conc(colour=0))
        conclistbox.bind("1", lambda x: color_conc(colour=1))
        conclistbox.bind("2", lambda x: color_conc(colour=2))
        conclistbox.bind("3", lambda x: color_conc(colour=3))
        conclistbox.bind("4", lambda x: color_conc(colour=4))
        conclistbox.bind("5", lambda x: color_conc(colour=5))
        conclistbox.bind("6", lambda x: color_conc(colour=6))
        conclistbox.bind("7", lambda x: color_conc(colour=7))
        conclistbox.bind("8", lambda x: color_conc(colour=8))
        conclistbox.bind("9", lambda x: color_conc(colour=9))
        conclistbox.bind("0", lambda x: color_conc(colour=0))

        # these were 'generate' and 'edit', but they look ugly right now. the spaces are nice though.
        #lab = StringVar()
        #lab.set('Concordancing: %s' % os.path.basename(corpus_fullpath.get()))
        #Label(tab4, textvariable=lab, font=("Helvetica", 13, "bold")).grid(row=1, column=0, padx=20, pady=10, columnspan=5, sticky=W)
        #Label(tab4, text=' ', font=("Helvetica", 13, "bold")).grid(row=1, column=9, columnspan=2)

        conc_right_button_frame = Frame(tab4)
        conc_right_button_frame.grid(row=1, column=0, padx=(10,0), sticky='N', pady=(5, 0))

        # edit conc lines
        editbuts = Frame(conc_right_button_frame)
        editbuts.grid(row=1, column=0, columnspan=6, sticky='W')
        Button(editbuts, text='Delete selected', command=lambda: delete_conc_lines(), ).grid(row=0, column=0, sticky=W)
        Button(editbuts, text='Just selected', command=lambda: delete_reverse_conc_lines(), ).grid(row=0, column=1)
        #Button(editbuts, text='Sort', command=lambda: conc_sort()).grid(row=0, column=4)

        def toggle_filenames(*args):
            if type(current_conc[0]) == str:
                return
            data = current_conc[0]
            add_conc_lines_to_window(data)

        def make_df_matching_screen():
            import re
            if type(current_conc[0]) == str:
                return
            df = current_conc[0]

            if show_filenames.get() == 0:
                df = df.drop('f', axis = 1, errors = 'ignore')
            if show_themes.get() == 0:
                df = df.drop('t', axis = 1, errors = 'ignore')

            ix_to_keep = []
            lines = conclistbox.get(0, END)
            reg = re.compile(r'^\s*([0-9]+)')
            for l in lines:
                s = re.search(reg, l)
                ix_to_keep.append(int(s.group(1)))
            df = df.ix[ix_to_keep]
            df = df.reindex(ix_to_keep)
            return df

        def concsave():
            name = simpledialog.askstring('Concordance name', 'Choose a name for your concordance lines:')
            if not name or name == '':
                return
            df = make_df_matching_screen()
            all_conc[name] = df
            global conc_saved
            conc_saved = True
            refresh()

        def merge_conclines():
            toget = prev_conc_listbox.curselection()
            should_continue = True
            global conc_saved
            if not conc_saved:
                if type(current_conc[0]) != str and len(toget) > 1:
                    should_continue = messagebox.askyesno("Unsaved data", 
                              "Unsaved concordance lines will be forgotten. Continue?")
                else:
                    should_continue = True

            if not should_continue:
                return
            import pandas
            
            dfs = []
            if toget != ():
                if len(toget) < 2:
                    for item in toget:
                        nm = prev_conc_listbox.get(item)
                        dfs.append(all_conc[nm])
                    dfs.append(current_conc[0])
                    #timestring('Need multiple concordances to merge.' % name)
                    #return
                for item in toget:
                    nm = prev_conc_listbox.get(item)
                    dfs.append(all_conc[nm])
            else:
                
                timestring('Nothing selected to merge.' % name)
                return
            df = pandas.concat(dfs, ignore_index = True)
            should_drop = messagebox.askyesno("Remove duplicates", 
                              "Remove duplicate concordance lines?")
            if should_drop:
                df = df.drop_duplicates(subset = ['l', 'm', 'r'])
            add_conc_lines_to_window(df)

        def load_saved_conc():
            should_continue = True
            global conc_saved
            if not conc_saved:
                if type(current_conc[0]) != str:
                    should_continue = messagebox.askyesno("Unsaved data", 
                              "Unsaved concordance lines will be forgotten. Continue?")
                else:
                    should_continue = True
            if should_continue:
                toget = prev_conc_listbox.curselection()
                if len(toget) > 1:
                    timestring('Only one selection allowed for load.' % name)
                    return
                if toget != ():
                    nm = prev_conc_listbox.get(toget[0])
                    df = all_conc[nm]
                    add_conc_lines_to_window(df, loading = True, preserve_colour=False)
            else:
                return

        
        fourbuts = Frame(conc_right_button_frame)
        fourbuts.grid(row=1, column=6, columnspan=1, sticky='E')
        Button(fourbuts, text='Store as', command=concsave).grid(row=0, column=0)
        Button(fourbuts, text='Remove', command= lambda: remove_one_or_more(window = 'conc', kind = 'concordance')).grid(row=0, column=1)
        Button(fourbuts, text='Merge', command=merge_conclines).grid(row=0, column=2)
        Button(fourbuts, text='Load', command=load_saved_conc).grid(row=0, column=3)

        showbuts = Frame(conc_right_button_frame)
        showbuts.grid(row=0, column=0, columnspan=6, sticky='W')

        show_filenames = IntVar()
        fnbut = Checkbutton(showbuts, text='Filenames', variable=show_filenames, command=toggle_filenames)
        fnbut.grid(row=0, column=3)
        fnbut.select()
        show_filenames.trace('w', toggle_filenames)

        show_subcorpora = IntVar()
        sbcrp = Checkbutton(showbuts, text='Subcorpora', variable=show_subcorpora, command=toggle_filenames)
        sbcrp.grid(row=0, column=2)
        sbcrp.select()
        show_subcorpora.trace('w', toggle_filenames)

        show_themes = IntVar()
        themebut = Checkbutton(showbuts, text='Scheme', variable=show_themes, command=toggle_filenames)
        themebut.grid(row=0, column=1)
        #themebut.select()
        show_themes.trace('w', toggle_filenames)

        show_speaker = IntVar()
        showspkbut = Checkbutton(showbuts, text='Speakers', variable=show_speaker, command=toggle_filenames)
        showspkbut.grid(row=0, column=4)
        #showspkbut.select()
        show_speaker.trace('w', toggle_filenames)

        show_index = IntVar()
        indbut = Checkbutton(showbuts, text='Index', variable=show_index, command=toggle_filenames)
        indbut.grid(row=0, column=0)
        indbut.select()
        # disabling because turning index off can cause problems when sorting, etc
        indbut.config(state=DISABLED)
        show_index.trace('w', toggle_filenames)
        
        interrobut_conc = Button(showbuts, text='Re-run')
        interrobut_conc.config(command=lambda: runner(interrobut_conc, do_interrogation, conc = True), state=DISABLED)
        interrobut_conc.grid(row=0, column=6, padx=(5,0))

        def recalc(*args):
            import pandas as pd
            name = simpledialog.askstring('New name', 'Choose a name for the data:')
            if not name:
                return
            else:
                out = current_conc[0].calculate()

            all_interrogations[name] = out
            name_of_interro_spreadsheet.set(name)
            i_resultname.set('Interrogation results: %s' % str(name_of_interro_spreadsheet.get()))
            totals_as_df = pd.DataFrame(out.totals, dtype=object)
            if out.results is not None:
                update_spreadsheet(interro_results, out.results, height=340)
                subs = out.results.index
            else:
                update_spreadsheet(interro_results, df_to_show=None, height=340)
                subs = out.totals.index

            update_spreadsheet(interro_totals, totals_as_df, height=10)

            ind = list(all_interrogations.keys()).index(name_of_interro_spreadsheet.get())
            if ind == 0:
                prev.configure(state=DISABLED)
            else:
                prev.configure(state=NORMAL)

            if ind + 1 == len(list(all_interrogations.keys())):
                nex.configure(state=DISABLED)
            else:
                nex.configure(state=NORMAL)
            refresh()

            subc_listbox.delete(0, 'end')
            for e in list(subs):
                if e != 'tkintertable-order':
                    subc_listbox.insert(END, e)
                timestring('Calculation done. "%s" created.' % name)
                note.change_tab(1)

        recalc_but = Button(showbuts, text='Calculate', command=recalc)
        recalc_but.config(command=recalc, state=DISABLED)
        recalc_but.grid(row=0, column=7, padx=(5,0))

        win = StringVar()
        win.set('Window')
        wind_size = OptionMenu(editbuts, win, *tuple(('Window', '20', '30', '40', '50', '60', '70', '80', '90', '100')))
        wind_size.config(width=10)
        wind_size.grid(row=0, column=5)
        win.trace("w", conc_sort)

        # possible sort
        sort_vals = ('Index', 'Subcorpus', 'File', 'Speaker', 'Colour', 'Scheme', 'Random', 'L5', 'L4', 'L3', 'L2', 'L1', 'M1', 'M2', 'M-2', 'M-1', 'R1', 'R2', 'R3', 'R4', 'R5')
        sortval = StringVar()
        sortval.set('Sort')
        prev_sortval = ['None']
        srtkind = OptionMenu(editbuts, sortval, *sort_vals)
        srtkind.config(width=10)
        srtkind.grid(row=0, column=3)
        sortval.trace("w", conc_sort)

        # export to csv
        Button(editbuts, text='Export', command=lambda: conc_export()).grid(row=0, column=6)

        Label(conc_right_button_frame, text='Stored concordances', font=("Helvetica", 13, "bold")).grid(row=0, column=6, sticky=E, padx=(380,0))

        prev_conc = Frame(conc_right_button_frame)
        prev_conc.grid(row=0, column=7, rowspan = 3, columnspan=2, sticky=E, padx=(10,0), pady=(4,0))
        prevcbar = Scrollbar(prev_conc)
        prevcbar.pack(side=RIGHT, fill=Y)
        prev_conc_listbox = Listbox(prev_conc, selectmode = EXTENDED, width=20, height=4, relief = SUNKEN, bg='#F4F4F4',
                                    yscrollcommand=prevcbar.set, exportselection = False)
        prev_conc_listbox.pack()
        cscrollbar.config(command=prev_conc_listbox.yview)

        ##############     ##############     ##############     ##############     ############## 
        # MANAGE TAB #     # MANAGE TAB #     # MANAGE TAB #     # MANAGE 'TAB' #     # MANAGE TAB # 
        ##############     ##############     ##############     ##############     ############## 

        def make_new_project():
            import os
            from corpkit.other import new_project
            reset_everything()
            name = simpledialog.askstring('New project', 'Choose a name for your project:')
            if not name:
                return
            home = os.path.expanduser("~")
            docpath = os.path.join(home, 'Documents')
            if sys.platform == 'darwin':
                the_kwargs = {'message': 'Choose a directory in which to create your new project'}
            else:
                the_kwargs = {}
            fp = filedialog.askdirectory(title = 'New project location',
                                           initialdir = docpath,
                                           **the_kwargs)
            if not fp:
                return
            new_proj_basepath.set('New project: "%s"' % name)
            new_project(name = name, loc = fp, root=root)
            project_fullpath.set(os.path.join(fp, name))
            os.chdir(project_fullpath.get())
            image_fullpath.set(os.path.join(project_fullpath.get(), 'images'))
            savedinterro_fullpath.set(os.path.join(project_fullpath.get(), 'saved_interrogations'))
            conc_fullpath.set(os.path.join(project_fullpath.get(), 'saved_concordances'))
            corpora_fullpath.set(os.path.join(project_fullpath.get(), 'data'))
            exported_fullpath.set(os.path.join(project_fullpath.get(), 'exported'))
            log_fullpath.set(os.path.join(project_fullpath.get(), 'logs'))
            addbut.config(state=NORMAL)

            open_proj_basepath.set('Loaded: "%s"' % name)
            save_config()
            root.title("corpkit: %s" % os.path.basename(project_fullpath.get()))
            #load_project(path = os.path.join(fp, name))
            timestring('Project "%s" created.' % name)
            note.focus_on(tab0)
            #current_corpus.set('Select corpus')
            update_available_corpora()

        def get_saved_results(kind = 'interrogation', add_to = False):
            from corpkit.other import load_all_results
            if kind == 'interrogation':
                datad = savedinterro_fullpath.get()
            elif kind == 'concordance':
                datad = conc_fullpath.get()
            elif kind == 'image':
                datad = image_fullpath.get()
            if datad == '':
                timestring('No project loaded.')
            if kind == 'image':
                image_list = sorted([f for f in os.listdir(image_fullpath.get()) if f.endswith('.png')])
                for iname in image_list:
                    if iname.replace('.png', '') not in all_images:
                        all_images.append(iname.replace('.png', ''))
                if len(image_list) > 0:
                    nbut.config(state=NORMAL)
            else:
                if kind == 'interrogation':
                    r = load_all_results(data_dir=datad, root=root, note=note)
                else:
                    r = load_all_results(data_dir=datad, root=root, note=note)
                if r is not None:
                    for name, loaded in list(r.items()):
                        if kind == 'interrogation':
                            if type(loaded) == dict:
                                for subname, subloaded in list(loaded.items()):
                                    all_interrogations[name + '-' + subname] = subloaded
                            else:
                                all_interrogations[name] = loaded
                        else:
                            all_conc[name] = loaded
                    if len(list(all_interrogations.keys())) > 0:
                        nex.configure(state=NORMAL)
            refresh()
        
        def recentchange(*args):
            """if user clicks a recent project, open it"""
            if recent_project.get() != '':
                project_fullpath.set(recent_project.get())            
                load_project(path = project_fullpath.get())

        def projchange(*args):
            """if user changes projects, add to recent list and save prefs"""
            if project_fullpath.get() != '' and 'Contents/MacOS' not in project_fullpath.get():
                in_a_project.set(1)
                if project_fullpath.get() not in most_recent_projects:
                    most_recent_projects.append(project_fullpath.get())
                save_tool_prefs(printout = False)
                #update_available_corpora()
            else:
                in_a_project.set(0)

        # corpus path setter
        savedinterro_fullpath = StringVar()
        savedinterro_fullpath.set('')
        data_basepath = StringVar()
        data_basepath.set('Select data directory')
        in_a_project = IntVar()
        in_a_project.set(0)
        project_fullpath = StringVar()
        project_fullpath.set(rd)
        project_fullpath.trace("w", projchange)
        recent_project = StringVar()
        recent_project.set('')
        recent_project.trace("w", recentchange)
        conc_fullpath = StringVar()
        conc_fullpath.set('')
        exported_fullpath = StringVar()
        exported_fullpath.set('')  
        log_fullpath = StringVar()
        import os
        home = os.path.expanduser("~")
        try:
            os.makedirs(os.path.join(home, 'corpkit-logs'))
        except:
            pass
        log_fullpath.set(os.path.join(home, 'corpkit-logs'))    
        image_fullpath = StringVar()
        image_fullpath.set('')
        image_basepath = StringVar()
        image_basepath.set('Select image directory')
        corpora_fullpath = StringVar()
        corpora_fullpath.set('')

        def imagedir_modified(*args):
            import matplotlib
            matplotlib.rcParams['savefig.directory'] = image_fullpath.get()

        image_fullpath.trace("w", imagedir_modified)

        def data_getdir():
            import os
            fp = filedialog.askdirectory(title = 'Open data directory')
            if not fp:
                return
            savedinterro_fullpath.set(fp)
            data_basepath.set('Saved data: "%s"' % os.path.basename(fp))
            #sel_corpus_button.set('Selected corpus: "%s"' % os.path.basename(newc))
            #fs = sorted([d for d in os.listdir(fp) if os.path.isfile(os.path.join(fp, d))])
            timestring('Set data directory: %s' % os.path.basename(fp))

        def image_getdir(nodialog = False):
            import os
            fp = filedialog.askdirectory()
            if not fp:
                return
            image_fullpath.set(fp)
            image_basepath.set('Images: "%s"' % os.path.basename(fp))
            timestring('Set image directory: %s' % os.path.basename(fp))

        def save_one_or_more(kind = 'interrogation'):
            sel_vals = manage_listbox_vals
            if len(sel_vals) == 0:
                timestring('Nothing selected to save.')
                return
            from corpkit.other import save
            import os
            saved = 0
            existing = 0
            # for each filename selected
            for i in sel_vals:
                safename = urlify(i) + '.p'
                # make sure not already there
                if safename not in os.listdir(savedinterro_fullpath.get()):
                    if kind == 'interrogation':
                        savedata = all_interrogations[i]
                        savedata.query.pop('root', None)
                        savedata.query.pop('note', None)
                        save(savedata, safename, savedir = savedinterro_fullpath.get())
                    else:
                        savedata = all_conc[i]
                        try:
                            savedata.query.pop('root', None)
                            savedata.query.pop('note', None)
                        except:
                            pass
                        save(savedata, safename, savedir = conc_fullpath.get())
                    saved += 1
                else:
                    existing += 1
                    timestring('%s already exists in %s.' % (urlify(i), os.path.basename(savedinterro_fullpath.get())))
            if saved == 1 and existing == 0:
                timestring('%s saved.' % sel_vals[0])
            else:
                if existing == 0:
                    timestring('%d %ss saved.' % (len(sel_vals), kind))
                else:
                    timestring('%d %ss saved, %d already existed' % (saved, kind, existing))
            refresh()
            manage_callback()


        def remove_one_or_more(window=False, kind ='interrogation'):
            sel_vals = manage_listbox_vals
            if window is not False:
                toget = prev_conc_listbox.curselection()
                sel_vals = [prev_conc_listbox.get(toget)]
            if len(sel_vals) == 0:
                timestring('No interrogations selected.')
                return
            for i in sel_vals:
                try:
                    if kind == 'interrogation':
                        del all_interrogations[i]
                    else:
                        del all_conc[i]
                except:
                    pass
            if len(sel_vals) == 1:
                timestring('%s removed.' % sel_vals[0])
            else:
                timestring('%d interrogations removed.' % len(sel_vals))
            if kind == 'image':
                refresh_images()
            refresh()
            manage_callback()

        def del_one_or_more(kind = 'interrogation'):
            sel_vals = manage_listbox_vals
            ext = '.p'
            if kind == 'interrogation':
                p = savedinterro_fullpath.get()
            elif kind == 'image':
                p = image_fullpath.get()
                ext = '.png'
            else:
                p = conc_fullpath.get()
            if len(sel_vals) == 0:
                timestring('No interrogations selected.')
                return
            import os
            result = messagebox.askquestion("Are You Sure?", "Permanently delete the following files:\n\n    %s" % '\n    '.join(sel_vals), icon='warning')
            if result == 'yes':
                for i in sel_vals:
                    if kind == 'interrogation':
                        del all_interrogations[i]
                        os.remove(os.path.join(p, i + ext))
                    elif kind == 'concordance':
                        del all_conc[i]
                        os.remove(os.path.join(p, i + ext))
                    else:
                        all_images.remove(i)
                        os.remove(os.path.join(p, i + ext))
            if len(sel_vals) == 1:
                timestring('%s deleted.' % sel_vals[0])
            else:
                timestring('%d %ss deleted.' % (kind, len(sel_vals)))
            refresh()
            manage_callback()

        def urlify(s):
            "Turn title into filename"
            import re
            #s = s.lower()
            s = re.sub(r"[^\w\s-]", '', s)
            s = re.sub(r"\s+", '-', s)
            s = re.sub(r"-(textbf|emph|textsc|textit)", '-', s)
            return s

        def rename_one_or_more(kind = 'interrogation'):
            ext = '.p'
            sel_vals = manage_listbox_vals
            if kind == 'interrogation':
                p = savedinterro_fullpath.get()
            elif kind == 'image':
                p = image_fullpath.get()
                ext = '.png'
            else:
                p = conc_fullpath.get()
            if len(sel_vals) == 0:
                timestring('No items selected.')
                return
            import os
            permanently = True

            if permanently:
                perm_text='permanently '
            else:
                perm_text=''
            for i in sel_vals:
                answer = simpledialog.askstring('Rename', 'Choose a new name for "%s":' % i, initialvalue = i)
                if answer is None or answer == '':
                    return
                else:
                    if kind == 'interrogation':
                        all_interrogations[answer] = all_interrogations.pop(i)
                    elif kind == 'image':
                        ind = all_images.index(i)
                        all_images.remove(i)
                        all_images.insert(ind, answer)
                    else:
                        all_conc[answer] = all_conc.pop(i)
                if permanently:
                    oldf = os.path.join(p, i + ext)
                    if os.path.isfile(oldf):
                        newf = os.path.join(p, urlify(answer) + ext)
                        os.rename(oldf, newf)
                if kind == 'interrogation':
                    if name_of_interro_spreadsheet.get() == i:
                        name_of_interro_spreadsheet.set(answer)
                        i_resultname.set('Interrogation results: %s' % str(answer))
                        #update_spreadsheet(interro_results, all_interrogations[answer].results)
                    if name_of_o_ed_spread.get() == i:
                        name_of_o_ed_spread.set(answer)
                        #update_spreadsheet(o_editor_results, all_interrogations[answer].results)
                    if name_of_n_ed_spread.get() == i:
                        name_of_n_ed_spread.set(answer)
                        #update_spreadsheet(n_editor_results, all_interrogations[answer].results)
            
            if kind == 'image':
                refresh_images()

            if len(sel_vals) == 1:
                timestring('%s %srenamed as %s.' % (sel_vals[0], perm_text, answer))
            else:
                timestring('%d items %srenamed.' % (len(sel_vals), perm_text))
            refresh()
            manage_callback()

        def export_interrogation(kind = 'interrogation'):
            sel_vals = manage_listbox_vals
            """save dataframes and options to file"""
            import os
            import pandas

            fp = False

            for i in sel_vals:
                answer = simpledialog.askstring('Export data', 'Choose a save name for "%s":' % i, initialvalue = i)
                if answer is None or answer == '':
                    return
                if kind != 'interrogation':
                    conc_export(data = i)
                else:  
                    data = all_interrogations[i]
                    keys = list(data.__dict__.keys())
                    if in_a_project.get() == 0:
                        if sys.platform == 'darwin':
                            the_kwargs = {'message': 'Choose save directory for exported interrogation'}
                        else:
                            the_kwargs = {}
                        fp = filedialog.askdirectory(title = 'Choose save directory', **the_kwargs)
                        if fp == '':
                            return
                    else:
                        fp = project_fullpath.get()
                    os.makedirs(os.path.join(exported_fullpath.get(), answer))
                    for k in keys:
                        if k == 'results':
                            if data.results is not None:
                                tkdrop = data.results.drop('tkintertable-order', errors = 'ignore')
                                tkdrop.to_csv(os.path.join(exported_fullpath.get(), answer, 'results.csv'), sep ='\t', encoding = 'utf-8')
                        if k == 'totals':
                            if data.totals is not None:
                                tkdrop = data.totals.drop('tkintertable-order', errors = 'ignore')
                                tkdrop.to_csv(os.path.join(exported_fullpath.get(), answer, 'totals.csv'), sep ='\t', encoding = 'utf-8')
                        if k == 'query':
                            if getattr(data, 'query', None):
                                pandas.DataFrame(list(data.query.values()), index = list(data.query.keys())).to_csv(os.path.join(exported_fullpath.get(), answer, 'query.csv'), sep ='\t', encoding = 'utf-8')
                        #if k == 'table':
                        #    if 'table' in list(data.__dict__.keys()) and data.table:
                        #        pandas.DataFrame(list(data.query.values()), index = list(data.query.keys())).to_csv(os.path.join(exported_fullpath.get(), answer, 'table.csv'), sep ='\t', encoding = 'utf-8')
            if fp:
                timestring('Results exported to %s' % (os.path.join(os.path.basename(exported_fullpath.get()), answer)))

        def reset_everything():
            # result names
            i_resultname.set('Interrogation results:')
            resultname.set('Results to edit:')
            editoname.set('Edited results:')
            savedplot.set('View saved images: ')
            open_proj_basepath.set('Open project')
            corpus_fullpath.set('')
            current_corpus.set('')
            corpora_fullpath.set('')
            project_fullpath.set(rd)
            special_queries.set('Off')

            # spreadsheets
            update_spreadsheet(interro_results, df_to_show=None, height=340)
            update_spreadsheet(interro_totals, df_to_show=None, height=10)
            update_spreadsheet(o_editor_results, df_to_show=None, height=140)
            update_spreadsheet(o_editor_totals, df_to_show=None, height=10)
            update_spreadsheet(n_editor_results, df_to_show=None, height=140)
            update_spreadsheet(n_editor_totals, df_to_show=None, height=10)

            # interrogations
            for e in list(all_interrogations.keys()):
                del all_interrogations[e]
            # another way:
            all_interrogations.clear()
            # subcorpora listbox
            subc_listbox.delete(0, END)
            subc_listbox_build.delete(0, END)
            # concordance
            conclistbox.delete(0, END)
            # every interrogation
            #every_interro_listbox.delete(0, END)
            # every conc
            #ev_conc_listbox.delete(0, END)
            prev_conc_listbox.delete(0, END)
            # images
            #every_image_listbox.delete(0, END)
            every_interrogation['menu'].delete(0, 'end')
            pick_subcorpora['menu'].delete(0, 'end')
            # speaker listboxes
            speaker_listbox.delete(0, 'end')
            #speaker_listbox_conc.delete(0, 'end')
            # keys
            for e in list(all_conc.keys()):
                del all_conc[e]
            for e in all_images:
                all_images.remove(e)
            #update_available_corpora(delete = True)
            refresh()

        def convert_speakdict_to_string(dictionary):
            """turn speaker info dict into a string for configparser"""
            if len(list(dictionary.keys())) == 0:
                return None
            out = []
            for k, v in list(dictionary.items()):
                out.append('%s:%s' % (k, ','.join([i.replace(',', '').replace(':', '').replace(';', '') for i in v])))
            return ';'.join(out)

        def parse_speakdict(string):
            """turn configparser's speaker info back into a dict"""
            if string is None:
                return {}
            redict = {}
            corps = string.split(';')
            for c in corps:
                try:
                    name, vals = c.split(':')
                except ValueError:
                    continue
                vs = vals.split(',')
                redict[name] = vs
            return redict

        def load_custom_list_json():
            import json
            f = os.path.join(project_fullpath.get(), 'custom_wordlists.txt')
            if os.path.isfile(f):
                data = json.loads(open(f).read())
                for k, v in data.items():
                    if k not in list(custom_special_dict.keys()):
                        custom_special_dict[k] = v
                    if k not in list(saved_special_dict.keys()):
                        saved_special_dict[k] = v

        def dump_custom_list_json():
            import json
            f = os.path.join(project_fullpath.get(), 'custom_wordlists.txt')
            with open(f, 'w') as fo:
                fo.write(json.dumps(saved_special_dict))

        def load_config():
            """use configparser to get project settings"""
            import os
            try:
                import configparser
            except ImportError:
                import ConfigParser as configparser
            Config = configparser.ConfigParser()
            f = os.path.join(project_fullpath.get(), 'settings.ini')
            Config.read(f)

            plot_style.set(conmap(Config, "Visualise")['plot style'])
            texuse.set(conmap(Config, "Visualise")['use tex'])
            x_axis_l.set(conmap(Config, "Visualise")['x axis title'])
            chart_cols.set(conmap(Config, "Visualise")['colour scheme'])
            rel_corpuspath = conmap(Config, "Interrogate")['corpus path']
            files_as_subcorpora.set(conmap(Config, "Interrogate")['treat files as subcorpora'])
            corpa = os.path.join(project_fullpath.get(), rel_corpuspath)
            #corpus_fullpath.set(corpa)
            current_corpus.set(os.path.basename(corpa))
            spk = conmap(Config, "Interrogate")['speakers']
            corpora_speakers = parse_speakdict(spk)
            for i, v in list(corpora_speakers.items()):
                corpus_names_and_speakers[i] = v
            fsize.set(conmap(Config, "Concordance")['font size'])
            # window setting causes conc_sort to run, causing problems.
            #win.set(conmap(Config, "Concordance")['window'])
            kind_of_dep.set(conmap(Config, 'Interrogate')['dependency type'])
            #conc_kind_of_dep.set(conmap(Config, "Concordance")['dependency type'])
            cods = conmap(Config, "Concordance")['coding scheme']
            if cods is None:
                for _, val in list(entryboxes.items()):
                    val.set('')
            else:
                codsep = cods.split(',')
                for (box, val), cod in zip(list(entryboxes.items()), codsep):
                    val.set(cod)
            if corpus_fullpath.get():
                subdrs = [d for d in os.listdir(corpus_fullpath.get()) if os.path.isdir(os.path.join(corpus_fullpath.get(),d))]
            else:
                subdrs = []
            if len(subdrs) == 0:
                charttype.set('bar')
            refresh()

        def load_project(path=False):
            import os
            if path is False:
                if sys.platform == 'darwin':
                    the_kwargs = {'message': 'Choose project directory'}
                else:
                    the_kwargs = {}
                fp = filedialog.askdirectory(title='Open project',
                                           **the_kwargs)
            else:
                fp = path
            if not fp or fp == '':
                return
            reset_everything()

            image_fullpath.set(os.path.join(fp, 'images'))
            savedinterro_fullpath.set(os.path.join(fp, 'saved_interrogations'))
            conc_fullpath.set(os.path.join(fp, 'saved_concordances'))
            exported_fullpath.set(os.path.join(fp, 'exported'))
            corpora_fullpath.set(os.path.join(fp, 'data'))
            log_fullpath.set(os.path.join(fp, 'logs'))

            if not os.path.isdir(savedinterro_fullpath.get()):
                timestring('Selected folder does not contain corpkit project.')    
                return    

            project_fullpath.set(fp)

            f = os.path.join(project_fullpath.get(), 'settings.ini')
            if os.path.isfile(f):
                load_config()

            os.chdir(fp)
            list_of_corpora = update_available_corpora()
            addbut.config(state=NORMAL) 
            
            get_saved_results(kind='interrogation')
            get_saved_results(kind='concordance')
            get_saved_results(kind='image')
            open_proj_basepath.set('Loaded: "%s"' % os.path.basename(fp))

            # reset tool:
            root.title("corpkit: %s" % os.path.basename(fp))

            #if corpus_fullpath.get() == '':
                # check if there are already (parsed) corpora
            
            if not current_corpus.get():
                parsed_corp = [d for d in list_of_corpora if d.endswith('-parsed')]
                # select 
                first = False
                if len(parsed_corp) > 0:
                    first = parsed_corp[0]
                else:
                    if len(list_of_corpora) > 0:
                        first = list_of_corpora[0]
                    else:
                        first = False
                if first:
                    corpus_fullpath.set(os.path.join(corpora_fullpath.get(), first))
                    current_corpus.set(first)
                else:
                    corpus_fullpath.set('')
                    # no corpora, so go to build...
                    note.focus_on(tab0)
                #else:
                #    current_corpus.set(os.path.basename(corpus_fullpath.get()))
                
            corpus_name = os.path.basename(corpus_fullpath.get())
            current_corpus.set(corpus_name)

            if corpus_fullpath.get() != '':
                subdrs = sorted([d for d in os.listdir(corpus_fullpath.get()) if os.path.isdir(os.path.join(corpus_fullpath.get(),d))])
            else:
                subdrs = []       

            #lab.set('Concordancing: %s' % corpus_name)
            pick_subcorpora['menu'].delete(0, 'end')

            if len(subdrs) > 0:
                pick_subcorpora['menu'].add_command(label='all', command=_setit(subc_pick, 'all'))
                pick_subcorpora.config(state=NORMAL)
                for choice in subdrs:
                    pick_subcorpora['menu'].add_command(label=choice, command=_setit(subc_pick, choice))
            else:
                pick_subcorpora.config(state=NORMAL)
                pick_subcorpora['menu'].add_command(label='None', command=_setit(subc_pick, 'None'))
                pick_subcorpora.config(state=DISABLED)
            timestring('Project "%s" opened.' % os.path.basename(fp))
            note.progvar.set(0)
            
            if corpus_name in list(corpus_names_and_speakers.keys()):
                togglespeaker()
                speakcheck.config(state=NORMAL)
            else:
                speakcheck.config(state=DISABLED)

            load_custom_list_json()

        def view_query(kind = False):
            if len(manage_listbox_vals) == 0:
                return
            if len(manage_listbox_vals) > 1:
                timestring('Can only view one interrogation at a time.')
                return

            global frame_to_the_right
            frame_to_the_right = Frame(manage_pop)
            frame_to_the_right.grid(column=2, row=0, rowspan = 6)

            Label(frame_to_the_right, text='Query information', font=("Helvetica", 13, "bold")).grid(sticky=W, row=0, column=0, padx=(10,0))
            mlb = Table(frame_to_the_right, ['Option', 'Value'],
                      column_weights=[1, 1], height=70, width=30)
            mlb.grid(sticky=N, column=0, row=1)
            for i in mlb._mlb.listboxes:
                i.config(height=29)

            mlb.columnconfig('Option', background='#afa')
            mlb.columnconfig('Value', background='#efe')

            q_dict = dict(all_interrogations[manage_listbox_vals[0]].query)
            mlb.clear()
            #show_query_vals.delete(0, 'end')
            flipped_trans = {v: k for k, v in list(transdict.items())}
            
            # flip options dict, make 'kind of search'
            if 'option' in list(q_dict.keys()):
                flipped_opt = {}
                for nm, lst in list(option_dict.items()):
                    for i in lst:
                        flipped_opt[i] = nm
                # not very robust, will break when more added
                try:
                    the_opt = flipped_opt[flipped_trans[q_dict['option']]]
                except KeyError:
                    the_opt = 'Stats'
                q_dict['kind_of_search'] = the_opt

            for d in ['dataframe1', 'dataframe2']:
                try:
                    del q_dict[d]
                except KeyError:
                    pass

            for i, k in enumerate(sorted(q_dict.keys())):
                v = q_dict[k]
                if k == 'option':
                    v = flipped_trans[v]
                try:
                    if v is False:
                        v = 'False'
                    if v == 0:
                        v = 'False'
                    if v is True:
                        v = 'True'
                    # could be bad with threshold etc
                    if v == 1:
                        v = True
                except:
                    pass
                mlb.append([k, v])

            if 'query' in list(q_dict.keys()):
                qubox = Text(frame_to_the_right, font=("Courier New", 14), relief = SUNKEN, wrap = WORD, width=40, height=5, undo = True)
                qubox.grid(column=0, row=2, rowspan = 1, padx=(10,0))
                qubox.delete(1.0, END)
                qubox.insert(END, q_dict['query'])
                manage_box['qubox'] = qubox
                bind_textfuncts_to_widgets([qubox])
            else:
                try:
                    manage_box['qubox'].destroy()
                except:
                    pass

        manage_listbox_vals = []
        def onselect_manage(evt):
            # remove old vals
            for i in manage_listbox_vals:
                manage_listbox_vals.pop()
            wx = evt.widget
            indices = wx.curselection()
            for index in indices:
                value = wx.get(index)
                if value not in manage_listbox_vals:
                    manage_listbox_vals.append(value)

        new_proj_basepath = StringVar()
        new_proj_basepath.set('New project')
        open_proj_basepath = StringVar()
        open_proj_basepath.set('Open project')

        the_current_kind = StringVar()

        def manage_popup():
            from tkinter import Toplevel
            global manage_pop
            manage_pop = Toplevel()
            manage_pop.geometry('+400+40')
            manage_pop.title("Manage data: %s" % os.path.basename(project_fullpath.get()))
            manage_pop.wm_attributes('-topmost', 1)

            manage_what = StringVar()
            manage_what.set('Manage: ')
            #Label(manage_pop, textvariable=manage_what).grid(row=0, column=0, sticky='W', padx=(5, 0))

            manag_frame = Frame(manage_pop, height=30)
            manag_frame.grid(column=0, row=1, rowspan = 1, columnspan=2, sticky='NW', padx=10)
            manage_scroll = Scrollbar(manag_frame)
            manage_scroll.pack(side=RIGHT, fill=Y)
            manage_listbox = Listbox(manag_frame, selectmode = SINGLE, height=30, width=30, relief = SUNKEN, bg='#F4F4F4',
                                            yscrollcommand=manage_scroll.set, exportselection=False)
            manage_listbox.pack(fill=BOTH)
            manage_listbox.select_set(0)
            manage_scroll.config(command=manage_listbox.yview)   
            xx = manage_listbox.bind('<<ListboxSelect>>', onselect_manage)
            # default: w option
            manage_listbox.select_set(0)
            the_current_kind.set('interrogation')
            #gtsv = StringVar()
            #gtsv.set('Get saved')    
            #getbut = Button(manage_pop, textvariable=gtsv, command=lambda: get_saved_results(), width=22)
            #getbut.grid(row=2, column=0, columnspan=2)

            manage_type = StringVar()
            manage_type.set('Interrogations')

            #Label(manage_pop, text='Save selected: ').grid(sticky=E, row=6, column=1)
            savebut = Button(manage_pop, text='Save', command=lambda: save_one_or_more(kind = the_current_kind.get()))
            savebut.grid(padx=15, sticky=W, column=0, row=3)
            viewbut = Button(manage_pop, text='View', command=lambda: view_query(kind = the_current_kind.get()))
            viewbut.grid(padx=15, sticky=W, column=0, row=4)
            renamebut = Button(manage_pop, text='Rename', command=lambda: rename_one_or_more(kind = the_current_kind.get()))
            renamebut.grid(padx=15, sticky=W, column=0, row=5)

            #Checkbutton(manage_pop, text="Permanently", variable=perm, onvalue = True, offvalue = False).grid(column=1, row=16, padx=15, sticky=W)
            exportbut = Button(manage_pop, text='Export', command=lambda: export_interrogation(kind = the_current_kind.get()))
            exportbut.grid(padx=15, sticky=E, column=1, row=3)
            #Label(manage_pop, text='Remove selected: '()).grid(padx=15, sticky=W, row=4, column=0)
            removebut = Button(manage_pop, text='Remove', command= lambda: remove_one_or_more(kind = the_current_kind.get()))
            removebut.grid(padx=15, sticky=E, column=1, row=4)
            #Label(manage_pop, text='Delete selected: '()).grid(padx=15, sticky=E, row=5, column=1)
            deletebut = Button(manage_pop, text='Delete', command=lambda: del_one_or_more(kind = the_current_kind.get()))
            deletebut.grid(padx=15, sticky=E, column=1, row=5)

            to_manage = OptionMenu(manage_pop, manage_type, *tuple(('Interrogations', 'Concordances', 'Images')))
            to_manage.config(width=32, justify=CENTER)
            to_manage.grid(row=0, column=0, columnspan=2)

            def managed(*args):
                #vals = [i.get() for i in butvar.values() if i.get() is not False and i.get() != 0 and i.get() != '0']
                #vals = sorted(vals, key=lambda x:orders[x])
                #the_opts = ','.join(vals)]
                manage_pop.destroy()
                try:
                    del manage_callback
                except:
                    pass

            global manage_callback
            def manage_callback(*args):
                import os
                """show correct listbox, enable disable buttons below"""
                # set text
                #manage_what.set('Manage %s' % manage_type.get().lower())
                #gtsv.set('Get saved %s' % manage_type.get().lower())
                # set correct action for buttons
                the_current_kind.set(manage_type.get().lower().rstrip('s'))
                #get_saved_results(kind = the_current_kind.get())
                # enable all buttons
                #getbut.config(state=NORMAL)
                #try:
                savebut.config(state=NORMAL)
                viewbut.config(state=NORMAL)
                renamebut.config(state=NORMAL)
                exportbut.config(state=NORMAL)
                removebut.config(state=NORMAL)
                deletebut.config(state=NORMAL)
                manage_listbox.delete(0, 'end')
                if the_current_kind.get() == 'interrogation':
                    the_path = savedinterro_fullpath.get()
                    the_ext = '.p'
                    list_of_entries = list(all_interrogations.keys())
                elif the_current_kind.get() == 'concordance':
                    the_path = conc_fullpath.get()
                    the_ext = '.p'
                    list_of_entries = list(all_conc.keys())
                    viewbut.config(state=DISABLED)
                    try:
                        frame_to_the_right.destroy()
                    except:
                        pass
                elif the_current_kind.get() == 'image':
                    the_path = image_fullpath.get()
                    the_ext = '.png'
                    refresh_images()
                    list_of_entries = all_images
                    viewbut.config(state=DISABLED)
                    savebut.config(state=DISABLED)
                    exportbut.config(state=DISABLED)
                    removebut.config(state=DISABLED)
                    try:
                        frame_to_the_right.destroy()
                    except:
                        pass
                for datum in list_of_entries:
                    manage_listbox.insert(END, datum)
                color_saved(manage_listbox, the_path, '#ccebc5', '#fbb4ae', ext = the_ext)

            manage_type.trace("w", manage_callback)

            manage_type.set('Interrogations')

        ##############     ##############     ##############     ##############     ############## 
        # BUILD TAB  #     # BUILD TAB  #     # BUILD TAB  #     # BUILD TAB  #     # BUILD TAB  # 
        ##############     ##############     ##############     ##############     ############## 
        
        from corpkit.build import download_large_file, extract_cnlp, get_corpus_filepaths, \
            check_jdk, parse_corpus, move_parsed_files, corenlp_exists

        def create_tokenised_text():
            from corpkit.corpus import Corpus
            note.progvar.set(0)
            #tokbut.config(state=DISABLED)
            #tokbut = Button(tab0, textvariable=tokenise_button_text, command=ignore, width=33)
            #tokbut.grid(row=6, column=0, sticky=W)
            unparsed_corpus_path = corpus_fullpath.get()
            if speakseg.get():
                timestring('Speaker segmentation has no effect when tokenising corpus.')
                #unparsed_corpus_path = unparsed_corpus_path + '-stripped'
            filelist = get_corpus_filepaths(project_fullpath.get(), unparsed_corpus_path)
            corp = Corpus(unparsed_corpus_path)
            parsed = corp.tokenise(root=root, 
                                  stdout = sys.stdout, 
                                  note=note, 
                                  only_tokenise = True,
                                  nltk_data_path = nltk_data_path)
            #corpus_fullpath.set(outdir)
            outdir = parsed.path
            current_corpus.set(parsed.name)
            subdrs = [d for d in os.listdir(corpus_fullpath.get()) if os.path.isdir(os.path.join(corpus_fullpath.get(),d))]
            if len(subdrs) == 0:
                charttype.set('bar')
            #basepath.set(os.path.basename(outdir))
            #if len([f for f in os.listdir(outdir) if f.endswith('.p')]) > 0:
            timestring('Corpus parsed and ready to interrogate: "%s"' % os.path.basename(outdir))
            #else:
                #timestring('Error: no files created in "%s"' % os.path.basename(outdir))
            update_available_corpora()

        def create_parsed_corpus():
            import os
            import re
            import corpkit
            from corpkit.corpus import Corpus
            from corpkit.process import get_corenlp_path

            parser_options()
            root.wait_window(poptions)

            unparsed_corpus_path = corpus_fullpath.get()
            unparsed = Corpus(unparsed_corpus_path)
            note.progvar.set(0)
            unparsed_corpus_path = corpus_fullpath.get()
            corenlppath.set(get_corenlp_path(corenlppath.get()))
            if not corenlppath.get() or corenlppath.get() == 'None':
                downstall_nlp = messagebox.askyesno("CoreNLP not found.", 
                              "CoreNLP parser not found. Download/install it?")
                if not downstall_nlp:
                    timestring('Cannot parse data without Stanford CoreNLP.')
                    return
            jdk = check_jdk()
            if jdk is False:
                downstall_jdk = messagebox.askyesno("Java JDK", "You need Java JDK 1.8 to use CoreNLP.\n\nHit 'yes' to open web browser at download link. Once installed, corpkit should resume automatically")
                if downstall_jdk:
                    import webbrowser
                    webbrowser.open_new('http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html')
                    import time
                    timestring('Waiting for Java JDK 1.8 installation to complete.')
                    while jdk is False:
                        jdk = check_jdk()
                        timestring('Waiting for Java JDK 1.8 installation to complete.')
                        time.sleep(5)
                else:
                    timestring('Cannot parse data without Java JDK 1.8.')
                    return

            parsed = unparsed.parse(speaker_segmentation=speakseg.get(),
                                    proj_path=project_fullpath.get(),
                                    copula_head=True,
                                    multiprocess=False,
                                    corenlppath=corenlppath.get(),
                                    operations=parser_opts.get(),
                                    root=root, 
                                    stdout=sys.stdout, 
                                    note=note,
                                    memory_mb=parser_memory.get()
                                   )
            if not parsed:
                print('Error during parsing.')

            sys.stdout = note.redir
            current_corpus.set(parsed.name)

            subdrs = [d for d in os.listdir(corpus_fullpath.get()) if \
                      os.path.isdir(os.path.join(corpus_fullpath.get(), d))]
            if len(subdrs) == 0:
                charttype.set('bar')

            update_available_corpora()
            timestring('Corpus parsed and ready to interrogate: "%s"' % parsed.name)

        parse_button_text=StringVar()
        parse_button_text.set('Create parsed corpus')

        tokenise_button_text=StringVar()
        tokenise_button_text.set('Create tokenised corpus')

        path_to_new_unparsed_corpus = StringVar()
        path_to_new_unparsed_corpus.set('')

        add_corpus = StringVar()
        add_corpus.set('')
        add_corpus_button = StringVar()
        add_corpus_button.set('Add corpus%s' % add_corpus.get())

        selected_corpus_has_no_subcorpora = IntVar()
        selected_corpus_has_no_subcorpora.set(0)

        def add_subcorpora_to_build_box(path_to_corpus):
            import os
            subc_listbox_build.configure(state=NORMAL)
            subc_listbox_build.delete(0, 'end')
            sub_corpora = [d for d in os.listdir(path_to_corpus) if os.path.isdir(os.path.join(path_to_corpus, d))]
            if len(sub_corpora) == 0:
                selected_corpus_has_no_subcorpora.set(1)
                subc_listbox_build.bind('<<Modified>>', onselect_subc_build)
                subc_listbox_build.insert(END, 'No subcorpora found.')
                subc_listbox_build.configure(state=DISABLED)
            else:
                selected_corpus_has_no_subcorpora.set(0)
                for e in sub_corpora:
                    subc_listbox_build.insert(END, e)
            onselect_subc_build()

        def select_corpus():
            """selects corpus for viewing/parsing
            ---not used anymore"""
            from os.path import join as pjoin
            from os.path import basename as bn
            #parse_button_text.set('Parse: "%s"' % bn(unparsed_corpus_path))
            tokenise_button_text.set('Tokenise: "%s"' % bn(unparsed_corpus_path))
            path_to_new_unparsed_corpus.set(unparsed_corpus_path)
            #add_corpus_button.set('Added: %s' % bn(unparsed_corpus_path))
            where_to_put_corpus = pjoin(project_fullpath.get(), 'data')       
            sel_corpus.set(unparsed_corpus_path)
            #sel_corpus_button.set('Selected: "%s"' % bn(unparsed_corpus_path))
            parse_button_text.set('Parse: "%s"' % bn(unparsed_corpus_path))
            add_subcorpora_to_build_box(unparsed_corpus_path)
            timestring('Selected corpus: "%s"' % bn(unparsed_corpus_path))

        def getcorpus():
            """copy unparsed texts to project folder"""
            import shutil
            import os
            from corpkit.process import saferead
            home = os.path.expanduser("~")
            docpath = os.path.join(home, 'Documents')
            if sys.platform == 'darwin':
                the_kwargs = {'message': 'Select your corpus of unparsed text files.'}
            else:
                the_kwargs = {}
            fp = filedialog.askdirectory(title = 'Path to unparsed corpus',
                                           initialdir = docpath,
                                           **the_kwargs)
            where_to_put_corpus = os.path.join(project_fullpath.get(), 'data')
            newc = os.path.join(where_to_put_corpus, os.path.basename(fp))
            try:
                shutil.copytree(fp, newc)
                timestring('Corpus copied to project folder.')
            except OSError:
                if os.path.basename(fp) == '':
                    return
                timestring('"%s" already exists in project.' % os.path.basename(fp)) 
                return
            from corpkit.build import folderise, can_folderise
            if can_folderise(newc):
                do_folderise = messagebox.askyesno("No subcorpora found", 
                              "Your corpus contains multiple files, but no subfolders. " \
                              "Would you like to treat each file as a subcorpus?")
                if do_folderise:
                    folderise(newc)
                    timestring('Turned files into subcorpora.')
            # encode and rename files
            for (rootdir, d, fs) in os.walk(newc):
                for f in fs:
                    fpath = os.path.join(rootdir, f)
                    data, enc = saferead(fpath)
                    with open(fpath, "w") as f:
                        f.write(data.encode('utf-8', errors='ignore'))
                    # rename file
                    #dname = '-' + os.path.basename(rootdir)
                    #newname = fpath.replace('.txt', dname + '.txt')
                    #shutil.move(fpath, newname)
            path_to_new_unparsed_corpus.set(newc)
            add_corpus_button.set('Added: "%s"' % os.path.basename(fp))
            current_corpus.set(os.path.basename(fp))
            #sel_corpus.set(newc)
            #sel_corpus_button.set('Selected corpus: "%s"' % os.path.basename(newc))
            timestring('Corpus copied to project folder.')
            parse_button_text.set('Parse: %s' % os.path.basename(newc))
            tokenise_button_text.set('Tokenise: "%s"' % os.path.basename(newc))
            add_subcorpora_to_build_box(newc)
            update_available_corpora()
            timestring('Selected corpus for viewing/parsing: "%s"' % os.path.basename(newc))
    
        Label(tab0, text='Project', font=("Helvetica", 13, "bold")).grid(sticky=W, row=0, column=0)
        #Label(tab0, text='New project', font=("Helvetica", 13, "bold")).grid(sticky=W, row=0, column=0)
        Button(tab0, textvariable=new_proj_basepath, command=make_new_project, width=24).grid(row=1, column=0, sticky=W)
        #Label(tab0, text='Open project: ').grid(row=2, column=0, sticky=W)
        Button(tab0, textvariable=open_proj_basepath, command=load_project, width=24).grid(row=2, column=0, sticky=W)
        #Label(tab0, text='Add corpus to project: ').grid(row=4, column=0, sticky=W)
        addbut = Button(tab0, textvariable=add_corpus_button, width=24, state=DISABLED)
        addbut.grid(row=3, column=0, sticky=W)
        addbut.config(command=lambda: runner(addbut, getcorpus))
        #Label(tab0, text='Corpus to parse: ').grid(row=6, column=0, sticky=W)
        #Button(tab0, textvariable=sel_corpus_button, command=select_corpus, width=24).grid(row=4, column=0, sticky=W)
        #Label(tab0, text='Parse: ').grid(row=8, column=0, sticky=W)
        #speakcheck_build = Checkbutton(tab0, text="Speaker segmentation", variable=speakseg, state=DISABLED)
        #speakcheck_build.grid(column=0, row=5, sticky=W)
        
        parsebut = Button(tab0, textvariable=parse_button_text, width=24, state=DISABLED)
        parsebut.grid(row=5, column=0, sticky=W)
        parsebut.config(command=lambda: runner(parsebut, create_parsed_corpus))
        #Label(tab0, text='Parse: ').grid(row=8, column=0, sticky=W)
        tokbut = Button(tab0, textvariable=tokenise_button_text, width=24, state=DISABLED)
        tokbut.grid(row=6, column=0, sticky=W)
        tokbut.config(command=lambda: runner(tokbut, create_tokenised_text))

        def onselect_subc_build(evt = False):
            """get selected subcorpus, delete editor, show files in subcorpus"""
            import os
            if evt:
                # should only be one
                for i in subc_sel_vals_build:
                    subc_sel_vals_build.pop()
                wx = evt.widget
                indices = wx.curselection()
                for index in indices:
                    value = wx.get(index)
                    if value not in subc_sel_vals_build:
                        subc_sel_vals_build.append(value)
            # return for false click
            if len(subc_sel_vals_build) == 0 and selected_corpus_has_no_subcorpora.get() == 0:
                return

            # destroy editor and canvas if possible
            for ob in list(buildbits.values()):
                try:
                    ob.destroy()
                except:
                    pass

            f_view.configure(state=NORMAL)
            f_view.delete(0, 'end')
            newp = path_to_new_unparsed_corpus.get()
            if selected_corpus_has_no_subcorpora.get() == 0:
                newsub = os.path.join(newp, subc_sel_vals_build[0])
            else:
                newsub = newp
            fs = [f for f in os.listdir(newsub) if f.endswith('.txt') or f.endswith('.xml') or f.endswith('.p')]
            for e in fs:
                f_view.insert(END, e)
            if selected_corpus_has_no_subcorpora.get() == 0:      
                f_in_s.set('Files in subcorpus: %s' % subc_sel_vals_build[0])
            else:
                f_in_s.set('Files in corpus: %s' % os.path.basename(path_to_new_unparsed_corpus.get()))

        # a listbox of subcorpora
        Label(tab0, text='Subcorpora', font=("Helvetica", 13, "bold")).grid(row=7, column=0, sticky=W)

        build_sub_f = Frame(tab0, width=24, height=24)
        build_sub_f.grid(row=8, column=0, sticky=W, rowspan = 2, padx=(8,0))
        build_sub_sb = Scrollbar(build_sub_f)
        build_sub_sb.pack(side=RIGHT, fill=Y)
        subc_listbox_build = Listbox(build_sub_f, selectmode = SINGLE, height=24, state=DISABLED, relief = SUNKEN, bg='#F4F4F4',
                                     yscrollcommand=build_sub_sb.set, exportselection=False, width=24)
        subc_listbox_build.pack(fill=BOTH)
        xxy = subc_listbox_build.bind('<<ListboxSelect>>', onselect_subc_build)
        subc_listbox_build.select_set(0)
        build_sub_sb.config(command=subc_listbox_build.yview)

        def show_a_tree(evt):
            """get selected file and show in file view"""
            import os
            from nltk import Tree
            from nltk.tree import ParentedTree
            from nltk.draw.util import CanvasFrame
            from nltk.draw import TreeWidget

            sbox = buildbits['sentsbox']
            sent = sentdict[int(sbox.curselection()[0])]
            t = ParentedTree.fromstring(sent)

            # make a frame attached to tab0
            #cf = CanvasFrame(tab0, width=200, height=200)
            
            cf = Canvas(tab0, width=800, height=400, bd = 5)
            buildbits['treecanvas'] = cf
            cf.grid(row=5, column=2, rowspan = 11, padx=(0,0))
            if cf not in boxes:
                boxes.append(cf)
            # draw the tree and send to the frame's canvas
            tc = TreeWidget(cf, t, draggable=1,
                            node_font=('helvetica', -10, 'bold'),
                            leaf_font=('helvetica', -10, 'italic'),
                            roof_fill='white', roof_color='black',
                            leaf_color='green4', node_color='blue2')

            tc.bind_click_trees(tc.toggle_collapsed)

        def select_all_editor(*args):
            """not currently using, but might be good for select all"""
            editor = buildbits['editor']
            editor.tag_add(SEL, "1.0", END)
            editor.mark_set(INSERT, "1.0")
            editor.see(INSERT)
            return 'break'

        def onselect_f(evt):
            """get selected file and show in file view"""
            for box in boxes:
                try:
                    box.destroy()
                except:
                    pass
            import os
            # should only be one
            for i in chosen_f:
                chosen_f.pop()
            wx = evt.widget
            indices = wx.curselection()
            for index in indices:
                value = wx.get(index)
                if value not in chosen_f:
                    chosen_f.append(value)

            if len(chosen_f) == 0:
                return

            if chosen_f[0].endswith('.txt') or chosen_f[0].endswith('.p'):
                newp = path_to_new_unparsed_corpus.get()
                if selected_corpus_has_no_subcorpora.get() == 0:
                    fp = os.path.join(newp, subc_sel_vals_build[0], chosen_f[0])
                else:
                    fp = os.path.join(newp, chosen_f[0])
                if chosen_f[0].endswith('.txt'):
                    try:
                        text=open(fp).read()
                    except IOError:
                        fp = os.path.join(newp, os.path.basename(corpus_fullpath.get()), chosen_f[0])
                        text=open(fp).read()
                else:
                    import pickle
                    data = pickle.load(open(fp, "rb"))
                    text='\n'.join(data)

                # needs a scrollbar
                editor = Text(tab0, height=32)

                bind_textfuncts_to_widgets([editor])

                buildbits['editor'] = editor
                editor.grid(row=1, column=2, rowspan = 9, pady=(10,0), padx=(20, 0))
                if editor not in boxes:
                    boxes.append(editor)
                all_text_widgets.append(editor)
                editor.bind("<%s-s>" % key, savebuttonaction)
                editor.bind("<%s-S>" % key, savebuttonaction)
                editor.config(borderwidth=0,
                      font="{Lucida Sans Typewriter} 12",
                      #foreground="green",
                      #background="black",
                      #insertbackground="white", # cursor
                      #selectforeground="green", # selection
                      #selectbackground="#008000",
                      wrap=WORD, # use word wrapping
                      width=64,
                      undo=True, # Tk 8.4
                      )    
                editor.delete(1.0, END)
                editor.insert(END, text)
                editor.mark_set(INSERT, 1.0)
                editf.set('Edit file: %s' % chosen_f[0])
                viewedit = Label(tab0, textvariable=editf, font=("Helvetica", 13, "bold"))
                viewedit.grid(row=0, column=2, sticky=W, padx=(20, 0))
                if viewedit not in boxes:
                    boxes.append(viewedit)
                filename.set(chosen_f[0])
                fullpath_to_file.set(fp)
                but = Button(tab0, text='Save changes', command=savebuttonaction)
                but.grid(row=9, column=2, sticky='SE')
                buildbits['but'] = but
                if but not in boxes:
                    boxes.append(but)
            elif chosen_f[0].endswith('.xml'):
                import re
                parsematch = re.compile(r'^\s*<parse>(.*)<.parse>')
                newp = path_to_new_unparsed_corpus.get()
                if selected_corpus_has_no_subcorpora.get() == 0:
                    fp = os.path.join(newp, subc_sel_vals_build[0], chosen_f[0])
                else:
                    fp = os.path.join(newp, chosen_f[0])
                try:
                    text=open(fp).read()
                except IOError:
                    fp = os.path.join(newp, os.path.basename(corpus_fullpath.get()), chosen_f[0])
                    text=open(fp).read()
                lines = text.splitlines()
                editf.set('View trees: %s' % chosen_f[0])
                vieweditxml = Label(tab0, textvariable=editf, font=("Helvetica", 13, "bold"))
                vieweditxml.grid(row=0, column=2, sticky=W, padx=(20,0))
                buildbits['vieweditxml'] = vieweditxml
                if vieweditxml not in boxes:
                    boxes.append(vieweditxml)
                trees = []
                def flatten_treestring(tree):
                    import re
                    tree = re.sub(r'\(.*? ', '', tree).replace(')', '')
                    tree = tree.replace('$ ', '$').replace('`` ', '``').replace(' ,', ',').replace(' .', '.').replace("'' ", "''").replace(" n't", "n't").replace(" 're","'re").replace(" 'm","'m").replace(" 's","'s").replace(" 'd","'d").replace(" 'll","'ll").replace('  ', ' ')
                    return tree

                for l in lines:
                    searched = re.search(parsematch, l)
                    if searched:
                        bracktree = searched.group(1)
                        flat = flatten_treestring(bracktree)
                        trees.append([bracktree, flat])
                sentsbox = Listbox(tab0, selectmode = SINGLE, width=120, font=("Courier New", 11))
                if sentsbox not in boxes:
                    boxes.append(sentsbox)
                buildbits['sentsbox'] = sentsbox
                sentsbox.grid(row=1, column=2, rowspan = 4, padx=(20,0))
                sentsbox.delete(0, END)
                for i in list(sentdict.keys()):
                    del sentdict[i]
                for i, (t, f) in enumerate(trees):
                    cutshort = f[:80] + '...'
                    sentsbox.insert(END, '%d: %s' % (i + 1, f))
                    sentdict[i] = t
                xxyyz = sentsbox.bind('<<ListboxSelect>>', show_a_tree)
            
        f_in_s = StringVar()
        f_in_s.set('Files in subcorpus ')

        # a listbox of files
        Label(tab0, textvariable=f_in_s, font=("Helvetica", 13, "bold")).grid(row=0, column=1, sticky='NW', padx=(30, 0))
        build_f_box = Frame(tab0, height=36)
        build_f_box.grid(row=1, column=1, rowspan = 9, padx=(20, 0), pady=(10, 0))
        build_f_sb = Scrollbar(build_f_box)
        build_f_sb.pack(side=RIGHT, fill=Y)
        f_view = Listbox(build_f_box, selectmode = EXTENDED, height=36, state=DISABLED, relief = SUNKEN, bg='#F4F4F4',
                         exportselection = False, yscrollcommand=build_f_sb.set)
        f_view.pack(fill=BOTH)
        xxyy = f_view.bind('<<ListboxSelect>>', onselect_f)
        f_view.select_set(0)
        build_f_sb.config(command=f_view.yview)    

        editf = StringVar()
        editf.set('Edit file: ')

        def savebuttonaction(*args):
            if fullpath_to_file.get().endswith('.txt'):
                f = open(fullpath_to_file.get(), "w")
            else:
                import pickle
                f = open(fullpath_to_file.get(), "wb")
            editor = buildbits['editor']
            text=editor.get(1.0, END)
            if fullpath_to_file.get().endswith('.p'):
                text=[x.strip() for x in text.split('\n')]
                pickle.dump(text, f)
            else:
                try:
                    # normalize trailing whitespace
                    f.write(text.rstrip().encode("utf-8"))
                    f.write("\n")
                finally:
                    f.close()
            timestring('%s saved.' % filename.get())

        filename = StringVar()
        filename.set('')
        fullpath_to_file = StringVar()
        fullpath_to_file.set('')

        ############ ############ ############ ############ ############ 
        # MENU BAR # # MENU BAR # # MENU BAR # # MENU BAR # # MENU BAR # 
        ############ ############ ############ ############ ############ 

        realquit = IntVar()
        realquit.set(0)

        def clear_all():
            import os
            import sys
            python = sys.executable
            os.execl(python, python, * sys.argv)

        def get_tool_pref_file():
            """get the location of the tool preferences files"""
            return os.path.join(rd, 'tool_settings.ini')

        def save_tool_prefs(printout = True):
            """save any preferences to tool preferences"""
            try:
                import configparser
            except:
                import ConfigParser as configparser
            import os
            Config = configparser.ConfigParser()
            settingsfile = get_tool_pref_file()
            if settingsfile is None:
                timestring('No settings file found.')
                return

            Config.add_section('Projects')
            Config.set('Projects','most recent', ';'.join(most_recent_projects[-5:]).lstrip(';'))
            Config.add_section('CoreNLP')
            Config.set('CoreNLP','Parser path', corenlppath.get())
            Config.set('CoreNLP','Memory allocation', parser_memory.get())
            Config.add_section('Appearance')
            Config.set('Appearance','Spreadsheet row header width', row_label_width.get())
            Config.set('Appearance','Spreadsheet cell width', cell_width.get())
            Config.add_section('Other')
            Config.set('Other','Truncate concordance lines', truncate_conc_after.get())
            Config.set('Other','Truncate spreadsheets', truncate_spreadsheet_after.get())
            Config.set('Other','Automatic update check', do_auto_update.get())
            Config.set('Other','do concordancing', do_concordancing.get())
            Config.set('Other','Only format middle concordance column', only_format_match.get())
            Config.set('Other','p value', p_val.get())
            cfgfile = open(settingsfile ,'w')
            Config.write(cfgfile)

            cell_width.get()
            row_label_width.get()
            truncate_conc_after.get()
            truncate_spreadsheet_after.get()
            do_auto_update.get()


            if printout:
                timestring('Tool preferences saved.')

        def load_tool_prefs():
            """load preferences"""
            import os
            try:
                import configparser
            except:
                import ConfigParser as configparser
            settingsfile = get_tool_pref_file()
            if settingsfile is None:
                timestring('No settings file found.')
                return
            if not os.path.isfile(settingsfile):
                timestring('No settings file found at %s' % settingsfile)
                return

            def tryer(config, var, section, name):
                """attempt to load a value, fail gracefully if not there"""
                try:
                    if config.has_option(section,name):
                        var.set(conmap(config, section)[name])
                except:
                    pass

            Config = configparser.ConfigParser()
            Config.read(settingsfile)
            tryer(Config, parser_memory, "CoreNLP", "memory allocation")
            tryer(Config, row_label_width, "Appearance", 'spreadsheet row header width')
            tryer(Config, cell_width, "Appearance", 'spreadsheet cell width')
            tryer(Config, do_auto_update, "Other", 'automatic update check')
            #tryer(Config, conc_when_int, "Other", 'concordance when interrogating')
            tryer(Config, only_format_match, "Other", 'only format middle concordance column')
            tryer(Config, do_concordancing, "Other", 'do concordancing')
            tryer(Config, noregex, "Other", 'disable regular expressions for plaintext search')
            tryer(Config, truncate_conc_after, "Other", 'truncate concordance lines')
            tryer(Config, truncate_spreadsheet_after, "Other", 'truncate spreadsheets')
            tryer(Config, p_val, "Other", 'p value')
            try:
                parspath = conmap(Config, "CoreNLP")['parser path']
            except:
                parspath == 'default'
            try:
                mostrec = conmap(Config, "Projects")['most recent'].lstrip(';').split(';')
                for i in mostrec:
                    most_recent_projects.append(i)
            except:
                pass
            if parspath == 'default' or parspath == '':
                corenlppath.set(os.path.join(os.path.expanduser("~"), 'corenlp'))
            else:
                corenlppath.set(parspath)
            timestring('Tool preferences loaded.')

        def save_config():
            try:
                import configparser
            except:
                import ConfigParser as configparser
            import os
            if any(v != '' for v in list(entryboxes.values())):
                codscheme = ','.join([i.get().replace(',', '') for i in list(entryboxes.values())])
            else:
                codscheme = None
            Config = configparser.ConfigParser()
            cfgfile = open(os.path.join(project_fullpath.get(), 'settings.ini') ,'w')
            Config.add_section('Build')
            Config.add_section('Interrogate')
            relcorpuspath = corpus_fullpath.get().replace(project_fullpath.get(), '').lstrip('/')
            Config.set('Interrogate','Corpus path', relcorpuspath)
            Config.set('Interrogate','Speakers', convert_speakdict_to_string(corpus_names_and_speakers))
            Config.set('Interrogate','dependency type', kind_of_dep.get())
            Config.set('Interrogate','Treat files as subcorpora', files_as_subcorpora.get())

            Config.add_section('Edit')
            Config.add_section('Visualise')
            Config.set('Visualise','Plot style', plot_style.get())
            Config.set('Visualise','Use TeX', texuse.get())
            Config.set('Visualise','x axis title', x_axis_l.get())
            Config.set('Visualise','Colour scheme', chart_cols.get())
            Config.add_section('Concordance')
            Config.set('Concordance','font size', fsize.get())
            #Config.set('Concordance','dependency type', conc_kind_of_dep.get())
            Config.set('Concordance','coding scheme', codscheme)
            if win.get() == 'Window':
                window = 70
            else:
                window = int(win.get())
            Config.set('Concordance','window', window)
            Config.add_section('Manage')
            Config.set('Manage','Project path',project_fullpath.get())

            Config.write(cfgfile)
            timestring('Project settings saved to settings.ini.')

        def quitfunc():
            if in_a_project.get() == 1:
                save_ask = messagebox.askyesno("Save settings", 
                              "Save settings before quitting?")
                if save_ask:
                    save_config()
                    save_tool_prefs()
            realquit.set(1)
            root.quit()

        root.protocol("WM_DELETE_WINDOW", quitfunc)

        def restart(newpath = False):
            """restarts corpkit .py or gui, designed for version updates"""
            import sys
            import os
            import subprocess
            import inspect
            timestring('Restarting ... ')
            # get path to current script
            if newpath is False:
                newpath = inspect.getfile(inspect.currentframe())
            if sys.platform == "win32":
                if newpath.endswith('.py'):
                    timestring('Not yet supported, sorry.')
                    return
                os.startfile(newpath)
            else:
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                if newpath.endswith('.py'):
                    opener = 'python'
                    if 'daniel/Work/corpkit' in newpath:
                        opener = '/Users/daniel/virtenvs/ssled/bin/python'
                    cmd = [opener, newpath]
                else:
                    if sys.platform == "darwin":
                        cmd = [opener, '-n', newpath]
                    else:
                        cmd = [opener, newpath]
                #os.system('%s %s' % (opener, newpath))
                #subprocess.Popen(cmd)
                from time import sleep
                sleep(1)
                #reload(inspect.getfile(inspect.currentframe()))
                subprocess.Popen(cmd)
            try:
                the_splash.__exit__()
            except:
                pass
            root.quit()
            sys.exit()

        def untar(fname, extractto):
            """untar a file"""
            import tarfile
            tar = tarfile.open(fname)
            tar.extractall(extractto)
            tar.close()

        def update_corpkit(stver):
            """get new corpkit, delete this one, open it up"""
            import sys
            import os
            import inspect
            import corpkit
            from corpkit.build import download_large_file
            # get path to this script
            corpath = rd
            #corpath = inspect.getfile(inspect.currentframe())
            
            # check we're using executable version, because .py users can
            # use github to update
            extens = '.%s' % fext
            if extens not in corpath and sys.platform != 'darwin':
                timestring("Get it from GitHub: https://www.github.com/interrogator/corpkit")
                return

            # split on .app or .exe, then re-add .app
            apppath = corpath.split(extens , 1)[0] + extens
            appdir = os.path.dirname(apppath)

            # get new version and the abs path of the download dir and the tar file
            url = 'https://raw.githubusercontent.com/interrogator/corpkit-app/master/corpkit-%s.tar.gz' % stver
 
            path_to_app_parent = sys.argv[0]
            if sys.platform == 'darwin':
                if '.app' in path_to_app_parent:
                    path_to_app_parent = os.path.dirname(path_to_app_parent.split('.app', 1)[0])
            else:
                # WINDOWS SUPPORT
                pass
            if '.py' in path_to_app_parent:
                py_script = True
                path_to_app_parent = os.path.dirname(os.path.join(path_to_app_parent.split('.py', 1)[0]))

            downloaded_dir, corpkittarfile = download_large_file(path_to_app_parent, \
                                                                  url, root=root, note=note, actually_download = True)
            
            timestring('Extracting update ...')
                    
            # why not extract to actual dir?
            untar(corpkittarfile, downloaded_dir)
            
            timestring('Applying update ...')
            
            # delete the tar
            #os.remove(corpkittarfile)
            # get whatever the new app is called
            newappfname = [f for f in os.listdir(downloaded_dir) if f.endswith(fext)][0]
            absnewapp = os.path.join(downloaded_dir, newappfname)
            # get the executable in the path
            restart_now = messagebox.askyesno("Update and restart",
                              "Restart now?\n\nThis will delete the current version of corpkit.")
            import shutil
            if restart_now:
                # remove this very app, but not script, just in case
                if '.py' not in apppath:
                    if sys.platform == 'darwin':
                        shutil.rmtree(apppath)
                    # if windows, it's not a dir
                    else:
                        os.remove(apppath)
                # move new version
                if sys.platform == 'darwin':
                    shutil.copytree(absnewapp, os.path.join(appdir, newappfname))
                # if windows, it's not a dir
                else:
                    shutil.copy(absnewapp, os.path.join(appdir, newappfname))
                # delete donwnloaded file and dir
                shutil.rmtree(downloaded_dir)
                restart(os.path.join(appdir, newappfname))
            # shitty way to do this. what is the standard way of downloading and not installing?
            else:
                if sys.platform == 'darwin':
                    try:
                        shutil.copytree(absnewapp, os.path.join(appdir, newappfname))
                    except OSError:
                        shutil.copytree(absnewapp, os.path.join(appdir, newappfname + '-new'))
                else:
                    try:
                        shutil.copy(absnewapp, os.path.join(appdir, newappfname))
                    except OSError:
                        shutil.copy(absnewapp, os.path.join(appdir, newappfname + '-new'))                
                timestring('New version in %s' % os.path.join(appdir, newappfname + '-new'))
                return

        def make_float_from_version(ver):
            """take a version string and turn it into a comparable float"""
            ver = str(ver)
            ndots_to_delete = ver.count('.') - 1
            return float(ver[::-1].replace('.', '', ndots_to_delete)[::-1])

        def modification_date(filename):
            """get datetime of file modification"""
            import os
            import datetime
            t = os.path.getmtime(filename)
            return datetime.datetime.fromtimestamp(t)

        def check_updates(showfalse = True, lateprint = False, auto = False):
            """check for updates, minor and major."""
            import os
            import re
            import datetime
            from dateutil.parser import parse
            import sys
            import shutil
            
            # weird hacky way to not repeat request
            if do_auto_update.get() == 0 and auto is True:
                return

            if do_auto_update_this_session.get() is False and auto is True:
                return

            # cancel auto if manual
            if auto is False:
                do_auto_update_this_session.set(0)

            # get version as float
            try:
                oldstver = open(os.path.join(rd, 'VERSION.txt'), 'r').read().strip()
            except:
                import corpkit
                oldstver = str(corpkit.__version__)
            ver = make_float_from_version(oldstver)

            # check for major update
            try:
                response = requests.get('https://www.github.com/interrogator/corpkit-app', verify=False)
                html = response.text
            except:
                if showfalse:
                    messagebox.showinfo(
                    "No connection to remote server",
                    "Could not connect to remote server.")
                return
            reg = re.compile('title=.corpkit-([0-9\.]+)\.tar\.gz')
            
            # get version number as string
            stver = str(re.search(reg, html).group(1))
            vnum = make_float_from_version(stver)
            
            # check for major update
            #if 2 == 2:
            if vnum > ver:
                timestring('Update found: corpkit %s' % stver)
                download_update = messagebox.askyesno("Update available",
                              "Update available: corpkit %s\n\n Download now?" % stver)
                if download_update:
                    update_corpkit(stver)
                    return
                else:
                    timestring('Update found: corpkit %s. Not downloaded.' % stver)
                    return
            
            # check for minor update
            else:
                import sys
                timereg = re.compile(r'# <updated>(.*)<.updated>')

                #if '.py' in sys.argv[0] and sys.platform == 'darwin':
                    #oldd = open(os.path.join(rd, 'gui.py'), 'r').read()
                #elif '.app' in sys.argv[0]:
                oldd = open(os.path.join(rd, 'gui.py'), 'r').read()

                dateline = next(l for l in oldd.split('\n') if l.startswith('# <updated>'))
                dat = re.search(timereg, dateline).group(1)
                try:
                    olddate = parse(dat)
                except:
                    olddate = modification_date(sys.argv[0])

                try:
                    script_response = requests.get('https://raw.githubusercontent.com/interrogator/corpkit-app/master/gui.py', verify=False)
                    newscript = script_response.text
                    dateline = next(l for l in newscript.split('\n') if l.startswith('# <updated>'))

                except:
                    if showfalse:
                        messagebox.showinfo(
                        "No connection to remote server",
                        "Could not connect to remote server.")
                    return

                # parse the date part
                try:
                    dat = re.search(timereg, dateline).group(1)
                    newdate = parse(dat)
                except:
                    if showfalse:
                        messagebox.showinfo(
                        "Error checking for update.",
                        "Error checking for update.")
                    return
                # testing code
                #if 2 == 2:
                if newdate > olddate:
                    timestring('Minor update found: corpkit %s' % stver)
                    download_update = messagebox.askyesno("Minor update available",
                                  "Minor update available: corpkit %s\n\n Download and apply now?" % stver)
                    if download_update:
                        url = 'https://raw.githubusercontent.com/interrogator/corpkit-app/master/corpkit-%s' % oldstver
                        
                        # update script
                        if not sys.argv[0].endswith('gui.py'):
                            script_url = 'https://raw.githubusercontent.com/interrogator/corpkit-app/master/gui.py'
                            response = requests.get(script_url, verify=False)
                            with open(os.path.join(rd, 'gui.py'), "w") as fo:
                                fo.write(response.text)
                        else:
                            timestring("Can't replace developer copy, sorry.")
                            return

                        dir_containing_ex, execut = download_large_file(project_fullpath.get(), 
                                                     url = url, root=root, note=note)

                        # make sure we can execute the new script
                        import os
                        os.chmod(execut, 0o777)

                        if not sys.argv[0].endswith('gui.py'):
                            os.remove(os.path.join(rd, 'corpkit-%s' % oldstver))
                            shutil.move(execut, os.path.join(rd, 'corpkit-%s' % oldstver))
                            shutil.rmtree(dir_containing_ex)
                        else:
                            timestring("Can't replace developer copy, sorry.")
                            return
                        #import inspect
                        #sys.argv[0]
                        #extens = '.%s' % fext
                        #if extens not in corpath and sys.platform != 'darwin':
                        #    timestring("Get it from GitHub: https://www.github.com/interrogator/corpkit")
                        #    return
                        ## split on .app or .exe, then re-add .app
                        #apppath = corpath.split(extens , 1)[0] + extens
                        restart(sys.argv[0].split('.app', 1)[0] + '.app')
                        return
                    else:
                        timestring('Minor update found: corpkit %s, %s. Not downloaded.' % (stver, dat.replace('T', ', ')))
                        return

            if showfalse:
                messagebox.showinfo(
                "Up to date!",
                "corpkit (version %s) up to date!" % oldstver)
                timestring('corpkit (version %s) up to date.' % oldstver)
                return


        def start_update_check():
            try:
                check_updates(showfalse = False, lateprint = True, auto = True)
            except:
                filemenu.entryconfig("Check for updates", state="disabled")

        def unmax():
            """stop it being always on top"""
            root.attributes('-topmost', False)

        root.after(1000, unmax)
        
        if not '.py' in sys.argv[0]:
            root.after(10000, start_update_check)

        def set_corenlp_path():
            if sys.platform == 'darwin':
                the_kwargs = {'message': 'Select folder containing the CoreNLP parser.'}
            else:
                the_kwargs = {}
            fp = filedialog.askdirectory(title = 'CoreNLP path',
                                           initialdir = os.path.expanduser("~"),
                                           **the_kwargs)
            if fp and fp != '':
                corenlppath.set(fp)
                if not get_fullpath_to_jars(corenlppath):
                    recog = messagebox.showwarning(title = 'CoreNLP not found', 
                                message = "CoreNLP not found in %s." % fp )
                    timestring("CoreNLP not found in %s." % fp )
                else:
                    save_tool_prefs()

        def config_menu(*args):
            import os
            fp = corpora_fullpath.get()
            recentmenu.delete(0, END)
            if len(most_recent_projects) == 0:
                filemenu.entryconfig("Open recent project", state="disabled")
            if len(most_recent_projects) == 1 and most_recent_projects[0] == '':
                filemenu.entryconfig("Open recent project", state="disabled")
            else:
                filemenu.entryconfig("Open recent project", state="normal")   
                for c in list(set(most_recent_projects[::-1][:5])):
                    if c:
                        lab = os.path.join(os.path.basename(os.path.dirname(c)), os.path.basename(c))
                        recentmenu.add_radiobutton(label=lab, variable=recent_project, value = c)
            if os.path.isdir(fp):
                all_corpora = sorted([d for d in os.listdir(fp) if os.path.isdir(os.path.join(fp, d)) and '/' not in d])
                if len(all_corpora) > 0:
                    filemenu.entryconfig("Select corpus", state="normal")
                    selectmenu.delete(0, END)
                    for c in all_corpora:
                        selectmenu.add_radiobutton(label=c, variable=current_corpus, value = c)
                else:
                    filemenu.entryconfig("Select corpus", state="disabled")
            else:
                filemenu.entryconfig("Select corpus", state="disabled")
                #filemenu.entryconfig("Manage project", state="disabled")
            if in_a_project.get() == 0:
                filemenu.entryconfig("Save project settings", state="disabled")
                filemenu.entryconfig("Load project settings", state="disabled")
                filemenu.entryconfig("Manage project", state="disabled")
                #filemenu.entryconfig("Set CoreNLP path", state="disabled")
            else:
                filemenu.entryconfig("Save project settings", state="normal")
                filemenu.entryconfig("Load project settings", state="normal")
                filemenu.entryconfig("Manage project", state="normal")

                #filemenu.entryconfig("Set CoreNLP path", state="normal")
        
        menubar = Menu(root)
        selectmenu = Menu(root)
        recentmenu = Menu(root)

        if sys.platform == 'darwin':
            filemenu = Menu(menubar, tearoff=0, name='apple', postcommand=config_menu)
        else:
            filemenu = Menu(menubar, tearoff=0, postcommand=config_menu)

        filemenu.add_command(label="New project", command=make_new_project)
        filemenu.add_command(label="Open project", command=load_project)
        filemenu.add_cascade(label="Open recent project", menu=recentmenu)
        filemenu.add_cascade(label="Select corpus", menu=selectmenu)

        filemenu.add_separator()
        filemenu.add_command(label="Save project settings", command=save_config)
        filemenu.add_command(label="Load project settings", command=load_config)
        filemenu.add_separator()
        filemenu.add_command(label="Save tool preferences", command=save_tool_prefs)
        filemenu.add_separator()
        filemenu.add_command(label="Manage project", command=manage_popup)
        filemenu.add_separator()
        #filemenu.add_command(label="Coding scheme print", command=print_entryboxes)
        
        # broken on deployed version ... path to self stuff
        #filemenu.add_separator()

        filemenu.add_command(label="Check for updates", command=check_updates)
        #filemenu.entryconfig("Check for updates", state="disabled")
        #filemenu.add_separator()
        #filemenu.add_command(label="Restart tool", command=restart)
        filemenu.add_separator()
        #filemenu.add_command(label="Exit", command=quitfunc)
        
        menubar.add_cascade(label="File", menu=filemenu)
        if sys.platform == 'darwin':
            windowmenu = Menu(menubar, name='window')
            menubar.add_cascade(menu=windowmenu, label='Window')
        else:
            sysmenu = Menu(menubar, name='system')
            menubar.add_cascade(menu=sysmenu)

        def schemesshow(*args):
            """only edit schemes once in project"""
            import os
            if project_fullpath.get() == '':
                schemenu.entryconfig("Wordlists", state="disabled")
                schemenu.entryconfig("Coding scheme", state="disabled")
            else:
                schemenu.entryconfig("Wordlists", state="normal")
                schemenu.entryconfig("Coding scheme", state="normal")

        schemenu = Menu(menubar, tearoff=0, postcommand=schemesshow)
        menubar.add_cascade(label="Schemes", menu=schemenu)
        schemenu.add_command(label="Coding scheme", command=codingschemer)
        schemenu.add_command(label="Wordlists", command=custom_lists)

        # prefrences section
        if sys.platform == 'darwin':
            root.createcommand('tk::mac::ShowPreferences', preferences_popup)

        def about_box():
            """About message with current corpkit version"""
            import os
            try:
                oldstver = str(open(os.path.join(rd, 'VERSION.txt'), 'r').read().strip())
            except:
                import corpkit
                oldstver = str(corpkit.__version__)

            messagebox.showinfo('About', 'corpkit %s\n\ninterrogator.github.io/corpkit\ngithub.com/interrogator/corpkit\npypi.python.org/pypi/corpkit\n\n' \
                                  'Creator: Daniel McDonald\nmcdonaldd@unimelb.edu.au' % oldstver)

        def show_log():
            """save log text as txt file and open it"""
            import os
            the_input = '\n'.join([x for x in note.log_stream])
            #the_input = note.text.get("1.0",END)
            c = 0
            logpath = os.path.join(log_fullpath.get(), 'log-%s.txt' % str(c).zfill(2))
            while os.path.isfile(logpath):
                logpath = os.path.join(log_fullpath.get(), 'log-%s.txt' % str(c).zfill(2))
                c += 1
            with open(logpath, "w") as fo:
                fo.write(the_input)
                prnt = os.path.join('logs', os.path.basename(logpath))
                timestring('Log saved to "%s".' % prnt)
            import sys
            
            if sys.platform == "win32":
                os.startfile(logpath)
            else:
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                import subprocess
                subprocess.call(['open', logpath])

        def bind_textfuncts_to_widgets(lst):
            """add basic cut copy paste to text entry widgets"""
            for i in lst:
                i.bind("<%s-a>" % key, select_all_text)
                i.bind("<%s-A>" % key, select_all_text)
                i.bind("<%s-v>" % key, paste_into_textwidget)
                i.bind("<%s-V>" % key, paste_into_textwidget)
                i.bind("<%s-x>" % key, cut_from_textwidget)
                i.bind("<%s-X>" % key, cut_from_textwidget)
                i.bind("<%s-c>" % key, copy_from_textwidget)
                i.bind("<%s-C>" % key, copy_from_textwidget)
                try:
                    i.config(undo = True)
                except:
                    pass

        # load preferences
        load_tool_prefs()

        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Help", command=lambda: show_help('h'))
        helpmenu.add_command(label="Query writing", command=lambda: show_help('q'))
        helpmenu.add_command(label="Troubleshooting", command=lambda: show_help('t'))
        helpmenu.add_command(label="Save log", command=show_log)
        #helpmenu.add_command(label="Set CoreNLP path", command=set_corenlp_path)
        helpmenu.add_separator()
        helpmenu.add_command(label="About", command=about_box)
        menubar.add_cascade(label="Help", menu=helpmenu)

        if sys.platform == 'darwin':
            import corpkit
            import subprocess
            ver = corpkit.__version__
            corpath = os.path.dirname(corpkit.__file__)
            if not corpath.startswith('/Library/Python') and not 'corpkit/corpkit/corpkit' in corpath:
                try:
                    subprocess.call('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "corpkit-%s" to true' ''' % ver, shell = True)
                except:
                    pass
        
        root.config(menu=menubar)
        note.focus_on(tab1)
    
    root.deiconify()
    root.lift()
    root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
    try:
        root._splash.__exit__()
    except:
        pass
    root.wm_state('normal')
    root.resizable(TRUE,TRUE)

    # overwrite quitting behaviour, prompt to save settings
    root.createcommand('exit', quitfunc)
    root.mainloop()

if __name__ == "__main__":
    # the traceback is mostly for debugging pyinstaller errors
    import sys
    import pip
    import importlib
    import traceback

    def install(name, loc):
        """if we don't have a module, download it"""
        try:
            importlib.import_module(name)
        except ImportError:
            pip.main(['install', loc])

    tkintertablecode = ('tkintertable', 'git+https://github.com/interrogator/tkintertable.git')
    pilcode = ('PIL', 'http://effbot.org/media/downloads/Imaging-1.1.7.tar.gz')

    if not any(arg.lower() == 'noinstall' for arg in sys.argv):
        install(*tkintertablecode)
        install(*pilcode)

    try:
        corpkit_gui()
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("*** print_tb:")
        traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
        print("*** print_exception:")
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                                  limit=2, file=sys.stdout)
        print("*** print_exc:")
        traceback.print_exc()
        print("*** format_exc, first and last line:")
        formatted_lines = traceback.format_exc().splitlines()
        print(formatted_lines[0])
        print(formatted_lines[-1])
        print("*** format_exception:")
        print(repr(traceback.format_exception(exc_type, exc_value,
                                              exc_traceback)))
        print("*** extract_tb:")
        print(repr(traceback.extract_tb(exc_traceback)))
        print("*** format_tb:")
        print(repr(traceback.format_tb(exc_traceback)))
        print("*** tb_lineno:", exc_traceback.tb_lineno)

