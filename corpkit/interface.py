#!usr/bin/python
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

import Tkinter
from Tkinter import *
import sys,string
import threading
import ScrolledText
import time
from time import strftime, localtime

########################################################################
class RedirectText(object):
    """"""
 
    #----------------------------------------------------------------------
    def __init__(self, text_ctrl):
        """Constructor"""
        self.output = text_ctrl
 
    #----------------------------------------------------------------------
    def write(self, string):
        """"""
        import re
        reg = re.compile(r'^\s*$')
        if not re.match(reg, string):
            self.output.insert(Tkinter.END, '\n' + string.replace('\r', ''))
 

class IORedirector(object):
    '''A general class for redirecting I/O to this Text widget.'''
    def __init__(self,text_area):
        self.text_area = text_area

class StdoutRedirector(IORedirector):
    '''A class for redirecting stdout to this Text widget.'''
    def write(self,str):
        self.text_area.write(str,False)

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
        self.BFrame = Frame(self.noteBookFrame)
        self.statusbar = Frame(self.noteBookFrame, bd = 2, height = 25, width = kw['width'] / 2 + 30)                                            #Create a frame to put the "tabs" in
        self.noteBook = Frame(self.noteBookFrame, relief = RAISED, bd = 2, **kw)           #Create the frame that will parent the frames for each tab
        self.noteBook.grid_propagate(0)
        self.text = ScrolledText.ScrolledText(self.statusbar, height = 0.5, font = ("Courier New", 15))
        self.text.grid()
        # alternative ...
        #self.text = Text(self.statusbar, height = 1, undo = True)
        self.text.update_idletasks()
        def callback(*args):
            self.text.see(END)
            self.text.edit_modified(0)
        self.text.bind('<<Modified>>', callback)

        self.redir = RedirectText(self.text)
        sys.stdout = self.redir

        #self.statusbar.grid_propagate(0)                                                    #self.noteBook has a bad habit of resizing itself, this line prevents that
        Frame.__init__(self)
        self.noteBookFrame.grid()
        self.BFrame.grid(row = 0, column = 0, columnspan = 27, sticky = N) # ", column = 13)" puts the tabs in the middle!
        self.noteBook.grid(row = 1, column = 0, columnspan = 27)
        self.statusbar.grid(row = 2)



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
        """Creates a new tab, and returns its corresponding frame

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
    import Tkinter, Tkconstants, tkFileDialog, tkMessageBox, tkSimpleDialog
    from Tkinter import StringVar, Listbox, Text
    import sys
    from tkintertable import TableCanvas, TableModel
    import corpkit
    #from dictionaries.process_types import process_types
    #from dictionaries.roles import roles
    #from dictionaries.wordlists import wordlists
    #from corpkit import interrogator, editor, plotter

    def adjustCanvas(someVariable = None):
        fontLabel["font"] = ("arial", var.get())
    
    root = Tk()
    root.title("corpkit")

    #HWHW
    note = Notebook(root, width= 980, height = 500, activefg = 'red', inactivefg = 'blue')  #Create a Note book Instance
    note.grid()
    tab1 = note.add_tab(text = "Interrogate")                                                  #Create a tab with the text "Tab One"
    tab2 = note.add_tab(text = "Edit")                                                  #Create a tab with the text "Tab Two"
    tab3 = note.add_tab(text = "Visualise")                                                    #Create a tab with the text "Tab Three"
    tab4 = note.add_tab(text = "Concordance")                                                 #Create a tab with the text "Tab Four"
    tab5 = note.add_tab(text = "Manage")                                                 #Create a tab with the text "Tab Five"
    #Label(tab1, text = 'Tab one').grid(row = 0, column = 0)                                #Use each created tab as a parent, etc etc...
    
    note.text.see(Tkinter.END)
    note.text.yview_pickplace("end")
    note.text.update_idletasks()
    ###################     ###################     ###################     ###################
    # INTERROGATE TAB #     # INTERROGATE TAB #     # INTERROGATE TAB #     # INTERROGATE TAB #
    ###################     ###################     ###################     ###################

    # a dict of the editor frame names and models
    editor_tables = {}
    sort_direction = True
    #import threading
    #sys.stdout = StdoutRedirector(root)
    #mostrecent_stdout = StringVar()
    #mostrecent_stdout.set('Dummy')
    #Label(note.statusbar, textvariable = mostrecent_stdout).grid()

    def need_make_totals(df):
        try:
            x = df.iloc[0,0]
        except:
            return False
        if type(df.iloc[0,0]) == float:
            return False
        elif type(df.iloc[0,0]) == int:
            return True

    def make_df_totals(df):   
        df = df.drop('Total', errors = 'ignore')
        # add new totals
        df.ix['Total'] = df.drop('tkintertable-order', errors = 'ignore').sum().astype(object)
        return df

    def make_df_from_model(model):
        recs = model.getAllCells()
        colnames = model.columnNames
        collabels = model.columnlabels
        row=[]
        csv_data = []
        for c in colnames:
            row.append(collabels[c])
        csv_data.append(','.join([str(s) for s in row]))
        #csv_data.append('\n')
        for row in recs.keys():
            rowname = model.getRecName(row)
            csv_data.append(','.join([str(rowname)] + [str(s) for s in recs[row]]))
            #csv_data.append('\n')
            #writer.writerow(recs[row])
        csv = '\n'.join(csv_data)
        import pandas
        from StringIO import StringIO
        newdata = pandas.read_csv(StringIO(csv), index_col=0, header=0)
        newdata = pandas.DataFrame(newdata, dtype = object)
        newdata = newdata.T
        newdata = newdata.drop('Total', errors = 'ignore')
        newdata = add_tkt_index(newdata)
        if need_make_totals(newdata):
            newdata = make_df_totals(newdata)
        return newdata

    def refresh():
        """refreshes the list of dataframes in the editor and plotter panes"""
        # Reset data1_pick and delete all old options
        # get the latest only after first interrogation
        if len(all_interrogations.keys()) == 1:
            data1_pick.set(all_interrogations.keys()[-1])
        #data2_pick.set(all_interrogations.keys()[-1])
        dataframe1s['menu'].delete(0, 'end')
        dataframe2s['menu'].delete(0, 'end')
        if len(all_interrogations.keys()) > 0:
            data_to_plot.set(all_interrogations.keys()[-1])
        every_interrogation['menu'].delete(0, 'end')
        every_interro_listbox.delete(0, 'end')
        try:
            del all_interrogations['None']
        except:
            pass

        new_choices = []
        for interro in all_interrogations.keys():
            new_choices.append(interro)
        new_choices = tuple(new_choices)
        dataframe2s['menu'].add_command(label='Self', command=Tkinter._setit(data2_pick, 'Self'))
        for choice in new_choices:
            dataframe1s['menu'].add_command(label=choice, command=Tkinter._setit(data1_pick, choice))
            dataframe2s['menu'].add_command(label=choice, command=Tkinter._setit(data2_pick, choice))
            every_interrogation['menu'].add_command(label=choice, command=Tkinter._setit(data_to_plot, choice))
            #every_interro_listbox.delete(0, END)
            if choice != 'None':
                every_interro_listbox.insert(END, choice)

    def add_tkt_index(df):
        import pandas
        """add order to df for tkintertable"""
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
            while the_name in all_interrogations.keys():
                c += 1
                the_name = '%s-%s' % (type_of_data, str(c).zfill(2))
        else:
            the_name = name_box_text
        return the_name

    transdict = {
            'Get distance from root for regex match': 'a',
            'Get tag and word of match': 'b',
            'Count matches': 'c',
            'Get "role:dependent", matching governor': 'd',
            'Get semantic role of match': 'f',
            'Get "role:governor", matching dependent': 'g',
            'Get lemmata via dependencies': 'l',
            'Get tokens by dependency role': 'm',
            'Get dependency index of regular expression match': 'n',
            'Get part-of-speech tag': 'p',
            'Regular expression search': 'r',
            'Simple search string search': 's',
            'Match tokens via dependencies': 't',
            'Get words': 'w'}

    import itertools
    direct = itertools.cycle([0,1]).next

    def data_sort(pane = 'interrogate', sort_direction = False):
        import pandas
        if pane == 'interrogate':
            #update_all_interrogations(pane = 'interrogate')
            #res = all_interrogations[all_interrogations.keys()[-1]].results
            #tot = pandas.DataFrame(all_interrogations[all_interrogations.keys()[-1]].totals, dtype = object)
            update_spreadsheet(interro_results, df_to_show = None, height = 260, indexwidth = 70, model = editor_tables[interro_results], just_default_sort = True)
            update_spreadsheet(interro_totals, height = 10, indexwidth = 70, model = editor_tables[interro_totals], just_default_sort = True)
        elif pane == 'edit':
            #update_all_interrogations(pane = 'edit')
            update_spreadsheet(o_editor_results, df_to_show = None, height = 260, indexwidth = 70, model = editor_tables[o_editor_results], just_default_sort = True)
            update_spreadsheet(o_editor_totals, df_to_show = None, height = 10, indexwidth = 70, model = editor_tables[o_editor_totals], just_default_sort = True)
            update_spreadsheet(n_editor_results, df_to_show = None, height = 260, indexwidth = 70, model = editor_tables[n_editor_results], just_default_sort = True)
            update_spreadsheet(n_editor_totals, df_to_show = None, height = 10, indexwidth = 70, model = editor_tables[n_editor_totals], just_default_sort = True)
        elif pane == 'plot':
            pass

    def do_interrogation():
        """performs an interrogation"""
        import pandas
        from corpkit import interrogator
        
        #Take_stdout()

        # spelling
        conv = (spl.var).get()
        if conv == 'Convert spelling' or conv == 'Off':
            conv = False

        # special query
        if special_queries.get() != 'Off':
            spec_quer_translate = {'Participants': 'participants',
                                   'Any': 'any',
                                   'Processes': 'processes',
                                   'Subjects': 'subjects',
                                   'Entiries': 'entities'}

            query = spec_quer_translate[special_queries.get()]
        
        # if not special query, get normal query, turn list into list
        else:
            query = entrytext.get()
            # allow list queries
            if query.startswith('[') and query.endswith(']'):
                query = query.lstrip('[').rstrip(']').replace("'", '').replace('"', '').replace(' ', '').split(',')

        selected_option = transdict[datatype_chosen_option.get()]
        interrogator_args = {'query': query,
                             'lemmatise': lem.get(),
                             'phrases': phras.get(),
                             'titlefilter': tit_fil.get(),
                             'case_sensitive': case_sensitive.get(),
                             'convert_spelling': conv,
                             'root': root}

        #r = interrogator('/users/danielmcdonald/documents/work/risk/data/nyt/sample', 
                          #selected_option, 
                          #**interrogator_args)
    
        # when not testing:
        r = interrogator(fullpath.get(), selected_option, **interrogator_args)

        # make name
        the_name = namer(nametext.get(), type_of_data = 'interrogation')
        
        # remove dummy entry from master
        try:
            del all_interrogations['None']
        except KeyError:
            pass

        # add interrogation to master
        all_interrogations[the_name] = r

        # total in a way that tkintertable likes
        totals_as_df = pandas.DataFrame(r.totals, dtype = object)

        # update spreadsheets
        if selected_option != 'c':
            update_spreadsheet(interro_results, r.results, height = 260, indexwidth = 70)
        update_spreadsheet(interro_totals, totals_as_df, height = 10, indexwidth = 70)
        
        i_resultname.set('Interrogation results: %s' % the_name)
        refresh()
        #Restore_stdout()
        ##Dbg_kill_topwin()
        # add button after first interrogation

        Button(tab1, text = 'Sort data', command = lambda: data_sort(pane = 'interrogate', sort_direction = sort_direction)).grid(row = 10, column = 2, sticky = W)
        Button(tab1, text = 'Update interrogation', command = lambda: update_all_interrogations(pane = 'interrogate')).grid(row = 10, column = 2, sticky = E)

    class MyOptionMenu(OptionMenu):
        """Simple OptionMenu for things that don't change"""
        def __init__(self, tab1, status, *options):
            self.var = StringVar(tab1)
            self.var.set(status)
            OptionMenu.__init__(self, tab1, self.var, *options)
            self.config(font=('calibri',(12)),width=20)
            self['menu'].config(font=('calibri',(10)))
    
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
        if not fp:
            return
        fullpath.set(fp)
        basepath.set('Corpus: "%s"' % os.path.basename(fp))
        subs = sorted([d for d in os.listdir(fp) if os.path.isdir(os.path.join(fp, d))])
        for k in subcorpora.keys():
            del subcorpora[k]
        subcorpora[fp] = subs
        time = strftime("%H:%M:%S", localtime())
        print '%s: Set corpus directory: %s' % (time, os.path.basename(fp))
    
    Label(tab1, text = 'Corpus directory: ').grid(row = 0, column = 0)
    Button(tab1, textvariable = basepath, command = getdir).grid(row = 0, column = 1, sticky=E)

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
                                ['Get "role:dependent", matching governor',
                                 'Get semantic role of match',
                                 'Get "role:governor", matching dependent',
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
        if chosen == 'Dependencies':
            pick_dep_type.configure(state = NORMAL)

    datatype_picked = StringVar(root)
    datatype_picked.set('Dependencies')
    Label(tab1, text = 'Kind of data:').grid(row = 1, column = 0)
    pick_a_datatype = OptionMenu(tab1, datatype_picked, *tuple(('Trees', 'Dependencies', 'Plaintext')))
    pick_a_datatype.grid(row = 1, column = 1, sticky=E)
    datatype_picked.trace("w", callback)

    datatype_listbox = Listbox(tab1, selectmode = BROWSE, width = 40)
    datatype_listbox.grid(row = 3, column = 0, columnspan = 2)
    datatype_chosen_option = StringVar()
    datatype_chosen_option.set('Get words')
    #datatype_chosen_option.set('w')
    x = datatype_listbox.bind('<<ListboxSelect>>', onselect)
    # hack: change it now to populate below 
    datatype_picked.set('Trees')
    datatype_listbox.select_set(0)

    def q_callback(*args):
        if special_queries.get() == 'Off':
            q.configure(state=NORMAL)
        else:
            q.configure(state=DISABLED)

    entrytext = StringVar()
    Label(tab1, text = 'Query:').grid(row = 4, column = 0, sticky = W)
    entrytext.set(r'JJ > (NP <<# /\brisk/)')
    q = Entry(tab1, textvariable = entrytext, width = 30)
    q.grid(row = 4, column = 0, columnspan = 2, sticky = E)

  

    queries = tuple(('Off', 'Any', 'Participants', 'Processes', 'Subjects'))
    special_queries = StringVar(root)
    special_queries.set('Off')
    Label(tab1, text = 'Preset query:').grid(row = 5, column = 0, sticky = W)
    pick_a_query = OptionMenu(tab1, special_queries, *queries)
    pick_a_query.grid(row = 5, column = 1, sticky=E)
    special_queries.trace("w", q_callback)

    # boolean interrogation arguments
    lem = IntVar()
    Checkbutton(tab1, text="Lemmatise", variable=lem, onvalue = True, offvalue = False).grid(column = 0, row = 6, sticky=W)
    phras = IntVar()
    Checkbutton(tab1, text="Multiword results", variable=phras, onvalue = True, offvalue = False).grid(column = 1, columnspan = 2, row = 6, sticky=W)
    tit_fil = IntVar()
    Checkbutton(tab1, text="Filter titles", variable=tit_fil, onvalue = True, offvalue = False).grid(row = 7, column = 0, sticky=W)
    case_sensitive = IntVar()
    Checkbutton(tab1, text="Case sensitive", variable=case_sensitive, onvalue = True, offvalue = False).grid(row = 7, column = 1, sticky=W)

    Label(tab1, text = 'Normalise spelling:').grid(row = 8, column = 0, sticky = W)
    spl = MyOptionMenu(tab1, 'Off','UK','US')
    spl.grid(row = 8, column = 1)

    # dep type
    dep_types = tuple(('Basic', 'Collapsed', 'Collapsed, CC-processed'))
    kind_of_dep = StringVar(root)
    kind_of_dep.set('Basic')
    Label(tab1, text = 'Dependency type:').grid(row = 9, column = 0, sticky = W)
    pick_dep_type = OptionMenu(tab1, kind_of_dep, *dep_types)
    pick_dep_type.config(state = DISABLED)
    pick_dep_type.grid(row = 9, column = 1, sticky=E)
    #kind_of_dep.trace("w", d_callback)

    # Interrogation name
    nametext = StringVar()
    nametext.set('untitled')
    Label(tab1, text = 'Interrogation name:').grid(row = 10, column = 0, sticky = W)
    Entry(tab1, textvariable = nametext).grid(row = 10, column = 1)

    def query_help():
        tkMessageBox.showwarning('Not yet implemented', 'Coming soon ...')

    # query help, interrogate button
    Button(tab1, text = 'Query help', command = query_help).grid(row = 11, column = 0, sticky = W)
    Button(tab1, text = 'Interrogate!', command = lambda: do_interrogation()).grid(row = 11, column = 1, sticky = E)

    i_resultname = StringVar()
    current_name = ''
    i_resultname.set('Interrogation results: %s' % str(current_name))
    Label(tab1, textvariable = i_resultname, 
          font = ("Helvetica", 12, "bold")).grid(row = 0, 
           column = 2, sticky = W, padx=20, pady=0)    
    interro_results = Frame(tab1, height = 28, width = 20, borderwidth = 2)
    interro_results.grid(column = 2, row = 1, rowspan=7, padx=20, pady=5)

    #Label(tab1, text = 'Interrogation totals:', font = ("Helvetica", 12, "bold")).grid(row = 8, column = 2, sticky = W, padx=20, pady=0)
    interro_totals = Frame(tab1, height = 1, width = 20, borderwidth = 2)
    interro_totals.grid(column = 2, row = 8, rowspan=2, padx=20, pady=5)

    #x = ConsoleText(tab1, width = 20)
    #x.grid(row = 15, column = 0)


    ##############    ##############     ##############     ##############     ############## 
    # EDITOR TAB #    # EDITOR TAB #     # EDITOR TAB #     # EDITOR TAB #     # EDITOR TAB # 
    ##############    ##############     ##############     ##############     ############## 

    def exchange_interro_branch(namedtupname, newdata, branch = 'results'):
        """replaces a namedtuple results/totals with newdata
           --- such a hack, should upgrade to recordtype"""
        
        namedtup = all_interrogations[namedtupname]
        if branch == 'results':
            the_branch = namedtup.results
            the_branch.drop(the_branch.index, inplace = True)
            the_branch.drop(the_branch.columns, axis = 1, inplace = True)
            for i in list(newdata.columns):
                the_branch[i] = i
            for index, i in enumerate(list(newdata.index)):
                the_branch.loc[i] = newdata.ix[index]
        elif branch == 'totals':
            the_branch = namedtup.totals
            the_branch.drop(the_branch.index, inplace = True)
            for index, datum in zip(newdata.index, newdata):
                the_branch.set_value(index, datum)

        all_interrogations[namedtupname] = namedtup

    def update_interrogation(table_id, id, is_total = False):
        """takes any changes made to spreadsheet and saves to the interrogation

        id: 0 = interrogator
            1 = old editor window
            2 = new editor window"""
        # if table doesn't exist, forget about it
        try:
            model=editor_tables[table_id]
        except:
            return

        newdata = make_df_from_model(model)
        if need_make_totals(newdata):
            newdata = make_df_totals(newdata)

        if id == 0:
            name_of_interrogation = all_interrogations.keys()[-1]
        if id == 1:
            name_of_interrogation = data1_pick.get()
        # 1 id for the new data
        if id == 2:
            name_of_interrogation = all_interrogations.keys()[-1]
        if not is_total:
            exchange_interro_branch(name_of_interrogation, newdata, branch = 'results')
        else:
            exchange_interro_branch(name_of_interrogation, newdata, branch = 'totals')

    def update_all_interrogations(pane = 'interrogate'):
        import pandas
        """update all_interrogations within spreadsheet data"""
        # to do: only if they are there
        if pane == 'interrogate':
            update_interrogation(interro_results, id = 0)
            update_interrogation(interro_totals, id = 0, is_total = True)
            if data1_pick.get() == all_interrogations.keys()[-1]:
                update_interrogation(o_editor_results, id = 1)
                update_interrogation(o_editor_totals, id = 1, is_total = True)
        if pane == 'edit':
            the_data = all_interrogations[data1_pick.get()]
            newdata = all_interrogations[all_interrogations.keys()[-1]]
            update_interrogation(o_editor_results, id = 1)
            update_interrogation(o_editor_totals, id = 1, is_total = True)
            update_interrogation(n_editor_results, id = 2)
            update_interrogation(n_editor_totals, id = 2, is_total = True)
            if i_resultname.get() == ('Interrogation results: ' + data1_pick.get()):
                update_interrogation(interro_results, id = 0)
                update_interrogation(interro_totals, id = 0, is_total = True)
        thetime = strftime("%H:%M:%S", localtime())
        print '%s: Updated interrogations with manual data.' % thetime
        if pane == 'interrogate':
            the_data = all_interrogations[data1_pick.get()]
            newdata = all_interrogations[all_interrogations.keys()[-1]]
            tot = pandas.DataFrame(all_interrogations[all_interrogations.keys()[-1]].totals, dtype = object)
            update_spreadsheet(interro_results, all_interrogations[all_interrogations.keys()[-1]].results, height = 260, indexwidth = 70)
            update_spreadsheet(interro_totals, tot, height = 10, indexwidth = 70)
        else:
            update_spreadsheet(o_editor_results, the_data.results, height = 100, indexwidth = 70)
            update_spreadsheet(o_editor_totals, pandas.DataFrame(the_data.totals, dtype = object), height = 10, indexwidth = 70)
            update_spreadsheet(n_editor_results, newdata.results, indexwidth = 70, height = 100)
            update_spreadsheet(n_editor_totals, pandas.DataFrame(newdata.totals, dtype = object), height = 10, indexwidth = 70)
        thetime = strftime("%H:%M:%S", localtime())
        print '%s: Updated spreadsheet display in edit window.' % thetime

    def is_number(s):
        """check if str can be added for the below"""
        try:
            float(s) # for int, long and float
        except ValueError:
            try:
                complex(s) # for complex
            except ValueError:
                return False
        return True

    def update_spreadsheet(frame_to_update, df_to_show = None, model = False, height = 140, width = False, indexwidth = 70, just_default_sort = False):
        """refresh a spreadsheet in the editor window"""
        from collections import OrderedDict
        import pandas
        kwarg = {}
        if width:
            kwarg['width'] = width
        if model:
            df_to_show = make_df_from_model(model)
            if need_make_totals:
                df_to_show = make_df_totals(df_to_show)
        else:
            if just_default_sort is False:    
                # for abs freq, make total
                model = TableModel()
                df_to_show = pandas.DataFrame(df_to_show, dtype = object)
                if need_make_totals(df_to_show):
                    df_to_show = make_df_totals(df_to_show)
                
                # turn pandas into dict
                raw_data = df_to_show.to_dict()

                table = TableCanvas(frame_to_update, model=model, 
                                    showkeynamesinheader=True, 
                                    height = height,
                                    rowheaderwidth=indexwidth,
                                    **kwarg)
                table.createTableFrame()
                model = table.model
                model.importDict(raw_data) #can import from a dictionary to populate model            
                for index, name in enumerate(list(df_to_show.index)):
                    model.moveColumn(model.getColumnIndex(name), index)
                table.createTableFrame()
                if 'tkintertable-order' in list(df_to_show.index):
                    table.sortTable(columnName = 'tkintertable-order')
                    ind = model.columnNames.index('tkintertable-order')
                    try:
                        model.deleteColumn(ind)
                    except:
                        pass
                else:
                    table.sortTable(reverse = 1)
            else:
                table = TableCanvas(frame_to_update, model=model, 
                                    showkeynamesinheader=True, 
                                    height = height,
                                    rowheaderwidth=indexwidth,
                                    **kwarg)
                table.createTableFrame()
                table.sortTable(columnName = 'Total', reverse = direct())

            table.redrawTable()
            editor_tables[frame_to_update] = model
            return
        if model:
            table = TableCanvas(frame_to_update, model=model, 
                                showkeynamesinheader=True, 
                                height = height,
                                rowheaderwidth=indexwidth,
                                **kwarg)
            table.createTableFrame()
            try:
                table.sortTable(columnName = 'Total', reverse = direct())
            except:
                direct()           
                table.sortTable(reverse = direct())
            table.createTableFrame()            # sorts by total freq, ok for now
            table.redrawTable()
        else:
            table = TableCanvas(frame_to_update, height = height, width = width)
            table.createTableFrame()            # sorts by total freq, ok for now
            table.redrawTable()


    def do_editing():
        """what happens when you press edit"""
        #Take_stdout()
        import pandas
        from corpkit import editor
        try:
            del all_edited_results['None']
        except KeyError:
            pass
        # translate operation into interrogator input
        operation_text = opp.get()
        if operation_text == 'None' or operation_text == 'Select an operation':
            operation_text = None
        # translate dataframe2 into interrogator input
        data2 = data2_pick.get()
        if data2 == 'None' or data2 == '' or data2 == 'Self':
            data2 = False

        if data2:
            if df2branch.get() == 'results':
                data2 = all_interrogations[data2].results
            elif df2branch.get() == 'totals':
                data2 = all_interrogations[data2].totals

        the_data = all_interrogations[data1_pick.get()]
        if df1branch.get() == 'results':
            data1 = all_interrogations[data1_pick.get()].results
        # is this wrong?
        elif df1branch.get() == 'totals':
            data1 = all_interrogations[data1_pick.get()].totals

        if (spl_editor.var).get() == 'Off' or (spl_editor.var).get() == 'Convert spelling':
            spel = False
        else:
            spel = (spl_editor.var).get()
        
        # dictionary of all arguments for editor

        editor_args = {'operation': operation_text,
                       'dataframe2': data2,
                       'spelling': spel,
                       'print_info': False}

        if (do_with_subc.var).get() == 'Merge':
            editor_args['merge_subcorpora'] = subc_sel_vals
        elif (do_with_subc.var).get() == 'Keep':
            editor_args['just_subcorpora'] = subc_sel_vals
        elif (do_with_subc.var).get() == 'Span':
            editor_args['span_subcorpora'] = subc_sel_vals
        elif (do_with_subc.var).get() == 'Skip':
            editor_args['skip_subcorpora'] = subc_sel_vals

        if (do_with_entries.var).get() == 'Merge':
            editor_args['merge_entries'] = entry_regex.get()
        elif (do_with_entries.var).get() == 'Keep':
            editor_args['just_entries'] = entry_regex.get()
        elif (do_with_entries.var).get() == 'Skip':
            editor_args['skip_entries'] = entry_regex.get()
        if new_subc_name.get() != '':
            editor_args['new_subcorpus_name'] = new_subc_name.get()
        if new_ent_name.get() != '':
            editor_args['new_subcorpus_name'] = new_ent_name.get()

        sort_trans = {'None': False,
                      'Total': 'total',
                      'Inverse total': 'infreq',
                      'Name': 'name',
                      'Increase': 'increase',
                      'Decrease': 'decrease',
                      'Static': 'static',
                      'Turbulent': 'turbulent'}

        editor_args['sort_by'] = sort_trans[sort_val.get()]
            
        if keep_stats_setting.get() == 1:
            editor_args['keep_stats'] = True

        if just_tot_setting.get() == 1:
            editor_args['just_totals'] = True
        # do editing
        r = editor(data1, **editor_args)

        thetime = strftime("%H:%M:%S", localtime())
        print '%s: Result editing completed successfully.' % thetime
        
        # name the edit
        the_name = namer(edit_nametext.get(), type_of_data = 'edited')

        # add edit to master dict
        all_interrogations[the_name] = r

        # update label above spreadsheet
        #interroname = the_name
        #resultname.set('Results to edit: %s' % str(interroname))   

        # update spreadsheets     
        update_spreadsheet(o_editor_results, the_data.results, height = 100, width = 350)
        update_spreadsheet(o_editor_totals, pandas.DataFrame(the_data.totals, dtype = object), height = 10, width = 350)

        # new editor results
        # update name above
        e_name = all_interrogations.keys()[-1]
        editoname.set('Edited results: %s' % str(e_name))
        
        # add current subcorpora to editor menu
        subc_listbox.delete(0, 'end')
        for e in list(the_data.results.index):
            if 'tkintertable-order' not in e:
                subc_listbox.insert(END, e)

        # update spreadsheets
        update_spreadsheet(n_editor_results, r.results, height = 100, width = 350)
        update_spreadsheet(n_editor_totals, pandas.DataFrame(r.totals, dtype = object), height = 10, width = 350)
        
        # add to edited results
        all_edited_results[the_name] = r
        
        # finish up
        refresh()
        #Restore_stdout()
        #Dbg_kill_topwin()


    def df_callback(*args):
        if data1_pick.get() != 'None':
            update_spreadsheet(o_editor_results, all_interrogations[data1_pick.get()].results, height = 100, width = 350)
            update_spreadsheet(o_editor_totals, all_interrogations[data1_pick.get()].totals, height = 10, width = 350)
            interroname = data1_pick.get()
            resultname.set('Results to edit: %s' % str(interroname))
            #update_spreadsheet(n_editor_results, None, height = 100, width = 350)
            #update_spreadsheet(n_editor_totals, None, height = 10, width = 350)
            # update names above spreadsheets
        e_name = ''
        editoname.set('Edited results: %s' % str(e_name))
        subc_listbox.delete(0, 'end')

        for e in list(all_interrogations[data1_pick.get()].results.index):
            if 'tkintertable-order' not in e:
                subc_listbox.insert(END, e)        

    from collections import OrderedDict
    all_interrogations = OrderedDict()
    all_interrogations['None'] = 'None'

    tup = tuple([i for i in all_interrogations.keys()])
    data1_pick = StringVar(root)
    data1_pick.set(all_interrogations.keys()[0])
    Label(tab2, text = 'To edit:').grid(row = 0, column = 0, sticky = W)
    dataframe1s = OptionMenu(tab2, data1_pick, *tup)
    dataframe1s.grid(row = 0, column = 1, sticky=E)
    data1_pick.trace("w", df_callback)

    # DF1 branch selection
    df1branch = StringVar()
    df1branch.set('results')
    df1box = OptionMenu(tab2, df1branch, 'results', 'totals')
    #df1box.select()
    df1box.grid(row = 0, column = 2, sticky = E)

    def op_callback(*args):
        if opp.get() != 'None':
            dataframe2s.config(state = NORMAL)
            df2box.config(state = NORMAL)
        elif opp.get() == 'None':
            dataframe2s.config(state = DISABLED)
            df2box.config(state = DISABLED)

    # operation for editor
    opp = StringVar(root)
    opp.set('None')
    operations = ('None', '%', '*', '/', '-', '+', 'a', 'd', 'k')
    Label(tab2, text='Operation:').grid(row = 1, column = 0, sticky = W)
    ops = OptionMenu(tab2, opp, *operations)
    ops.grid(row = 1, column = 1, sticky = E)
    opp.trace("w", op_callback)

    # DF2 option for editor
    tups = tuple(['Self'] + [i for i in all_interrogations.keys()])
    data2_pick = StringVar(root)
    data2_pick.set('Self')
    Label(tab2, text = 'Denominator:').grid(row = 3, column = 0, sticky = W)
    dataframe2s = OptionMenu(tab2, data2_pick, *tups)
    dataframe2s.config(state = DISABLED)
    dataframe2s.grid(row = 3, column = 1, sticky = E)

    # DF2 branch selection
    df2branch = StringVar(root)
    df2branch.set('totals')
    df2box = OptionMenu(tab2, df2branch, 'results', 'totals')
    df2box.config(state = DISABLED)
    df2box.grid(row = 3, column = 2, sticky = E)

    Label(tab2, text = 'Sort results by:').grid(row = 4, column = 0, sticky = W)
    sort_val = StringVar(root)
    sort_val.set('None')
    sorts = OptionMenu(tab2, sort_val, 'None', 'Total', 'Inverse total', 'Name','Increase', 'Decrease', 'Static', 'Turbulent')
    #sorts.config(state = DISABLED)
    sorts.grid(row = 4, column = 2, sticky = E)



    Label(tab2, text = 'Spelling:').grid(row = 5, column = 0, sticky = W)
    spl_editor = MyOptionMenu(tab2, 'Off','UK','US')
    spl_editor.grid(row = 5, column = 1, sticky = E)


    # not hooked up yet
    just_tot_setting = IntVar()
    just_tot_but = Checkbutton(tab2, text="Just totals", variable=just_tot_setting, state = DISABLED)
    #just_tot_but.select()
    just_tot_but.grid(column = 0, row = 6)

    # not hooked up yet
    keep_stats_setting = IntVar()
    keep_stat_but = Checkbutton(tab2, text="Keep stats", variable=keep_stats_setting)
    #keep_stat_but.select()
    keep_stat_but.grid(column = 1, row = 6)

    # not hooked up yet
    rem_abv_p_set = IntVar()
    rem_abv_p_but = Checkbutton(tab2, text="Remove above p", variable=rem_abv_p_set)
    #rem_abv_p_but.select()
    rem_abv_p_but.grid(column = 2, row = 6)

    subc_sel_vals = []
    # entries + entry field for regex, off, skip, keep, merge
    Label(tab2, text = 'Entries:').grid(row = 7, column = 0, sticky = W, pady = 5)
    entry_regex = StringVar()
    entry_regex.set('')
    Entry(tab2, textvariable = entry_regex).grid(row = 7, column = 1, sticky = E)
    do_with_entries = MyOptionMenu(tab2, 'Off', 'Skip', 'Keep', 'Merge')
    do_with_entries.grid(row = 7, column = 2, sticky = E)
    Label(tab2, text = 'Merge name:', pady = 10).grid(row = 8, column = 1, sticky = 'NE')
    new_ent_name = StringVar()
    new_ent_name.set('')
    Entry(tab2, textvariable = new_ent_name).grid(row = 8, column = 2, sticky = 'NE')


    def onselect_subc(evt):
        # remove old vals
        for i in subc_sel_vals:
            subc_sel_vals.pop()
        wx = evt.widget
        indices = wx.curselection()
        for index in indices:
            value = wx.get(index)
            if value not in subc_sel_vals:
                subc_sel_vals.append(value)

    # subcorpora + optionmenu off, skip, keep
    Label(tab2, text = 'Subcorpora:').grid(row = 9, column = 0, sticky = W)
    subc_listbox = Listbox(tab2, selectmode = EXTENDED, height = 5)
    subc_listbox.grid(row = 9, column = 1, sticky = E)
    # Set interrogation option
    subc_chosen_option = StringVar()
    #ei_chosen_option.set('w')
    xx = subc_listbox.bind('<<ListboxSelect>>', onselect_subc)
    # default: w option
    subc_listbox.select_set(0)
    do_with_subc = MyOptionMenu(tab2, 'Off', 'Skip', 'Keep', 'Merge', 'Span')
    do_with_subc.grid(row = 9, column = 2, sticky = 'NE')
    Label(tab2, text = 'Merge name:').grid(row = 9, column = 2, sticky = 'E')
    new_subc_name = StringVar()
    new_subc_name.set('')
    Entry(tab2, textvariable = new_subc_name).grid(row = 9, column = 2, sticky = 'SE')

    # edit name
    edit_nametext = StringVar()
    edit_nametext.set('untitled')
    Label(tab2, text = 'Edit name:').grid(row = 10, column = 0, sticky = W)
    Entry(tab2, textvariable = edit_nametext).grid(row = 10, column = 1, sticky = 'news')
    Button(tab2, text = 'Edit', command = lambda: do_editing()).grid(row = 10, column = 2, sticky = E)
    # storage of edited results
    all_edited_results = OrderedDict()
    all_edited_results['None'] = 'None'

    Button(tab2, text = 'Sort data', command = lambda: data_sort(pane = 'edit', sort_direction = sort_direction)).grid(row = 12, column = 3, sticky = E)
    Button(tab2, text = 'Update interrogation(s)', command = lambda: update_all_interrogations(pane = 'edit')).grid(row = 12, column = 3, sticky = E)

    # output
    resultname = StringVar()
    interroname = ''
    resultname.set('Results to edit: %s' % str(interroname))
    Label(tab2, textvariable = resultname, 
          font = ("Helvetica", 12, "bold")).grid(row = 0, 
           column = 3, sticky = W, padx=20, pady=0)    
    o_editor_results = Frame(tab2, height = 15, width = 350)
    o_editor_results.grid(column = 3, row = 1, rowspan=5, padx=20)
    #Label(tab2, text = 'Totals to edit:', 
          #font = ("Helvetica", 12, "bold")).grid(row = 4, 
           #column = 3, sticky = W, padx=20, pady=0)
    o_editor_totals = Frame(tab2, height = 1, width = 350)
    o_editor_totals.grid(column = 3, row = 6, rowspan=1, padx=20)
    
    editoname = StringVar()
    e_name = ''
    editoname.set('Edited results: %s' % str(e_name))
    Label(tab2, textvariable = editoname, 
          font = ("Helvetica", 12, "bold")).grid(row = 7, 
           column = 3, sticky = W, padx=20, pady=0)        
    n_editor_results = Frame(tab2, height = 15, width = 350)
    n_editor_results.grid(column = 3, row = 8, rowspan=3, padx=20)
    #Label(tab2, text = 'Edited totals:', 
          #font = ("Helvetica", 12, "bold")).grid(row = 15, 
           #column = 3, sticky = W, padx=20, pady=0)
    n_editor_totals = Frame(tab2, height = 1, width = 350)
    n_editor_totals.grid(column = 3, row =11, rowspan=1, padx=20)

    # ????
    interrogation_name = StringVar()
    interrogation_name.set('waiting')
    Label(tab1, textvariable = interrogation_name.get()).grid()
    #root.TEXT_INFO = Label(tab1, height=20, width=80, text="", justify = LEFT, font=("Courier New", 12))

    #################       #################      #################      #################  
    # VISUALISE TAB #       # VISUALISE TAB #      # VISUALISE TAB #      # VISUALISE TAB #  
    #################       #################      #################      #################  


    thefig = []

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
        if plotbranch.get() == 'results':
            what_to_plot = all_interrogations[data_to_plot.get()].results
        elif plotbranch.get() == 'totals':
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

        the_kind = charttype.get()
        if the_kind == 'Type of chart':
            the_kind = 'line'
        # plotter options
        d = {'num_to_plot': num,
             'kind': the_kind}

        d['style'] = plot_style.get()

        if texuse.get() == 1:
            d['tex'] = True
        else:
            d['tex'] = False

        if bw.get() == 1:
            d['black_and_white'] = True
        else:
            d['black_and_white'] = False

        if log_x.get() == 1 and log_y.get() == 1:
            d['log'] = 'x,y'
        if log_x.get() == 1 and not log_y.get() == 1:
            d['log'] = 'x'
        if log_y.get() == 1 and not log_x.get() == 1:
            d['log'] = 'y'

        if x_axis_l.get() != '':
            d['x_label'] = x_axis_l.get()
        if x_axis_l.get() == 'None':
            d['x_label'] = False
        if y_axis_l.get() != '':
            d['y_label'] = y_axis_l.get()
        if y_axis_l.get() == 'None':
            d['y_label'] = False

        if chart_cols.get() != 'Default':
            d['colours'] = chart_cols.get()

        legend_loc = legloc.get()
        if legend_loc == 'None':
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

        f = plotter(plotnametext.get(), what_to_plot, **d)
        time = strftime("%H:%M:%S", localtime())
        print '%s: %s plotted.' % (time, plotnametext.get())
        # a Tkinter.DrawingArea
        toolbar_frame = Tkinter.Frame(tab3)
        toolbar_frame.grid(row=12, column=2, columnspan = 3, sticky = N)
        canvas = FigureCanvasTkAgg(f.gcf(), tab3)
        canvas.show()
        canvas.get_tk_widget().grid(column = 2, row = 1, rowspan = 10, padx = 20, columnspan = 3)
        toolbar = NavigationToolbar2TkAgg(canvas,toolbar_frame)
        toolbar.update()
        for i in thefig:
            thefig.pop()
        thefig.append(f.gcf())

    def save_current_image():
        import os
        # figre out filename
        filename = namer(plotnametext.get(), type_of_data = 'image') + '.png'
        import sys
        defaultextension = '.png' if sys.platform == 'darwin' else ''
        kwarg = {'defaultextension': defaultextension,
                 #'filetypes': [('all files', '.*'), 
                               #('png file', '.png')],
                 'initialfile': filename}
        imagedir = image_fullpath.get()
        if imagedir:
            kwarg['initialdir'] = imagedir

        fo = tkFileDialog.asksaveasfilename(**kwarg)

        #fo = tkFileDialog.asksaveasfile(mode='w', defaultextension=".png")
        if fo is None: # asksaveasfile return `None` if dialog closed with "cancel".
            return
        #fo.write(f.gcf())
        #fo.close() # `()` was missing.
        thefig[0].savefig(os.path.join(image_fullpath.get(), fo))
        time = strftime("%H:%M:%S", localtime())
        print '%s: %s saved to %s.' % (time, fo, image_fullpath.get())

    def image_clear():
        thefig[0].get_tk_widget().grid_forget()

    def reset_plotter_pane():
        return

    # title tab
    Label(tab3, text = 'Image title:').grid(row = 0, column = 0, sticky = 'W')
    plotnametext = StringVar()
    plotnametext.set('Untitled')
    Entry(tab3, textvariable = plotnametext).grid(row = 0, column = 1)

    #Label(tab3, text = 'Image:').grid(row = 0, column = 2, padx = 20)

    Label(tab3, text = 'Data to plot:').grid(row = 1, column = 0, sticky = W)
    # select result to plot
    data_to_plot = StringVar(root)
    data_to_plot.set(all_interrogations[all_interrogations.keys()[-1]])
    every_interrogation = OptionMenu(tab3, data_to_plot, *tuple([i for i in all_interrogations.keys()]))
    every_interrogation.grid(column = 0, row = 2, sticky = W, columnspan = 2)

    # branch selection
    plotbranch = StringVar(root)
    plotbranch.set('results')
    plotbox = OptionMenu(tab3, plotbranch, 'results', 'totals')
    #plotbox.config(state = DISABLED)
    plotbox.grid(row = 2, column = 0, sticky = E, columnspan = 2)

    # num_to_plot
    Label(tab3, text = 'Results to show:').grid(row = 3, column = 0, sticky = W)
    number_to_plot = StringVar()
    number_to_plot.set('7')
    Entry(tab3, textvariable = number_to_plot, width = 3).grid(row = 3, column = 1, sticky = E)

    # chart type
    Label(tab3, text='Kind of chart').grid(row = 4, column = 0, sticky = W)
    charttype = StringVar(root)
    charttype.set('line')
    kinds_of_chart = ('line', 'bar', 'barh', 'pie', 'area')
    chart_kind = OptionMenu(tab3, charttype, *kinds_of_chart)
    chart_kind.grid(row = 4, column = 1, sticky = E)

    Label(tab3, text = 'x axis label:').grid(row = 5, column = 0, sticky = W)
    x_axis_l = StringVar()
    x_axis_l.set('')
    Entry(tab3, textvariable = x_axis_l).grid(row = 5, column = 1, sticky = W)

    Label(tab3, text = 'y axis label:').grid(row = 6, column = 0, sticky = W)
    y_axis_l = StringVar()
    y_axis_l.set('')
    Entry(tab3, textvariable = y_axis_l).grid(row = 6, column = 1)

    # log options
    log_x = IntVar()
    Checkbutton(tab3, text="Log x axis", variable=log_x).grid(column = 0, row = 7, sticky = W)
    log_y = IntVar()
    Checkbutton(tab3, text="Log y axis", variable=log_y).grid(column = 1, row = 7, sticky = E)

    bw = IntVar()
    Checkbutton(tab3, text="Black and white", variable=bw).grid(column = 0, row = 8, sticky = W)
    texuse = IntVar()
    Checkbutton(tab3, text="Use TeX", variable=texuse).grid(column = 1, row = 8, sticky = E)

    # chart type
    Label(tab3, text='Colour scheme:').grid(row = 9, column = 0, sticky = W)
    chart_cols = StringVar(root)
    chart_cols.set('Default')
    schemes = tuple(('Default', 'Spectral', 'summer', 'coolwarm', 'Wistia_r', 'pink_r', 'Set1', 'Set2', 
        'Set3', 'brg_r', 'Dark2', 'prism', 'PuOr_r', 'afmhot_r', 'terrain_r', 'PuBuGn_r', 
        'RdPu', 'gist_ncar_r', 'gist_yarg_r', 'Dark2_r', 'YlGnBu', 'RdYlBu', 'hot_r', 
        'gist_rainbow_r', 'gist_stern', 'PuBu_r', 'cool_r', 'cool', 'gray', 'copper_r', 
        'Greens_r', 'GnBu', 'gist_ncar', 'spring_r', 'gist_rainbow', 'gist_heat_r', 'Wistia', 
        'OrRd_r', 'CMRmap', 'bone', 'gist_stern_r', 'RdYlGn', 'Pastel2_r', 'spring', 'terrain', 
        'YlOrRd_r', 'Set2_r', 'winter_r', 'PuBu', 'RdGy_r', 'spectral', 'rainbow', 'flag_r', 
        'jet_r', 'RdPu_r', 'gist_yarg', 'BuGn', 'Paired_r', 'hsv_r', 'bwr', 'cubehelix', 
        'Greens', 'PRGn', 'gist_heat', 'spectral_r', 'Paired', 'hsv', 'Oranges_r', 'prism_r', 
        'Pastel2', 'Pastel1_r', 'Pastel1', 'gray_r', 'jet', 'Spectral_r', 'gnuplot2_r', 
        'gist_earth', 'YlGnBu_r', 'copper', 'gist_earth_r', 'Set3_r', 'OrRd', 'gnuplot_r', 
        'ocean_r', 'brg', 'gnuplot2', 'PuRd_r', 'bone_r', 'BuPu', 'Oranges', 'RdYlGn_r', 'PiYG', 
        'CMRmap_r', 'YlGn', 'binary_r', 'gist_gray_r', 'Accent', 'BuPu_r', 'gist_gray', 'flag', 
        'bwr_r', 'RdBu_r', 'BrBG', 'Reds', 'Set1_r', 'summer_r', 'GnBu_r', 'BrBG_r', 'Reds_r', 
        'RdGy', 'PuRd', 'Accent_r', 'Blues', 'autumn_r', 'autumn', 'cubehelix_r', 
        'nipy_spectral_r', 'ocean', 'PRGn_r', 'Greys_r', 'pink', 'binary', 'winter', 'gnuplot', 
        'RdYlBu_r', 'hot', 'YlOrBr', 'coolwarm_r', 'rainbow_r', 'Purples_r', 'PiYG_r', 'YlGn_r', 
        'Blues_r', 'YlOrBr_r', 'seismic', 'Purples', 'seismic_r', 'RdBu', 'Greys', 'BuGn_r', 
        'YlOrRd', 'PuOr', 'PuBuGn', 'nipy_spectral', 'afmhot'))
    ch_col = OptionMenu(tab3, chart_cols, *schemes)
    ch_col.grid(row = 9, column = 1, sticky = E)

    stys = tuple(('ggplot', 'fivethirtyeights', 'bmh'))
    plot_style = StringVar(root)
    plot_style.set('ggplot')
    Label(tab3, text = 'Plot style:').grid(row = 10, column = 0, sticky = W)
    pick_a_datatype = OptionMenu(tab3, plot_style, *stys)
    pick_a_datatype.grid(row = 10, column = 1, sticky=E)

    # legend pos
    Label(tab3, text='Legend position:').grid(row = 11, column = 0, sticky = W)
    legloc = StringVar(root)
    legloc.set('best')
    locs = tuple(('best', 'outside right', 'upper right', 'right', 'lower right', 'lower left', 'upper left', 'middle', 'none'))
    loc_options = OptionMenu(tab3, legloc, *locs)
    loc_options.grid(row = 11, column = 1, sticky = E)

    # show_totals option
    Label(tab3, text='Show totals: ').grid(row = 12, column = 0, sticky = W)
    showtot = StringVar(root)
    showtot.set('Off')
    showtot_options = tuple(('Off', 'legend', 'plot', 'legend + plot'))
    show_tot_menu = OptionMenu(tab3, showtot, *showtot_options)
    show_tot_menu.grid(row = 12, column = 1, sticky = E)

    # plot button
    Button(tab3, text = 'Plot', command = lambda: do_plotting()).grid(row = 13, column = 1, sticky = E)

    # save image button
    #Button(tab3, text = 'Save image', command = lambda: save_current_image()).grid(column = 2, row = 13)

    # clear image
    #Button(tab3, text = 'Clear image', command = lambda: do_plotting()).grid(column = 3, row = 13)

    # reset pane
    #Button(tab3, text = 'Reset plotter pane', command = lambda: reset_plotter_pane()).grid(column = 4, row = 13)


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
             'n': 'all',
             'print_status': False,
             'print_output': False}
        time = strftime("%H:%M:%S", localtime())
        print '%s: Concordancing in progress ... ' % (time, fo, image_fullpath.get())        
        r = conc(corpus, query, **d)
        time = strftime("%H:%M:%S", localtime())
        print '%s: Concordancing done ... ' % (time, fo, image_fullpath.get())
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
        from corpkit import load_all_results
        #Take_stdout()
        r = load_all_results(data_dir = data_fullpath.get(), root = root)
        #Restore_stdout()

        for name, loaded in r.items():
            all_interrogations[name] = loaded
        #Dbg_kill_topwin()
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
        if not fp:
            return
        data_fullpath.set(fp)
        data_basepath.set('Saved data: "%s"' % os.path.basename(fp))
        #fs = sorted([d for d in os.listdir(fp) if os.path.isfile(os.path.join(fp, d))])
        time = strftime("%H:%M:%S", localtime())
        print '%s: Set data directory: %s' % (time, os.path.basename(fp))
    
    # corpus path setter
    image_fullpath = StringVar()
    image_fullpath.set('/users/danielmcdonald/documents/work/risk/images')
    image_basepath = StringVar()
    image_basepath.set('Select image directory')

    def image_getdir():
        fp = tkFileDialog.askdirectory()
        if not fp:
            return
        image_fullpath.set(fp)
        image_basepath.set('Images: "%s"' % os.path.basename(fp))
        time = strftime("%H:%M:%S", localtime())
        print '%s: Set image directory: %s' % (time, os.path.basename(fp))

    #Label(tab5, text = 'Data directory: ').grid(sticky = W, row = 0, column = 0)
    Button(tab5, textvariable = data_basepath, command = data_getdir).grid(row = 0, column = 0, sticky=E)
    #Label(tab5, text = 'Image directory: ').grid(sticky = W, row = 1, column = 0)
    Button(tab5, textvariable = image_basepath, command = image_getdir).grid(row = 1, column = 0, sticky=E)
    #Label(tab5, text = 'Get saved interrogations: ').grid(sticky = W, row = 2, column = 0)
    Button(tab5, text = 'Get saved interrogations', command = get_saved_results).grid(row = 2, column = 0, sticky=E)

    def save_one_or_more():
        if len(sel_vals) == 0:
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: No interrogations selected.' % thetime
            return
        from corpkit import save_result
        import os
        saved = 0
        existing = 0
        for i in sel_vals:
            if i + '.p' not in os.listdir(data_fullpath.get()):
                save_result(all_interrogations[i], urlify(i) + '.p', savedir = data_fullpath.get())
                saved += 1
            else:
                existing += 1
                thetime = strftime("%H:%M:%S", localtime())
                print '%s: File already exists in %s.' % (thetime, os.path.basename(data_fullpath.get()))   
        thetime = strftime("%H:%M:%S", localtime())
        if saved == 1 and existing == 0:
            print '%s: %s saved.' % (thetime, sel_vals[0])
        else:
            if existing == 0:
                print '%s: %d interrogations saved.' % (thetime, len(sel_vals))
            else:
                print '%s: %d interrogations saved, %d already existed' % (thetime, saved, existing)
        refresh()

    def remove_one_or_more():
        if len(sel_vals) == 0:
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: No interrogations selected.' % thetime
            return
        for i in sel_vals:
            try:
                del all_interrogations[i]
            except:
                pass
        thetime = strftime("%H:%M:%S", localtime())
        if len(sel_vals) == 1:
            print '%s: %s removed.' % (thetime, sel_vals[0])
        else:
            print '%s: %d interrogations removed.' % (thetime, len(sel_vals))
        refresh()

    def del_one_or_more():
        if len(sel_vals) == 0:
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: No interrogations selected.' % thetime
            return
        import os
        result = tkMessageBox.askquestion("Are You Sure?", "Permanently delete the following files:\n\n    %s" % '\n    '.join(sel_vals), icon='warning')
        if result == 'yes':
            for i in sel_vals:
                try:
                    del all_interrogations[i]
                    os.remove(os.path.join(data_fullpath.get(), i + '.p'))
                except:
                    pass
        thetime = strftime("%H:%M:%S", localtime())
        if len(sel_vals) == 1:
            print '%s: %s deleted.' % (thetime, sel_vals[0])
        else:
            print '%s: %d interrogations deleted.' % (thetime, len(sel_vals))
        refresh()

    def urlify(s):
        "Turn title into filename"
        import re
        s = s.lower()
        s = re.sub(r"[^\w\s-]", '', s)
        s = re.sub(r"\s+", '-', s)
        s = re.sub(r"-(textbf|emph|textsc|textit)", '-', s)
        return s

    def rename_one_or_more():
        if perm.get():
            import os
            perm_text = 'permanently '
        else:
            perm_text = ''
        for i in sel_vals:
            answer = tkSimpleDialog.askstring('Rename', 'Choose a new name for "%s":' % i)
            if answer is None or answer == '':
                continue
            else:
                all_interrogations[answer] = all_interrogations.pop(i)
            if perm.get():
                p = data_fullpath.get()
                oldf = os.path.join(p, i + '.p')
                if os.path.isfile(oldf):
                    newf = os.path.join(p, urlify(answer) + '.p')
                    os.rename(oldf, newf)
        thetime = strftime("%H:%M:%S", localtime())
        if len(sel_vals) == 1:
            print '%s: %s %srenamed as %s.' % (thetime, sel_vals[0], perm_text, answer)
        print '%s: %d interrogations %srenamed.' % (thetime, len(sel_vals), perm_text)
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
    every_interro_listbox.grid(sticky = E, column = 0, row = 3)
    # Set interrogation option
    ei_chosen_option = StringVar()
    #ei_chosen_option.set('w')
    xx = every_interro_listbox.bind('<<ListboxSelect>>', onselect_interro)
    # default: w option
    every_interro_listbox.select_set(0)

    #Label(tab5, text = 'Remove selected: ').grid(sticky = W, row = 4, column = 0)
    Button(tab5, text="Remove", 
           command=remove_one_or_more).grid(sticky = E, column = 0, row = 4)
    #Label(tab5, text = 'Delete selected: ').grid(sticky = E, row = 5, column = 0)
    Button(tab5, text = 'Delete', command = del_one_or_more).grid(sticky = E, column = 0, row = 5)
    #Label(tab5, text = 'Save selected: ').grid(sticky = E, row = 6, column = 0)
    Button(tab5, text = 'Save', command = save_one_or_more).grid(sticky = E, column = 0, row = 6)
    Button(tab5, text = 'Rename', command = rename_one_or_more).grid(sticky = E, column = 0, row = 7)
    perm = IntVar()
    Checkbutton(tab5, text="Permanently", variable=perm, onvalue = True, offvalue = False).grid(column = 0, row = 7, sticky=W)
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

    note.focus_on(tab1)
    root.mainloop()

if __name__ == "__main__":
    corpkit_gui()

