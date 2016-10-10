"""
corpkit: edit Interrogation, Concordance and Interrodict objects
"""
from __future__ import print_function
from corpkit.constants import STRINGTYPE, PYTHON_VERSION

def editor(interrogation, 
           operation=None,
           denominator=False,
           sort_by=False,
           keep_stats=False,
           keep_top=False,
           just_totals=False,
           threshold='medium',
           just_entries=False,
           skip_entries=False,
           span_entries=False,
           merge_entries=False,
           just_subcorpora=False,
           skip_subcorpora=False,
           span_subcorpora=False,
           merge_subcorpora=False,
           replace_names=False,
           replace_subcorpus_names=False,
           projection=False,
           remove_above_p=False,
           p=0.05, 
           print_info=False,
           spelling=False,
           selfdrop=True,
           calc_all=True,
           keyword_measure='ll',
           **kwargs
          ):
    """
    See corpkit.interrogation.Interrogation.edit() for docstring
    """

    # grab arguments, in case we get dict input and have to iterate
    locs = locals()

    import corpkit

    import re
    import collections
    import pandas as pd
    import numpy as np

    from pandas import DataFrame, Series
    from time import localtime, strftime
    
    try:
        get_ipython().getoutput()
    except TypeError:
        have_ipython = True
    except NameError:
        have_ipython = False
    try:
        from IPython.display import display, clear_output
    except ImportError:
        pass
    # new ipython error
    except AttributeError:
        have_ipython = False
        pass

    # to use if we also need to worry about concordance lines
    return_conc = False

    from corpkit.interrogation import Interrodict, Interrogation, Concordance
    if interrogation.__class__ == Interrodict:
        locs.pop('interrogation', None)
        from collections import OrderedDict
        outdict = OrderedDict()
        for i, (k, v) in enumerate(interrogation.items()):
            # only print the first time around
            if i != 0:
                locs['print_info'] = False

            if isinstance(denominator, STRINGTYPE) and denominator.lower() == 'self':
                denominator = interrogation

            # if df2 is also a dict, get the relevant entry

            if isinstance(denominator, (dict, Interrodict)):
                #if sorted(set([i.lower() for i in list(dataframe1.keys())])) == \
                #   sorted(set([i.lower() for i in list(denominator.keys())])):
                #   locs['denominator'] = denominator[k]

                # fix: this repeats itself for every key, when it doesn't need to
                # denominator_sum: 
                if kwargs.get('denominator_sum'):
                    locs['denominator'] = denominator.collapse(axis='key')

                if kwargs.get('denominator_totals'):
                    locs['denominator'] = denominator[k].totals
                else:
                    locs['denominator'] = denominator[k].results


            outdict[k] = v.results.edit(**locs)
        if print_info:
            
            thetime = strftime("%H:%M:%S", localtime())
            print("\n%s: Finished! Output is a dictionary with keys:\n\n         '%s'\n" % (thetime, "'\n         '".join(sorted(outdict.keys()))))
        return Interrodict(outdict)

    elif isinstance(interrogation, (DataFrame, Series)):
        dataframe1 = interrogation
    elif isinstance(interrogation, Interrogation):
        #if interrogation.__dict__.get('concordance', None) is not None:
        #    concordances = interrogation.concordance
        branch = kwargs.pop('branch', 'results')
        if branch.lower().startswith('r') :
            dataframe1 = interrogation.results
        elif branch.lower().startswith('t'):
            dataframe1 = interrogation.totals
        elif branch.lower().startswith('c'):
            dataframe1 = interrogation.concordance
            return_conc = True
        else:
            dataframe1 = interrogation.results
    
    elif isinstance(interrogation, Concordance) or \
                        all(x in list(dataframe1.columns) for x in [ 'l', 'm', 'r']):
        return_conc = True
        print('heree')
        dataframe1 = interrogation
    # hope for the best
    else:
        dataframe1 = interrogation

    the_time_started = strftime("%Y-%m-%d %H:%M:%S")

    pd.options.mode.chained_assignment = None

    try:
        from process import checkstack
    except ImportError:
        from corpkit.process import checkstack
        
    if checkstack('pythontex'):
        print_info=False

    def combiney(df, df2, operation='%', threshold='medium', prinf=True):
        """
        Mash df and df2 together in appropriate way
        """
        totals = False
        # delete under threshold
        if just_totals:
            if using_totals:
                if not single_totals:
                    to_drop = list(df2[df2['Combined total'] < threshold].index)
                    df = df.drop([e for e in to_drop if e in list(df.index)])
                    if prinf:
                        to_show = []
                        [to_show.append(w) for w in to_drop[:5]]
                        if len(to_drop) > 10:
                            to_show.append('...')
                            [to_show.append(w) for w in to_drop[-5:]]
                        if len(to_drop) > 0:
                            print('Removing %d entries below threshold:\n    %s' % (len(to_drop), '\n    '.join(to_show)))
                        if len(to_drop) > 10:
                            print('... and %d more ... \n' % (len(to_drop) - len(to_show) + 1))
                        else:
                            print('')
                else:
                    denom = df2
        else:
            denom = list(df2)
        if single_totals:
            if operation == '%':
                totals = df.sum() * 100.0 / float(df.sum().sum())
                df = df * 100.0
                try:
                    df = df.div(denom, axis=0)
                except ValueError:
                    
                    thetime = strftime("%H:%M:%S", localtime())
                    print('%s: cannot combine DataFrame 1 and 2: different shapes' % thetime)
            elif operation == '+':
                try:
                    df = df.add(denom, axis=0)
                except ValueError:
                    
                    thetime = strftime("%H:%M:%S", localtime())
                    print('%s: cannot combine DataFrame 1 and 2: different shapes' % thetime)
            elif operation == '-':
                try:
                    df = df.sub(denom, axis=0)
                except ValueError:
                    
                    thetime = strftime("%H:%M:%S", localtime())
                    print('%s: cannot combine DataFrame 1 and 2: different shapes' % thetime)
            elif operation == '*':
                totals = df.sum() * float(df.sum().sum())
                try:
                    df = df.mul(denom, axis=0)
                except ValueError:
                    
                    thetime = strftime("%H:%M:%S", localtime())
                    print('%s: cannot combine DataFrame 1 and 2: different shapes' % thetime)
            elif operation == '/':
                try:
                    totals = df.sum() / float(df.sum().sum())
                    df = df.div(denom, axis=0)
                except ValueError:
                    
                    thetime = strftime("%H:%M:%S", localtime())
                    print('%s: cannot combine DataFrame 1 and 2: different shapes' % thetime)

            elif operation == 'a':
                for c in [c for c in list(df.columns) if int(c) > 1]:
                    df[c] = df[c] * (1.0 / int(c))
                df = df.sum(axis=1) / df2
            
            elif operation.startswith('c'):
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    df = pandas.concat([df, df2], axis=1)
            return df, totals

        elif not single_totals:
            if not operation.startswith('a'):
                # generate totals
                if operation == '%':
                    totals = df.sum() * 100.0 / float(df2.sum().sum())
                if operation == '*':
                    totals = df.sum() * float(df2.sum().sum())
                if operation == '/':
                    totals = df.sum() / float(df2.sum().sum())
                if operation.startswith('c'):
                    # add here the info that merging will not work 
                    # with identical colnames
                    import warnings
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        d = pd.concat([df.T, df2.T])
                        # make index nums
                        d = d.reset_index()
                        # sum and remove duplicates
                        d = d.groupby('index').sum()
                        dx = d.reset_index('index')
                        dx.index = list(dx['index'])
                        df = dx.drop('index', axis=1).T

                def editf(datum):
                    meth = {'%': datum.div,
                            '*': datum.mul,
                            '/': datum.div,
                            '+': datum.add,
                            '-': datum.sub}

                    if datum.name in list(df2.columns):

                        method = meth[operation]
                        mathed = method(df2[datum.name], fill_value=0.0)
                        if operation == '%':
                            return mathed * 100.0
                        else:
                            return mathed
                    else:
                        return datum * 0.0

                df = df.apply(editf)

            else:
                for c in [c for c in list(df.columns) if int(c) > 1]:
                    df[c] = df[c] * (1.0 / int(c))
                df = df.sum(axis=1) / df2.T.sum()

        return df, totals

    def skip_keep_merge_span(df):
        """
        Do all skipping, keeping, merging and spanning
        """
        from corpkit.dictionaries.process_types import Wordlist
        if skip_entries:
            if isinstance(skip_entries, (list, Wordlist)):
                df = df.drop(list(skip_entries), axis=1, errors='ignore')
            else:
                df = df.loc[:,~df.columns.str.contains(skip_entries)]
        if just_entries:
            if isinstance(just_entries, (list, Wordlist)):
                je = [i for i in list(just_entries) if i in list(df.columns)]
                df = df[je]
            else:
                df = df.loc[:,df.columns.str.contains(just_entries)]
        if merge_entries:
            for newname, crit in merge_entries.items():
                if isinstance(crit, (list, Wordlist)):
                    crit = [i for i in list(crit) if i in list(df.columns)]
                    cr = [i for i in list(crit) if i in list(df.columns)]
                    summed = df[cr].sum(axis=1)
                    df = df.drop(list(cr), axis=1, errors='ignore')
                else:
                    summed = df.loc[:,df.columns.str.contains(crit)].sum(axis=1)
                    df = df.loc[:,~df.columns.str.contains(crit)]
                df.insert(0, newname, summed, allow_duplicates=True)
        if span_entries:
            df = df.iloc[:,span_entries[0]:span_entries[1]]
        if skip_subcorpora:
            if isinstance(skip_subcorpora, (list, Wordlist)):
                df = df.drop(list(skip_subcorpora), axis=0, errors='ignore')
            else:
                df = df[~df.index.str.contains(skip_subcorpora)]
        if just_subcorpora:
            if isinstance(just_subcorpora, (list, Wordlist)):
                js = [i for i in list(just_subcorpora) if i in list(df.index)]
                df = df.loc[js]
            else:
                df = df[df.index.str.contains(just_subcorpora)]
        if merge_subcorpora:
            df = df.T
            for newname, crit in merge_subcorpora.items():
                if isinstance(crit, (list, Wordlist)):
                    crit = [i for i in list(crit) if i in list(df.columns)]
                    summed = df[list(crit)].sum(axis=1)
                    df = df.drop(list(crit), axis=1, errors='ignore')
                else:
                    summed = df.loc[:,df.columns.str.contains(crit)].sum(axis=1)
                    df = df.loc[:,~df.columns.str.contains(crit)]                
                df.insert(0, newname, summed, allow_duplicates=True)
            df = df.T
        if span_subcorpora:
            df = df.iloc[span_subcorpora[0]:span_subcorpora[1],:]
        return df

    def parse_input(df, the_input):
        """turn whatever has been passed in into list of words that can 
           be used as pandas indices---maybe a bad way to go about it"""
        parsed_input = False
        import re
        if the_input == 'all':
            the_input = r'.*'
        if isinstance(the_input, int):
            try:
                the_input = str(the_input)
            except:
                pass
            the_input = [the_input]
        elif isinstance(the_input, STRINGTYPE):
            regex = re.compile(the_input)
            parsed_input = [w for w in list(df) if re.search(regex, w)]
            return parsed_input
        from corpkit.dictionaries.process_types import Wordlist
        if isinstance(the_input, Wordlist) or the_input.__class__ == Wordlist:
            the_input = list(the_input)
        if isinstance(the_input, list):
            if isinstance(the_input[0], int):
                parsed_input = [word for index, word in enumerate(list(df)) if index in the_input]
            elif isinstance(the_input[0], STRINGTYPE):
                try:
                    parsed_input = [word for word in the_input if word in df.columns]
                except AttributeError: # if series
                    parsed_input = [word for word in the_input if word in df.index]
        return parsed_input

    def synonymise(df, pos='n'):
        """pass a df and a pos and convert df columns to most common synonyms"""
        from nltk.corpus import wordnet as wn
        #from dictionaries.taxonomies import taxonomies
        from collections import Counter
        fixed = []
        for w in list(df.columns):
            try:
                syns = []
                for syns in wn.synsets(w, pos=pos):
                    for w in syns:
                        synonyms.append(w)
                top_syn = Counter(syns).most_common(1)[0][0]
                fixed.append(top_syn)
            except:
                fixed.append(w)
        df.columns = fixed
        return df

    def convert_spell(df, convert_to='US', print_info=print_info):
        """turn dataframes into us/uk spelling"""
        from dictionaries.word_transforms import usa_convert
        if print_info:
            print('Converting spelling ... \n')
        if convert_to == 'UK':
            usa_convert = {v: k for k, v in list(usa_convert.items())}
        fixed = []
        for val in list(df.columns):
            try:
                fixed.append(usa_convert[val])
            except:
                fixed.append(val)
        df.columns = fixed
        return df

    def merge_duplicates(df, print_info=print_info):
        if print_info:
            print('Merging duplicate entries ... \n')
        # now we have to merge all duplicates
        for dup in df.columns.get_duplicates():
            #num_dupes = len(list(df[dup].columns))
            temp = df[dup].sum(axis=1)
            #df = df.drop([dup for d in range(num_dupes)], axis=1)
            df = df.drop(dup, axis=1)
            df[dup] = temp
        return df

    def name_replacer(df, replace_names, print_info=print_info):
        """replace entry names and merge"""
        import re
        # get input into list of tuples
        # if it's a string, we want to delete it
        if isinstance(replace_names, STRINGTYPE):
            replace_names = [(replace_names, '')]
        # this is for some malformed list
        if not isinstance(replace_names, dict):
            if isinstance(replace_names[0], STRINGTYPE):
                replace_names = [replace_names]
        # if dict, make into list of tupes
        if isinstance(replace_names, dict):
            replace_names = [(v, k) for k, v in replace_names.items()]
        for to_find, replacement in replace_names:
            if print_info:
                if replacement:
                    print('Replacing "%s" with "%s" ...\n' % (to_find, replacement))
                else:
                    print('Deleting "%s" from entry names ...\n' % to_find)
            to_find = re.compile(to_find)
            if not replacement:
                replacement = ''
            df.columns = [re.sub(to_find, replacement, l) for l in list(df.columns)]
        df = merge_duplicates(df, print_info=False)
        return df

    def newname_getter(df, parsed_input, newname='combine', prinf=True, merging_subcorpora=False):
        """makes appropriate name for merged entries"""
        if merging_subcorpora:
            if newname is False:
                newname = 'combine'
        if isinstance(newname, int):
            the_newname = list(df.columns)[newname]
        elif isinstance(newname, STRINGTYPE):
            if newname == 'combine':
                if len(parsed_input) <= 3:
                    the_newname = '/'.join(parsed_input)
                elif len(parsed_input) > 3:
                    the_newname = '/'.join(parsed_input[:3]) + '...'
            else:
                the_newname = newname
        if not newname:
            # revise this code
            import operator
            sumdict = {}
            for item in parsed_input:
                summed = sum(list(df[item]))
                sumdict[item] = summed
            the_newname = max(iter(sumdict.items()), key=operator.itemgetter(1))[0]
        if not isinstance(the_newname, STRINGTYPE):
            the_newname = str(the_newname, errors='ignore')
        return the_newname

    def projector(df, list_of_tuples, prinf=True):
        """project abs values"""
        if isinstance(list_of_tuples, list):
            tdict = {}
            for a, b in list_of_tuples:
                tdict[a] = b
            list_of_tuples = tdict
        for subcorpus, projection_value in list(list_of_tuples.items()):
            if isinstance(subcorpus, int):
                subcorpus = str(subcorpus)
            df.ix[subcorpus] = df.ix[subcorpus] * projection_value
            if prinf:
                if isinstance(projection_value, float):
                    print('Projection: %s * %s' % (subcorpus, projection_value))
                if isinstance(projection_value, int):
                    print('Projection: %s * %d' % (subcorpus, projection_value))
        if prinf:
            print('')
        return df

    def lingres(ser, index):
        from scipy.stats import linregress
        from pandas import Series
        ix = ['slope', 'intercept', 'r', 'p', 'stderr']
        return Series(linregress(index, ser.values), index=ix)

    def do_stats(df):
        """do linregress and add to df"""

        try: 
            from scipy.stats import linregress
        except ImportError:
            thetime = strftime("%H:%M:%S", localtime())
            print('%s: sort type not available in this version of corpkit.' % thetime)
            return False

        indices = list(df.index)
        first_year = list(df.index)[0]
        try:
            x = [int(y) - int(first_year) for y in indices]
        except ValueError:
            x = list(range(len(indices)))

        stats = df.apply(lingres, axis=0, index=x)
        df = df.append(stats)
        df = df.replace([np.inf, -np.inf], 0.0)

        return df

    def resort(df, sort_by = False, keep_stats = False):
        """sort results, potentially using scipy's linregress"""
        
        # translate options and make sure they are parseable
        stat_field = ['slope', 'intercept', 'r', 'p', 'stderr']
        easy_sorts = ['total', 'infreq', 'name', 'most', 'least']
        stat_sorts = ['increase', 'decrease', 'static', 'turbulent']
        options = stat_field + easy_sorts + stat_sorts
        sort_by_convert = {'most': 'total', True: 'total', 'least': 'infreq'}
        sort_by = sort_by_convert.get(sort_by, sort_by)

        # probably broken :(
        if just_totals:
            if sort_by == 'name':
                return df.sort_index()
            else:
                return df.sort_values(by='Combined total', ascending=sort_by != 'total', axis=1)

        stats_done = False
        if keep_stats or sort_by in stat_field + stat_sorts:
            df = do_stats(df)
            stats_done = True
            if isinstance(df, bool):
                if df is False:
                    return False
        
        if isinstance(df, Series):
            if stats_done:
                stats = df.ix[range(-5, 0)]
                df = df.drop(list(stats.index))
            if sort_by == 'name':
                df = df.sort_index()
            else:
                df = df.sort_values(ascending=sort_by != 'total')
            if stats_done:
                df = df.append(stats)
            return df

        if sort_by == 'name':
            # currently case sensitive
            df = df.reindex_axis(sorted(df.columns), axis=1)
        elif sort_by in ['total', 'infreq']:
            if df1_istotals:
                df = df.T
            df = df[list(df.sum().sort_values(ascending=sort_by != 'total').index)]
        
        # sort by slope etc., or search by subcorpus name
        if sort_by in stat_field or sort_by not in options:
            asc = kwargs.get('reverse', False)
            df = df.T.sort_values(by=sort_by, ascending=asc).T
        
        if sort_by in ['increase', 'decrease', 'static', 'turbulent']:
            slopes = df.ix['slope']
            if sort_by == 'increase':
                df = df[slopes.argsort()[::-1]]
            elif sort_by == 'decrease':
                df = df[slopes.argsort()]
            elif sort_by == 'static':
                df = df[slopes.abs().argsort()]
            elif sort_by == 'turbulent':
                df = df[slopes.abs().argsort()[::-1]]
            if remove_above_p:
                df = df.T
                df = df[df['p'] <= p]
                df = df.T

        # remove stats field by default
        if not keep_stats:
            df = df.drop(stat_field, axis=0, errors='ignore')
        return df

    def set_threshold(big_list, threshold, prinf=True):
        if isinstance(threshold, STRINGTYPE):
            if threshold.startswith('l'):
                denominator = 10000
            if threshold.startswith('m'):
                denominator = 5000
            if threshold.startswith('h'):
                denominator = 2500
            if isinstance(big_list, DataFrame):
                tot = big_list.sum().sum()

            if isinstance(big_list, Series):
                tot = big_list.sum()
            tshld = float(tot) / float(denominator)
        else:
            tshld = threshold
        if prinf:
            print('Threshold: %d\n' % tshld)
        return tshld

    # copy dataframe to be very safe
    df = dataframe1.copy()
    # make cols into strings
    try:
        df.columns = [str(c) for c in list(df.columns)]
    except:
        pass

    if operation is None:
        operation = 'None'

    if isinstance(interrogation, Concordance):
        return_conc = True
    # do concordance work
    if return_conc:
        if just_entries:
            if isinstance(just_entries, int):
                just_entries = [just_entries]
            if isinstance(just_entries, STRINGTYPE):
                df = df[df['m'].str.contains(just_entries)]
            if isinstance(just_entries, list):
                if all(isinstance(e, STRINGTYPE) for e in just_entries):
                    mp = df['m'].map(lambda x: x in just_entries)
                    df = df[mp]
                else:
                    df = df.ix[just_entries]

        if skip_entries:
            if isinstance(skip_entries, int):
                skip_entries = [skip_entries]
            if isinstance(skip_entries, STRINGTYPE):
                df = df[~df['m'].str.contains(skip_entries)]
            if isinstance(skip_entries, list):
                if all(isinstance(e, STRINGTYPE) for e in skip_entries):
                    mp = df['m'].map(lambda x: x not in skip_entries)
                    df = df[mp]
                else:
                    df = df.drop(skip_entries, axis=0)

        if just_subcorpora:
            if isinstance(just_subcorpora, int):
                just_subcorpora = [just_subcorpora]
            if isinstance(just_subcorpora, STRINGTYPE):
                df = df[df['c'].str.contains(just_subcorpora)]
            if isinstance(just_subcorpora, list):
                if all(isinstance(e, STRINGTYPE) for e in just_subcorpora):
                    mp = df['c'].map(lambda x: x in just_subcorpora)
                    df = df[mp]
                else:
                    df = df.ix[just_subcorpora]

        if skip_subcorpora:
            if isinstance(skip_subcorpora, int):
                skip_subcorpora = [skip_subcorpora]
            if isinstance(skip_subcorpora, STRINGTYPE):
                df = df[~df['c'].str.contains(skip_subcorpora)]
            if isinstance(skip_subcorpora, list):
                if all(isinstance(e, STRINGTYPE) for e in skip_subcorpora):
                    mp = df['c'].map(lambda x: x not in skip_subcorpora)
                    df = df[mp]
                else:
                    df = df.drop(skip_subcorpora, axis=0)

        return Concordance(df)

    if print_info:
        print('\n***Processing results***\n========================\n')

    df1_istotals = False
    if isinstance(df, Series):
        df1_istotals = True
        df = DataFrame(df)
        # if just a single result
    else:
        df = DataFrame(df)
    if operation.startswith('k'):
        if sort_by is False:
            if not df1_istotals:
                sort_by = 'turbulent'
        if df1_istotals:
            df = df.T
    
    # figure out if there's a second list
    # copy and remove totals if there is
    single_totals = True
    using_totals = False
    outputmode = False

    if denominator.__class__ == Interrogation:
        try:
            denominator = denominator.results
        except AttributeError:
            denominator = denominator.totals

    if denominator is not False and not isinstance(denominator, STRINGTYPE):
        df2 = denominator.copy()
        using_totals = True
        if isinstance(df2, DataFrame):
            if len(df2.columns) > 1:
                single_totals = False
            else:
                df2 = Series(df2.iloc[:,0])
        elif isinstance(df2, Series):
            single_totals = True
            #if operation == 'k':
                #raise ValueError('Keywording requires a DataFrame for denominator. Use "self"?')
    else:
        if operation in ['k', 'a', '%', '/', '*', '-', '+']:
            denominator = 'self'         
        if denominator == 'self':
            outputmode = True

    if operation.startswith('a') or operation.startswith('A'):
        if list(df.columns)[0] != '0' and list(df.columns)[0] != 0:
            df = df.T
        if using_totals:
            if not single_totals:
                df2 = df2.T

    if projection:
        # projection shouldn't do anything when working with '%', remember.
        df = projector(df, projection)
        if using_totals:
            df2 = projector(df2, projection)

    if spelling:
        df = convert_spell(df, convert_to=spelling)
        df = merge_duplicates(df, print_info=False)

        if not single_totals:
            df2 = convert_spell(df2, convert_to=spelling, print_info=False)
            df2 = merge_duplicates(df2, print_info=False)
        if not df1_istotals:
            sort_by = 'total'

    if replace_names:
        df = name_replacer(df, replace_names)
        df = merge_duplicates(df)
        if not single_totals:
            df2 = name_replacer(df2, replace_names, print_info=False)
            df2 = merge_duplicates(df2, print_info=False)
        if not sort_by:
            sort_by = 'total'

    if replace_subcorpus_names:
        df = name_replacer(df.T, replace_subcorpus_names)
        df = merge_duplicates(df).T
        df = df.sort_index()
        if not single_totals:
            if isinstance(df2, DataFrame):
                df2 = df2.T
            df2 = name_replacer(df2, replace_subcorpus_names, print_info=False)
            df2 = merge_duplicates(df2, print_info=False)
            if isinstance(df2, DataFrame):
                df2 = df2.T
            df2 = df2.sort_index()
        if not sort_by:
            sort_by = 'total'

    # remove old stats if they're there:
    statfields = ['slope', 'intercept', 'r', 'p', 'stderr']
    try:
        df = df.drop(statfields, axis=0)
    except:
        pass
    if using_totals:
        try:
            df2 = df2.drop(statfields, axis=0)
        except:
            pass

    # remove totals and tkinter order
    for name, ax in zip(['Total'] * 2 + ['tkintertable-order'] * 2, [0, 1, 0, 1]):
        if name == 'Total' and df1_istotals:
            continue
        try:
            df = df.drop(name, axis=ax, errors='ignore')
        except:
            pass
    for name, ax in zip(['Total'] * 2 + ['tkintertable-order'] * 2, [0, 1, 0, 1]):
        if name == 'Total' and single_totals:
            continue

        try:
            df2 = df2.drop(name, axis=ax, errors='ignore')
        except:
            pass

    df = skip_keep_merge_span(df)
    try:
        df2 = skip_keep_merge_span(df2)
    except:
        pass

    # drop infinites and nans
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.fillna(0.0)

    if just_totals:
        df = DataFrame(df.sum(), columns=['Combined total'])
        if using_totals:
            if not single_totals:
                df2 = DataFrame(df2.sum(), columns=['Combined total'])
            else:
                df2 = df2.sum()

    tots = df.sum(axis=1)

    if using_totals or outputmode:
        if not operation.startswith('k'):
            tshld = 0
            # set a threshold if just_totals
            if outputmode is True:
                df2 = df.T.sum()
                if not just_totals:
                    df2.name = 'Total'
                else:
                    df2.name = 'Combined total'
                using_totals = True
                single_totals = True
            if just_totals:
                if not single_totals:
                    tshld = set_threshold(df2, threshold, prinf=print_info)
            df, tots = combiney(df, df2, operation=operation, threshold=tshld, prinf=print_info)
    
    # if doing keywording...
    if operation.startswith('k'):

        if isinstance(denominator, STRINGTYPE):
            if denominator == 'self':
                df2 = df.copy()
            else:
                df2 = denominator

        from corpkit.keys import keywords
        df = keywords(df, df2, 
                      selfdrop=selfdrop, 
                      threshold=threshold, 
                      print_info=print_info,
                      editing=True,
                      calc_all=calc_all,
                      sort_by=sort_by,
                      measure=keyword_measure,
                      **kwargs)
    
    # drop infinites and nans
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.fillna(0.0)

    # resort data
    if sort_by or keep_stats:
        df = resort(df, keep_stats=keep_stats, sort_by=sort_by)
        if isinstance(df, bool):
            if df is False:
                return 'linregress'

    if keep_top:
        if not just_totals:
            df = df[list(df.columns)[:keep_top]]
        else:
            df = df.head(keep_top)

    if just_totals:
        # turn just_totals into series:
        df = Series(df['Combined total'], name='Combined total')

    if df1_istotals:
        if operation.startswith('k'):
            try:
                df = Series(df.ix[dataframe1.name])
                df.name = '%s: keyness' % df.name
            except:
                df = df.iloc[0, :]
                df.name = 'keyness' % df.name

    # generate totals branch if not percentage results:
    # fix me
    if df1_istotals or operation.startswith('k'):
        if not just_totals:
            try:
                total = Series(df['Total'], name='Total')
            except:
                total = 'none'
                pass

            #total = df.copy()
        else:
            total = 'none'
    else:
        # might be wrong if using division or something...
        try:
            total = df.T.sum(axis=1)
        except:
            total = 'none'
    
    if not isinstance(tots, DataFrame) and not isinstance(tots, Series):
        total = df.sum(axis=1)
    else:
        total = tots

    if isinstance(df, DataFrame):
        if df.empty:
            datatype = 'object'
        else:
            datatype = df.iloc[0].dtype
    else:
        datatype = df.dtype
    locs['datatype'] = datatype

    # TURN INT COL NAMES INTO STR
    try:
        df.results.columns = [str(d) for d in list(df.results.columns)]
    except:
        pass

    def add_tkt_index(df):
        """add an order for tkintertable if using gui"""
        if isinstance(df, Series):
            df = df.T
            df = df.drop('tkintertable-order', errors='ignore', axis=0)
            df = df.drop('tkintertable-order', errors='ignore', axis=1)
            dat = [i for i in range(len(df.index))]
            df['tkintertable-order'] = Series(dat, index=list(df.index))
            df = df.T
        return df

    # while tkintertable can't sort rows
    if checkstack('tkinter'):
        df = add_tkt_index(df)

    if kwargs.get('df1_always_df'):
        if isinstance(df, Series):
            df = DataFrame(df)

    # delete non-appearing conc lines
    lns = None
    if isinstance(getattr(interrogation, 'concordance', None), Concordance):
        try:
            col_crit = interrogation.concordance['m'].map(lambda x: x in list(df.columns))
            ind_crit = interrogation.concordance['c'].map(lambda x: x in list(df.index))
            lns = interrogation.concordance[col_crit]
            lns = lns.loc[ind_crit]
            lns = Concordance(lns)
        except ValueError:
            lns = None
    
    output = Interrogation(results=df, totals=total, query=locs, concordance=lns)

    if print_info:
        print('***Done!***\n========================\n')

    return output





