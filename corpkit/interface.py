#!usr/bin/env python
#tkNotebook
#Created By: Patrick T. Cossette <cold_soul79078@yahoo.com>

#tkNotebook allows users to make notebook widgets in Tk

#This software may be modified and redistributed, as long as any and all changes made
#From here on are stated, and ("Created By: Patrick T. Cossette <cold_soul79078@yahoo.com>") still remains somewhere
#In the code.

#This software is opensource, and free in hopes that it may be useful, and comes AS IS
#With no warrenty.

"""
    Defines a Notebook class to be used with Tkinter. A Notebook instance
    has the attributes change_tab, add_tab, destroy_tab, and focus_on.

    change_tab:  Internal Function, I don't suggest you call this directly.
    add_tab:     Creates a tab
    destroy_tab: destroys the given tab
    focus_on:    Focuses on the given tab

    The __init__ function creates three frames. One to hold the tabs together,
    one to create the base to parent each tab's children, and one to hold the
    base frame and the tab frame together.

    Each tab is a Label with a default relief of "GROOVE". Each label uses
    event bindings so that change_tab is called with the tab's ID Number as
    an argument. Each tab relief, when selected is set by default to "RAISED"
    
    For an exampe, view the source code, and run the module.

    Created By: Patrick T. Cossette <cold_soul79078@yahoo.com>    

"""

#!/usr/bin/ipython

# progress bar for various corpling_tools

# from http://nbviewer.ipython.org/github/ipython/ipython/blob/3607712653c66d63e0d7f13f073bde8c0f209ba8/docs/examples/notebooks/Animations_and_Progress.ipynb

# there is dirname as a second arg, which will display the subcorpus in the progress bar

# daniel mcdonald

