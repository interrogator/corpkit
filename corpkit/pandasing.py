# a file for working with dataframes. most importantly, make a dataframe plotter.


def pplotter(
    title,
    dataframe,
    num_to_plot = 7,
    only_totals = False,
    x_label = False,
    y_label = False,
    legend = 'default',
    style = 'ggplot',
    log = False,
    save = False):
    """Take a Pandas dataframe and plot it"""

    def urlify_title(title):
        import re
        new_title = title.lower()
        new_title = re.sub(r"[^\w\s]", '', new_title)
        new_title = re.sub(r"\s+", '-', new_title)
        return new_title


    def smart_axis_labeller():
    	if not x_label:

    	if not y_label:


    def projector(subcorpus_name, multiplier):
    	"""project subcorpus_name by multiplier"""

    	return projected

    def edit_entry_name(oldname):
        if legend == 'total':
            entry_addition = u' (n=%d)' % abs_freq
        elif legend == 'perc':
            entry_addition = u' (%d\%)' % percentage
        elif legend == 'p_value'
            entry_addition = u' (p=%d)' % p_val
        else:
            raise ValueError('legend = %s not recognised.' % legend)
        newname = oldname + entry_addition
        return newname

    def make_barchart():

    def make_line_chart():

    def logscaler():
        plt.gca().get_xaxis().set_major_locator(MaxNLocator(integer=True))
        if log == 'x':
            plt.xscale('log')
            plt.gca().get_xaxis().set_major_formatter(ScalarFormatter())
        elif log == 'y':
            plt.yscale('log')
            plt.gca().get_yaxis().set_major_formatter(ScalarFormatter())
        elif log.startswith('x') and log.endswith('y'):
            plt.xscale('log')
            plt.gca().get_xaxis().set_major_formatter(ScalarFormatter())
            plt.yscale('log')
            plt.gca().get_yaxis().set_major_formatter(ScalarFormatter())
        else:
            plt.ticklabel_format(useOffset=False, axis='x', style = 'plain')












def pconc():
    return concordance

def pquickview(lst, n = 50):
    import pandas as pd
    from StringIO import StringIO
    csv = ['word,total']
    for w in list(lst.index)[:n]:
        tot = lst.T[w][-1]
        line = [str(w), str(tot)]
        line = ','.join(line)
        csv.append(line)
    csv = '\n'.join(csv)
    tab = pd.read_csv(StringIO(csv))
    tab.reset_index()
    return tab