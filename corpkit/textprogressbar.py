#!/usr/bin/python

from __future__ import print_function

class TextProgressBar:
    """a text progress bar for CLI operations
       no need for user to call"""
    from time import localtime, strftime
        
    def __init__(self, iterations, dirname = False):
        from time import localtime, strftime
        self.iterations = iterations
        self.prog_bar = '[]'
        self.fill_char = '*'
        self.width = 60
        self.__update_amount(0, dirname = dirname)
        self.animate = self.animate_ipython

    def animate_ipython(self, iter, dirname = None):
        from time import localtime, strftime
        import sys
        print(str(self) + '\r', end='')
        try:
            sys.stdout.flush()
        except:
            pass
        self.update_iteration(iter + 1, dirname)

    def update_iteration(self, elapsed_iter, dirname = None):
        from time import localtime, strftime
        num = float(self.iterations)
        if num != 0:
            self.__update_amount((elapsed_iter / float(self.iterations)) * 100.0, dirname)
        else:
            self.__update_amount(0 * 100.0, dirname)
        self.prog_bar += ' ' # + ' %d of %s complete' % (elapsed_iter, self.iterations)

    def __update_amount(self, new_amount, dirname = None):
        from time import localtime, strftime
        percent_done = int(round((new_amount / 100.0) * 100.0, 2))
        all_full = self.width - 2
        num_hashes = int(round((percent_done / 100.0) * all_full))
        time = strftime("%H:%M:%S", localtime())
        self.prog_bar = time + ': [' + self.fill_char * num_hashes + ' ' * (all_full - num_hashes) + ']'
        
        if dirname:
            pct_string = '%d%% ' % percent_done + '(' + dirname + ')'
        else:
            pct_string = '%d%%' % percent_done # could pass dirname here!
        # find out where the index of the first space in the middle string
        index_of_space = next((i for i, j in enumerate(pct_string) if j.isspace()), 0)
        
        # put middle string in centre, adjust so that spaces are always aligned
        pct_place = int(len(self.prog_bar) / float(2)) - index_of_space
        #if len(pct_string) < 20:
            #pct_string = ' ' * (20 - len(pct_string)) + pct_string
        self.prog_bar = self.prog_bar[0:pct_place] + \
           (pct_string + self.prog_bar[pct_place + len(pct_string):])

    def __str__(self):
        return str(self.prog_bar)