class GuiProgressBar:
    from time import localtime, strftime
    try:
        from IPython.display import display, clear_output
    except ImportError:
        pass
    have_ipython = False
    def __init__(self, iterations):
        from time import localtime, strftime
        try:
            from IPython.display import display, clear_output
        except ImportError:
            pass
        have_ipython = False
        self.iterations = iterations
        self.prog_bar = '[]'
        self.fill_char = '*'
        self.width = 60
        self.__update_amount(0)
        if have_ipython:
            self.animate = self.animate_ipython
        else:
            self.animate = self.animate_noipython

    def animate_ipython(self, iter, dirname = None):
        from time import localtime, strftime
        import sys

        sys.stdout.flush()
        if dirname:
            self.update_iteration(iter + 1, dirname)
        else:
            self.update_iteration(iter + 1, dirname)
        return '\r', self
    def animate_noipython(self, iter, dirname = None):
        from time import localtime, strftime
        import sys

        if dirname:
            self.update_iteration(iter + 1, dirname)
        else:
            self.update_iteration(iter + 1, dirname)
        return '\r', self

    def update_iteration(self, elapsed_iter, dirname = None):
        from time import localtime, strftime
        self.__update_amount((elapsed_iter / float(self.iterations)) * 100.0, dirname)
        self.prog_bar += ' ' # + ' %d of %s complete' % (elapsed_iter, self.iterations)

    def __update_amount(self, new_amount, dirname = None):
        from time import localtime, strftime
        percent_done = int(round((new_amount / 100.0) * 100.0, 2))
        all_full = self.width - 2
        num_hashes = int(round((percent_done / 100.0) * all_full))
        time = strftime("%H:%M:%S", localtime())
        self.prog_bar = time + ': [' + self.fill_char * num_hashes + ' ' * (all_full - num_hashes) + ']'
        pct_place = (len(self.prog_bar) // 2) + (3)
        if dirname:
            pct_string = '%d%% ' % percent_done + '(' + dirname + ')'
        else:
            pct_string = '%d%%' % percent_done # could pass dirname here!
        self.prog_bar = self.prog_bar[0:pct_place] + \
           (pct_string + self.prog_bar[pct_place + len(pct_string):])

    def __str__(self):
        return str(self.prog_bar)

from Tkinter import *

class IORedirector(object):
    def __init__(self,TEXT_INFO):
        self.TEXT_INFO = TEXT_INFO

class StdoutRedirector(IORedirector):
    def write(self,str):
        self.TEXT_INFO.config(text=self.TEXT_INFO.cget('text') + str)

class Notebook(Frame):
    """Notebook Widget"""
    def __init__(self, parent, activerelief = RAISED, inactiverelief = RIDGE, xpad = 4, ypad = 6, activefg = 'black', inactivefg = 'black', **kw):
        """Construct a Notebook Widget

        Notebook(self, parent, activerelief = RAISED, inactiverelief = RIDGE, xpad = 4, ypad = 6, activefg = 'black', inactivefg = 'black', **kw)        
    
        Valid resource names: background, bd, bg, borderwidth, class,
        colormap, container, cursor, height, highlightbackground,
        highlightcolor, highlightthickness, relief, takefocus, visual, width, activerelief,
        inactiverelief, xpad, ypad.

        xpad and ypad are values to be used as ipady and ipadx
        with the Label widgets that make up the tabs. activefg and inactivefg define what
        color the text on the tabs when they are selected, and when they are not

        """
                                                                                           #Make various argument available to the rest of the class
        self.activefg = activefg                                                           
        self.inactivefg = inactivefg
        self.deletedTabs = []        
        self.xpad = xpad
        self.ypad = ypad
        self.activerelief = activerelief
        self.inactiverelief = inactiverelief                                               
        self.kwargs = kw                                                                   
        self.tabVars = {}                                                                  #This dictionary holds the label and frame instances of each tab
        self.tabs = 0                                                                      #Keep track of the number of tabs                                                                             
        self.noteBookFrame = Frame(parent)                                                 #Create a frame to hold everything together
        self.BFrame = Frame(self.noteBookFrame)                                            #Create a frame to put the "tabs" in
        self.noteBook = Frame(self.noteBookFrame, relief = RAISED, bd = 2, **kw)           #Create the frame that will parent the frames for each tab
        self.noteBook.grid_propagate(0)                                                    #self.noteBook has a bad habit of resizing itself, this line prevents that
        Frame.__init__(self)
        self.noteBookFrame.grid()
        self.BFrame.grid(row =0, sticky = W)
        self.noteBook.grid(row = 1, column = 0, columnspan = 27)

    def change_tab(self, IDNum):
        """Internal Function"""
        
        for i in (a for a in range(0, len(self.tabVars.keys()))):
            if not i in self.deletedTabs:                                                  #Make sure tab hasen't been deleted
                if i <> IDNum:                                                             #Check to see if the tab is the one that is currently selected
                    self.tabVars[i][1].grid_remove()                                       #Remove the Frame corresponding to each tab that is not selected
                    self.tabVars[i][0]['relief'] = self.inactiverelief                     #Change the relief of all tabs that are not selected to "Groove"
                    self.tabVars[i][0]['fg'] = self.inactivefg                             #Set the fg of the tab, showing it is selected, default is black
                else:                                                                      #When on the tab that is currently selected...
                    self.tabVars[i][1].grid()                                              #Re-grid the frame that corresponds to the tab                      
                    self.tabVars[IDNum][0]['relief'] = self.activerelief                   #Change the relief to "Raised" to show the tab is selected
                    self.tabVars[i][0]['fg'] = self.activefg                               #Set the fg of the tab, showing it is not selected, default is black

    def add_tab(self, width = 2, **kw):
        import Tkinter
        """Creates a new tab, and returns it's corresponding frame

        """
        
        temp = self.tabs
        self.tabVars[self.tabs] = [Label(self.BFrame, relief = RIDGE, **kw)]               #Create the tab
        self.tabVars[self.tabs][0].bind("<Button-1>", lambda Event:self.change_tab(temp))  #Makes the tab "clickable"
        self.tabVars[self.tabs][0].pack(side = LEFT, ipady = self.ypad, ipadx = self.xpad) #Packs the tab as far to the left as possible
        self.tabVars[self.tabs].append(Frame(self.noteBook, **self.kwargs))                #Create Frame, and append it to the dictionary of tabs
        self.tabVars[self.tabs][1].grid(row = 0, column = 0)                               #Grid the frame ontop of any other already existing frames
        self.change_tab(0)                                                                 #Set focus to the first tab
        self.tabs += 1                                                                     #Update the tab count
        return self.tabVars[temp][1]                                                       #Return a frame to be used as a parent to other widgets

    def destroy_tab(self, tab):
        """Delete a tab from the notebook, as well as it's corresponding frame

        """
        
        self.iteratedTabs = 0                                                              #Keep track of the number of loops made
        for b in self.tabVars.values():                                                    #Iterate through the dictionary of tabs
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
        for b in self.tabVars.values():                                                    #Iterate through the dictionary of tabs
            if b[1] == tab:                                                                #Find the NumID of the given tab
                self.change_tab(self.iteratedTabs)                                         #send the tab's NumID to change_tab to set focus, mimicking that of each tab's event bindings
                break                                                                      #Job is done, exit the loop
            self.iteratedTabs += 1                                                         #Add one to the loop count

def corpkit_gui():
    import Tkinter, Tkconstants, tkFileDialog
    from Tkinter import StringVar, Listbox, Text
    import sys
    from tkintertable import TableCanvas, TableModel
    #from corpkit import interrogator, editor, plotter

    def adjustCanvas(someVariable = None):
        fontLabel["font"] = ("arial", var.get())
    
    root = Tk()
    root.title("corpkit")
    note = Notebook(root, width= 900, height =800, activefg = 'red', inactivefg = 'blue')  #Create a Note book Instance
    note.grid()
    tab1 = note.add_tab(text = "Interrogate")                                                  #Create a tab with the text "Tab One"
    tab2 = note.add_tab(text = "Edit")                                                  #Create a tab with the text "Tab Two"
    tab3 = note.add_tab(text = "Visualise")                                                    #Create a tab with the text "Tab Three"
    tab4 = note.add_tab(text = "Concordance")                                                 #Create a tab with the text "Tab Four"
    tab5 = note.add_tab(text = "Management")                                                 #Create a tab with the text "Tab Five"
    #Label(tab1, text = 'Tab one').grid(row = 0, column = 0)                                #Use each created tab as a parent, etc etc...
    
    ###################     ###################     ###################     ###################
    # INTERROGATE TAB #     # INTERROGATE TAB #     # INTERROGATE TAB #     # INTERROGATE TAB #
    ###################     ###################     ###################     ###################

    def refresh():
        """refreshes the list of dataframes in the editor and plotter panes"""
        # Reset data1_pick and delete all old options
        data1_pick.set(all_interrogations.keys()[-1])
        #data2_pick.set(all_interrogations.keys()[-1])
        dataframe1s['menu'].delete(0, 'end')
        dataframe2s['menu'].delete(0, 'end')
        data_to_plot.set(all_interrogations.keys()[-1])
        every_interrogation['menu'].delete(0, 'end')
        every_interro_listbox.delete(0, 'end')

        new_choices = ['Select an interrogation']
        for interro in all_interrogations.keys():
            new_choices.append(interro)
        new_choices = tuple(new_choices)
        for choice in new_choices:
            dataframe1s['menu'].add_command(label=choice, command=Tkinter._setit(data1_pick, choice))
            dataframe2s['menu'].add_command(label=choice, command=Tkinter._setit(data2_pick, choice))
            every_interrogation['menu'].add_command(label=choice, command=Tkinter._setit(data_to_plot, choice))
            #every_interro_listbox.delete(0, END)
            if choice != 'Select an interrogation' and choice != 'None':
                every_interro_listbox.insert(END, choice)

    transdict = {
            'Get distance from root for regex match': 'a',
            'Get tag and word of match': 'b',
            'Count matches': 'c',
            'Get dependent of regular expression match and the r/ship': 'd',
            'Get dependency function of regular expression match': 'f',
            'Get governor of regular expression match and the r/ship': 'g',
            'Get lemmata via dependencies': 'l',
            'Get tokens by dependency role': 'm',
            'Get dependency index of regular expression match': 'n',
            'Get part-of-speech tag': 'p',
            'Regular expression search': 'r',
            'Simple search string search': 's',
            'Match tokens via dependencies': 't',
            'Get words': 'w'}

    def do_interrogation():
        """performs an interrogation"""

        from corpkit import interrogator
        #root.TEXT_INFO = Label(tab1, height=20, width=80, text="", justify = LEFT, font=("Courier New", 12))
        #root.TEXT_INFO.grid(column=1, row = 1)
        conv = (spl.var).get()
        if conv == 'Convert spelling' or conv == 'Off':
            conv = False
        interrogator_args = {'query': entrytext.get(),
                         'lemmatise': lem.get(),
                         'phrases': phras.get(),
                         'titlefilter': tit_fil.get(),
                         'convert_spelling': conv}
        #sys.stdout = StdoutRedirector(root.TEXT_INFO)
        r = interrogator('/users/danielmcdonald/documents/work/risk/data/nyt/sample', 
                          transdict[datatype_chosen_option.get()], 
                          **interrogator_args)
        # when not testing:
        #r = interrogator(fullpath.get(), chosen_option.get(), **interrogator_args)
        if nametext.get() == 'interrogation name':
            c = 0
            the_name = 'interrogation-%s' % str(c).zfill(2)
            while the_name in all_interrogations.keys():
                c += 1
                the_name = 'interrogation-%s' % str(c).zfill(2)
        else:
            the_name = nametext.get()
        try:
            del all_interrogations['None']
        except KeyError:
            pass
        all_interrogations[the_name] = r
        refresh()
        import pandas

        totals_as_df = pandas.DataFrame(r.totals, dtype = object)
        if transdict[datatype_chosen_option.get()] != 'c':
            longest = max([len(str(i)) for i in list(r.results.columns)]) 
            update_spreadsheet(interro_results, r.results, height = 260, width = 50)
        else:
            longest = 10
        update_spreadsheet(interro_totals, totals_as_df, height = 10, width = 50)

    class MyOptionMenu(OptionMenu):
        """Simple OptionMenu for things that don't change"""
        def __init__(self, tab1, status, *options):
            self.var = StringVar(tab1)
            self.var.set(status)
            OptionMenu.__init__(self, tab1, self.var, *options)
            self.config(font=('calibri',(12)),width=20)
            self['menu'].config(font=('calibri',(10)))
    
    c = 0 # for naming unnamed interrogations

    # corpus path setter
    fullpath = StringVar()
    fullpath.set('/users/danielmcdonald/documents/work/risk/data/nyt/sample')
    basepath = StringVar()
    basepath.set('Select corpus path')

    import os
    subcorpora = {fullpath.get(): sorted([d for d in os.listdir(fullpath.get()) if os.path.isdir(os.path.join(fullpath.get(), d))])}

    def getdir():
        import os
        fp = tkFileDialog.askdirectory()
        fullpath.set(fp)
        basepath.set('Corpus: "%s"' % os.path.basename(fp))
        subs = sorted([d for d in os.listdir(fp) if os.path.isdir(os.path.join(fp, d))])
        for k in subcorpora.keys():
            del subcorpora[k]
        subcorpora[fp] = subs
    
    Button(tab1, textvariable = basepath, command = getdir).grid()


    # not sure i need this ...
    def onselect(evt):
        w = evt.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        datatype_chosen_option.set(value)


    def callback(*args):
        """if the drop down list for data type changes, fill options"""
        option_dict = {'Trees': ['Get words', 
                                 'Get tag and word of match', 
                                 'Count matches', 
                                 'Get part-of-speech tag'],
                        'Dependencies':
                                ['Get dependent of regular expression match and the r/ship',
                                 'Get dependency function of regular expression match',
                                 'Get governor of regular expression match and the r/ship',
                                 'Get lemmata via dependencies',
                                 'Get tokens by dependency role',
                                 'Match tokens via dependencies',
                                 'Get distance from root for regex match'],
                        'Plaintext': 
                                ['Regular expression search', 
                                 'Simple search string search']}
        datatype_listbox.delete(0, 'end')
        chosen = datatype_picked.get()
        lst = option_dict[chosen]
        for e in lst:
            datatype_listbox.insert(END, e)

    datatype_picked = StringVar(root)
    datatype_picked.set('Dependencies')
    pick_a_datatype = OptionMenu(tab1, datatype_picked, *tuple(('Trees', 'Dependencies', 'Plaintext')))
    pick_a_datatype.grid()
    datatype_picked.trace("w", callback)

    datatype_listbox = Listbox(tab1, selectmode = BROWSE)
    datatype_listbox.grid()
    datatype_chosen_option = StringVar()
    datatype_chosen_option.set('Get words')
    #datatype_chosen_option.set('w')
    x = datatype_listbox.bind('<<ListboxSelect>>', onselect)
    # hack: change it now to populate below 
    datatype_picked.set('Trees')
    datatype_listbox.select_set(0)


    # query: should be drop down, with custom option ...
    entrytext = StringVar()
    entrytext.set('any')
    Entry(tab1, textvariable = entrytext).grid()

    # Interrogation name
    nametext = StringVar()
    nametext.set('interrogation name')
    Entry(tab1, textvariable = nametext).grid()

    # boolean interrogation arguments
    lem = IntVar()
    Checkbutton(tab1, text="Lemmatise", variable=lem, onvalue = True, offvalue = False).grid()
    phras = IntVar()
    Checkbutton(tab1, text="Phrases", variable=phras, onvalue = True, offvalue = False).grid()
    tit_fil = IntVar()
    Checkbutton(tab1, text="Filter titles", variable=tit_fil, onvalue = True, offvalue = False).grid()

    spl = MyOptionMenu(tab1, 'Convert spelling', 'Off','UK','US')
    spl.grid()

    # interrogate button
    Button(tab1, text = 'Interrogate!', command = lambda: do_interrogation()).grid()

    # output
    interro_results = Frame(tab1)
    interro_results.grid(column = 1, row = 0, rowspan=3)

    interro_totals = Frame(tab1, height = 1)
    interro_totals.grid(column = 1, row = 4, rowspan=3)

    ##############    ##############     ##############     ##############     ############## 
    # EDITOR TAB #    # EDITOR TAB #     # EDITOR TAB #     # EDITOR TAB #     # EDITOR TAB # 
    ##############    ##############     ##############     ##############     ############## 

    def update_spreadsheet(frame_to_update, df_to_show, height = 140, width = 50):
        """refresh a spreadsheet in the editor window"""
        from collections import OrderedDict
        import pandas
        model = TableModel()
        as_int = pandas.DataFrame(df_to_show, dtype = object)
        raw_data = as_int.to_dict()
        raw_data = OrderedDict(sorted(raw_data.items(), key=lambda t: sum([i for i in t[1].values()]), reverse = True))
        #sorted_raw = OrderedDict{}
        #better = OrderedDict{}
        for name, val in raw_data.items():
            raw_data[name] = OrderedDict(sorted(val.items(), key=lambda t: t[0]))
        table = TableCanvas(frame_to_update, model=model, showkeynamesinheader=True, height = height, rowheaderwidth=width)
        table.createTableFrame()
        model = table.model
        model.importDict(raw_data) #can import from a dictionary to populate model
        table.createTableFrame()
        # sorts by total freq, ok for now
        table.sortTable(reverse = 1)
        table.redrawTable()

    def do_editing():
        """what happens when you press edit"""
        import pandas
        from corpkit import editor
        try:
            del all_edited_results['None']
        except KeyError:
            pass
        # translate operation into interrogator input
        operation_text = (ops.var).get()
        if operation_text == 'None' or operation_text == 'Select an operation':
            operation_text = None
        # translate dataframe2 into interrogator input
        data2 = data2_pick.get()
        if data2 == 'None' or data2 == 'Pick something to combine with' or data2 == 'Select an interrogation':
            data2 = False

        if data2:
            if df2branch.get() == 1:
                data2 = all_interrogations[data2].results
            elif df2branch.get() == 0:
                data2 = all_interrogations[data2].totals

        the_data = all_interrogations[data1_pick.get()]
        if df1branch.get() == 1:
            data1 = all_interrogations[data1_pick.get()].results
        # is this wrong?
        elif df1branch.get() == 0:
            data1 = all_interrogations[data1_pick.get()].totals

        if (spl_editor.var).get() == 'Off' or (spl_editor.var).get() == 'Convert spelling':
            spel = False
        else:
            spel = (spl_editor.var).get()
        
        # dictionary of all arguments for editor

        editor_args = {'operation': operation_text,
                       'dataframe2': data2,
                       'spelling': spel}
        
        # do editing
        r = editor(data1, **editor_args)
        # name the edit
        c = 0
        if edit_nametext.get() == 'edit name':
            the_name = 'edited-%s' % str(c).zfill(2)
            while the_name in all_edited_results.keys():
                c += 1
                the_name = 'edited-%s' % str(c).zfill(2)
        else:
            the_name = edit_nametext.get()
        all_interrogations[the_name] = r
        # store edited interrogation

        #longest = max([len(str(i)) for i in list(the_data.results.columns)])
        update_spreadsheet(o_editor_results, the_data.results, width = 50)
        update_spreadsheet(o_editor_totals, pandas.DataFrame(the_data.totals, dtype = object), height = 10, width = 50)

        #longest = max([len(str(i)) for i in list(r.results.columns)])
        update_spreadsheet(n_editor_results, r.results, width = 50)
        update_spreadsheet(n_editor_totals, pandas.DataFrame(r.totals, dtype = object), height = 10, width = 50)
        all_edited_results[the_name] = r
        refresh()




    # Edit name
    edit_nametext = StringVar()
    edit_nametext.set('edit name')
    Entry(tab2, textvariable = edit_nametext).grid()

    # DF1 for editor
    data1_pick = StringVar(root)
    data1_pick.set("Select an interrogation")
    from collections import OrderedDict
    all_interrogations = OrderedDict()
    all_interrogations['None'] = 'sorry'

    # DF1 options for editor
    dataframe1s = OptionMenu(tab2, data1_pick, *tuple([i for i in all_interrogations.keys()]))
    dataframe1s.grid()

    # DF2 branch selection
    df1branch = IntVar()
    df1box = Checkbutton(tab2, text="Use results branch of df1?", variable=df1branch)
    df1box.select()
    df1box.grid()

    # operation for editor
    operations = ('None', '%', '*', '/', '-', '+', 'a', 'd', 'k')
    l =  ['Select an operation'] + [i for i in operations]
    ops = MyOptionMenu(tab2, 'Select an operation', *operations)
    ops.grid()

    # DF2 option for editor
    data2_pick = StringVar(root)
    data2_pick.set('Pick something to combine with')
    dataframe2s = OptionMenu(tab2, data2_pick, *tuple([i for i in all_interrogations.keys()]))
    dataframe2s.grid()

    # DF2 branch selection
    df2branch = IntVar()
    Checkbutton(tab2, text="Use results branch of df2?", variable=df2branch).grid()

    spl_editor = MyOptionMenu(tab2, 'Convert spelling', 'Off','UK','US')
    spl_editor.grid()

    Button(tab2, text = 'Edit', command = lambda: do_editing()).grid()
    # storage of edited results
    all_edited_results = OrderedDict()
    all_edited_results['None'] = 'sorry'

    # output
    o_editor_results = Frame(tab2)
    o_editor_results.grid(column = 1, row = 0, rowspan=2)

    o_editor_totals = Frame(tab2)
    o_editor_totals.grid(column = 1, row = 2, rowspan=1)
        
    n_editor_results = Frame(tab2)
    n_editor_results.grid(column = 1, row = 3, rowspan=2)

    n_editor_totals = Frame(tab2)
    n_editor_totals.grid(column = 1, row = 5, rowspan=1)

    interrogation_name = StringVar()
    interrogation_name.set('waiting')
    Label(tab1, textvariable = interrogation_name.get()).grid()
    #root.TEXT_INFO = Label(tab1, height=20, width=80, text="", justify = LEFT, font=("Courier New", 12))

    #################       #################      #################      #################  
    # VISUALISE TAB #       # VISUALISE TAB #      # VISUALISE TAB #      # VISUALISE TAB #  
    #################       #################      #################      #################  

    def do_plotting():

        # junk for showing the plot in tkinter
        import matplotlib
        matplotlib.use('TkAgg')
        from numpy import arange, sin, pi
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
        # implement the default mpl key bindings
        from matplotlib.backend_bases import key_press_handler
        from matplotlib.figure import Figure

        from corpkit import plotter
        if branch_to_plot.get() == 1:
            what_to_plot = all_interrogations[data_to_plot.get()].results
        elif branch_to_plot.get() == 0:
            what_to_plot = all_interrogations[data_to_plot.get()].totals
        # determine num to plot
        num = number_to_plot.get()
        try:
            num = int(num)
        except:
            if num.lower() == 'any':
                num = 'any'
            else:
                num = 7

        the_kind = (chart_kind.var).get()
        if the_kind == 'Type of chart':
            the_kind = 'line'
        # plotter options
        d = {'num_to_plot': num,
             'kind': the_kind}
        f = plotter(plotnametext.get(), what_to_plot, **d)
        # a Tkinter.DrawingArea
        canvas = FigureCanvasTkAgg(f.gcf(), tab3)
        canvas.show()
        canvas.get_tk_widget().grid(column = 1, row = 0, rowspan = 5)        

    def save_current_image():
        return

    def image_clear():
        return

    def reset_plotter_pane():
        return


    # title tab
    plotnametext = StringVar()
    plotnametext.set('Image title')
    Entry(tab3, textvariable = plotnametext).grid()

    # select result to plot
    data_to_plot = StringVar(root)
    data_to_plot.set(all_interrogations[all_interrogations.keys()[-1]])

    every_interrogation = OptionMenu(tab3, data_to_plot, *tuple([i for i in all_interrogations.keys()]))
    every_interrogation.grid()

    # branch selection
    branch_to_plot = IntVar()
    plotbranch_button = Checkbutton(tab3, text="Use results branch?", variable=branch_to_plot)
    plotbranch_button.select()
    plotbranch_button.grid()
    # options:

    # num_to_plot
    number_to_plot = StringVar()
    number_to_plot.set('7')
    Entry(tab3, textvariable = number_to_plot).grid()

    # x label

    # y label

    # etc

    kinds_of_chart = ('line', 'bar', 'barh', 'pie', 'area')
    k =  ['Type of chart'] + [i for i in kinds_of_chart]
    chart_kind = MyOptionMenu(tab3, 'Type of chart', *kinds_of_chart)
    chart_kind.grid()

    # plot button
    Button(tab3, text = 'Plot', command = lambda: do_plotting()).grid()

    # save image button
    Button(tab3, text = 'Save image', command = lambda: save_current_image()).grid()

    # clear image
    Button(tab3, text = 'Clear image', command = lambda: do_plotting()).grid()

    # reset pane
    Button(tab3, text = 'Reset plotter pane', command = lambda: reset_plotter_pane()).grid()


    ###################     ###################     ###################     ###################
    # CONCORDANCE TAB #     # CONCORDANCE TAB #     # CONCORDANCE TAB #     # CONCORDANCE TAB #
    ###################     ###################     ###################     ###################

    def do_concordancing():
        from corpkit import conc
        corpus = os.path.join(fullpath.get(), subc_pick.get())
        query = query_text.get()
        d = {'window': int(wind_size.get()), 
             'random': random_conc_option.get(),
             'trees': show_trees.get(),
             'n': 'all'}
        r = conc(corpus, query, **d)
        return

    # SELECT SUBCORPUS
    subc_pick = StringVar(root)
    subc_pick.set("Select subcorpus to concordance")
    pick_subcorpora = OptionMenu(tab4, subc_pick, *tuple([s for s in subcorpora[fullpath.get()]]))
    pick_subcorpora.grid()

    # query: should be drop down, with custom option ...
    query_text = StringVar()
    query_text.set('any')
    Entry(tab4, textvariable = query_text).grid()
    
    # WINDOW SIZE
    window_sizes = ('20', '30', '40', '50', '60', '70', '80', '90', '100')
    l =  ['Window size'] + [i for i in window_sizes]
    wind_size = MyOptionMenu(tab4, 'Window size', *window_sizes)
    wind_size.grid()

    # RANDOM
    random_conc_option = IntVar()
    Checkbutton(tab4, text="Random", variable=random_conc_option, onvalue = True, offvalue = False).grid()

    # RANDOM
    show_trees = IntVar()
    Checkbutton(tab4, text="Show trees", variable=show_trees, onvalue = True, offvalue = False).grid()

    Button(tab4, text = 'Run', command = lambda: do_concordancing()).grid()


    ##############     ##############     ##############     ##############     ############## 
    # MANAGE TAB #     # MANAGE TAB #     # MANAGE TAB #     # MANAGE TAB #     # MANAGE TAB # 
    ##############     ##############     ##############     ##############     ############## 

    # save result(s) to file
    # load result(s)
    # delete results from memory
    # rename results

    def get_saved_results():
        from corpkit import load_result, load_all_results
        r = load_all_results(data_dir = data_fullpath.get())
        for name, loaded in r.items():
            all_interrogations[name] = loaded
        refresh()

    def renamer():
        return
    
    # corpus path setter
    data_fullpath = StringVar()
    data_fullpath.set('/users/danielmcdonald/documents/work/risk/data/mini_saved')
    data_basepath = StringVar()
    data_basepath.set('Select data directory')

    def data_getdir():
        fp = tkFileDialog.askdirectory()
        data_fullpath.set(fp)
        data_basepath.set('Saved data: "%s"' % os.path.basename(fp))
        #fs = sorted([d for d in os.listdir(fp) if os.path.isfile(os.path.join(fp, d))])
    Button(tab5, textvariable = data_basepath, command = data_getdir).grid()
    Button(tab5, text = 'Get all saved interrogations', command = get_saved_results).grid()

    def save_one_or_more():
        from corpkit import save_result
        for i in sel_vals:
            if i + '.p' not in os.listdir(data_fullpath.get()):
                save_result(all_interrogations[i], i + '.p', savedir = data_fullpath.get())
            else:
                print 'File already exists.'
        return

    def remove_one_or_more():
        for i in sel_vals:
            try:
                del all_interrogations[i]
            except:
                pass
        refresh()

    sel_vals = []

    # a list of every interrogation
    def onselect_interro(evt):
        # remove old vals
        for i in sel_vals:
            sel_vals.pop()
        wx = evt.widget
        indices = wx.curselection()
        for index in indices:
            value = wx.get(index)
            if value not in sel_vals:
                sel_vals.append(value)

    every_interro_listbox = Listbox(tab5, selectmode = EXTENDED)
    every_interro_listbox.grid()
    # Set interrogation option
    ei_chosen_option = StringVar()
    #ei_chosen_option.set('w')
    xx = every_interro_listbox.bind('<<ListboxSelect>>', onselect_interro)
    # default: w option
    every_interro_listbox.select_set(0)

    Button(tab5, text="Remove selected interrogation(s)", 
           command=remove_one_or_more).grid()

    Button(tab5, text = 'Save selected interrogation(s)', command = save_one_or_more).grid()

    #var = IntVar()
    #var.set(10)
    #scale = Scale(tab1, font = ("arial", 10), orient = 'horizontal', command = adjustCanvas, variable =var).grid()
    #fontLabel = Label(tab1, text = "TEXT", font = ("Arial", 10))
    #fontLabel.grid()
    #df_var = StringVar()
    #try:
    #    df_var.set(all_interrogations[-1].results.head(5).T.head(5).T.to_string)
    #except:
    #    df_var.set(all_interrogations[-1])
    #Label(tab2, textvariable = df_var).grid()

    note.focus_on(tab5)
    root.mainloop()

if __name__ == "__main__":
    corpkit_gui()

