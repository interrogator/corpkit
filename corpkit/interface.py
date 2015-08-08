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
        """Creates a new tab, and returns it's corresponding frame

        """
        
        temp = self.tabs                                                                   #Temp is used so that the value of self.tabs will not throw off the argument sent by the label's event binding
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

def demo():
    import Tkinter, Tkconstants, tkFileDialog
    from Tkinter import StringVar, Listbox, Text
    import sys
    import threading
    #from corpkit import interrogator, editor, plotter

    def adjustCanvas(someVariable = None):
        fontLabel["font"] = ("arial", var.get())
    
    root = Tk()
    root.title("corpkit gui")
    note = Notebook(root, width= 1600, height =800, activefg = 'red', inactivefg = 'blue')  #Create a Note book Instance
    note.grid()
    tab1 = note.add_tab(text = "Interrogate")                                                  #Create a tab with the text "Tab One"
    tab2 = note.add_tab(text = "Edit")                                                  #Create a tab with the text "Tab Two"
    tab3 = note.add_tab(text = "Visualise")                                                #Create a tab with the text "Tab Three"
    tab4 = note.add_tab(text = "Concordance")                                                 #Create a tab with the text "Tab Four"
    tab5 = note.add_tab(text = "Other")                                                 #Create a tab with the text "Tab Five"
    Label(tab1, text = 'Tab one').grid(row = 0, column = 0)                                #Use each created tab as a parent, etc etc...
    

    c = 0

    # corpus path setter
    fullpath = StringVar()
    #fullpath.set('users/danielmcdonald/documents/work/risk/data/nyt/sample')
    basepath = StringVar()
    basepath.set('Select corpus path')
    def getdir():
        import os
        fp = tkFileDialog.askdirectory()
        fullpath.set(fp)
        basepath.set('Corpus: "%s"' % os.path.basename(fp))
    Button(tab1, textvariable = basepath, command = getdir).grid()

    # options
    chosen_option = StringVar()
    chosen_option.set('w')
    def onselect(evt):
        # Note here that Tkinter passes an event object to onselect()
        w = evt.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        chosen_option.set(value)
    listbox = Listbox(tab1, selectmode = BROWSE)
    listbox.grid()
    for item in ['w', 'g', 't']:
        listbox.insert(END, item)
    x = listbox.bind('<<ListboxSelect>>', onselect)
    listbox.select_set(0)

    # query
    entrytext = StringVar()
    entrytext.set('any')
    Entry(tab1, textvariable = entrytext).grid()

    # name
    nametext = StringVar()
    nametext.set('interrogation name')
    Entry(tab1, textvariable = nametext).grid()

    class MyOptionMenu(OptionMenu):
        def __init__(self, tab1, status, *options):
            self.var = StringVar(tab1)
            self.var.set(status)
            OptionMenu.__init__(self, tab1, self.var, *options)
            self.config(font=('calibri',(12)),width=20)
            self['menu'].config(font=('calibri',(10)))
    
    data1_pick = StringVar(root)
    data1_pick.set("Select an interrogation")
    from collections import OrderedDict
    all_interrogations = OrderedDict()
    all_interrogations['None'] = 'sorry'

    def get_saved_results():
        from corpkit import load_result
        r = load_all_results()

    def do_interrogation():

        def refresh():
            # Reset data1_pick and delete all old options
            data1_pick.set(all_interrogations.keys()[-1])
            #data2_pick.set(all_interrogations.keys()[-1])
            dataframe1s['menu'].delete(0, 'end')
            dataframe2s['menu'].delete(0, 'end')
            # Insert list of new options (tk._setit hooks them up to data1_pick)
            new_choices = ['Select an interrogation']
            for interro in all_interrogations.keys():
                new_choices.append(interro)
            new_choices = tuple(new_choices)
            for choice in new_choices:
                dataframe1s['menu'].add_command(label=choice, command=Tkinter._setit(data1_pick, choice))
                dataframe2s['menu'].add_command(label=choice, command=Tkinter._setit(data2_pick, choice))

        from corpkit import interrogator
        root.TEXT_INFO = Label(tab1, height=20, width=80, text="", justify = LEFT, font=("Courier New", 12))
        root.TEXT_INFO.grid(column=1, row = 1)
        conv = (spl.var).get()
        if conv == 'Convert spelling' or conv == 'Off':
            conv = False
        interrogator_args = {'query': entrytext.get(),
                         'lemmatise': lem.get(),
                         'phrases': phras.get(),
                         'titlefilter': tit_fil.get(),
                         'convert_spelling': conv
                         }
        sys.stdout = StdoutRedirector(root.TEXT_INFO)
        r = interrogator('/users/danielmcdonald/documents/work/risk/data/nyt/sample', chosen_option.get(), **interrogator_args)
        # when not testing:
        #r = interrogator(fullpath.get(), chosen_option.get(), **interrogator_args)
        df = r.results.T.head(10).T
        print df
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


    dataframe1s = OptionMenu(tab2, data1_pick, *tuple([i for i in all_interrogations.keys()]))
    dataframe1s.grid()  

    # boolean interrogation arguments
    lem = IntVar()
    Checkbutton(tab1, text="Lemmatise", variable=lem, onvalue = True, offvalue = False).grid()
    phras = IntVar()
    Checkbutton(tab1, text="Phrases", variable=phras, onvalue = True, offvalue = False).grid()
    tit_fil = IntVar()
    Checkbutton(tab1, text="Filter titles", variable=tit_fil, onvalue = True, offvalue = False).grid()
    

    operations = ('None', '%', '*', '/', '-', '+', 'a', 'd', 'k')
    l =  ['Select an operation'] + [i for i in operations]
    ops = MyOptionMenu(tab2, 'Select an operation', *operations)
    ops.grid()

    data2_pick = StringVar(root)
    data2_pick.set('Pick something to combine with.')
    dataframe2s = OptionMenu(tab2, data2_pick, *tuple([i for i in all_interrogations.keys()]))
    dataframe2s.grid()

    df2branch = IntVar()
    Checkbutton(tab2, text="Use results branch of df2?", variable=df2branch, onvalue = 'results', offvalue = 'totals').grid()

    def do_editing():
        from corpkit import editor
        operation_text = (ops.var).get()
        if operation_text == 'None' or operation_text == 'Select an operation':
            operation_text = None
        data2 = data2_pick.get()
        if data2_pick == 'None' or data2_pick == 'Pick something to combine with.':
            data2 = False
        if data2:
            if df2branch == 'results':
                data2 = data2.results
            elif df2branch == 'totals':
                data2 = data2.totals
        editor_args = {'dataframe1': all_interrogations[data1_pick.get()],
                         'operation': operation_text,
                         'dataframe2': data2 
                         }
        edited = editor(editor_args['dataframe1'].results, editor_args['operation'])
        print edited.results.head(5).T.head(5).T.to_string()

    spl = MyOptionMenu(tab1, 'Convert spelling', 'Off','UK','US')
    spl.grid()

    Button(tab1, text = 'Interrogate!', command = lambda: do_interrogation()).grid()
    Button(tab2, text = 'Edit', command = lambda: do_editing()).grid()
    interrogation_name = StringVar()
    interrogation_name.set('waiting')
    Label(tab1, textvariable = interrogation_name.get()).grid()
    #root.TEXT_INFO = Label(tab1, height=20, width=80, text="", justify = LEFT, font=("Courier New", 12))
    
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
    Button(tab3, text = 'Destroy Tab Four!', command = lambda:note.destroy_tab(tab4)).grid()
    Label(tab3, text = "Destroying a tab will remove it,\nand competely destoy all child widgets.\nOnce you destroy a tab, you have to recreate it\ncompletely in order to get it back.", font = ("Comic Sans MS", 12, "italic")).grid()
    Label(tab4, text = 'Tab 4').grid()
    Button(tab5, text = 'Tab One', command = lambda:note.focus_on(tab1)).grid(pady = 3)
    Button(tab5, text = 'EXIT', width = 23, command = root.destroy).grid()
    note.focus_on(tab1)
    root.mainloop()

if __name__ == "__main__":
    demo()

