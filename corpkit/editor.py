# a file for working with dataframe1s. most importantly, make a dataframe1 plotter.

def editor(dataframe1, 
            operation = '%',
            dataframe2 = False,
            sort_by = False,
            keep_stats = False,
            keep_top = False,
            just_totals = False,
            threshold = 'medium',
            
            just_entries = False,
            skip_entries = False,
            merge_entries = False,
            newname = False,

            just_subcorpora = False,
            skip_subcorpora = False,
            span_subcorpora = False,
            merge_subcorpora = False,

            projection = False,

            only_totals = False,
            remove_above_p = False,
            p = 0.05, 
            revert_year = True
            ):
    """Edit results of corpus interrogation"""

    import pandas
    import pandas as pd
    import numpy as np
    import collections
    from pandas import DataFrame, Series
    from corpkit.progressbar import ProgressBar
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

    def combiney(df, df2, operation = '%', threshold = 'medium', just_totals = False):
        """mash df and df2 together in appropriate way"""
        if single_totals:
            if operation == '%':
                if just_totals:
                    df = df * 100.0 / df2.sum()
                else:
                    df = df * 100.0
                    df = df.div(list(df2), axis = 0)
            elif operation == '+':
                df = df.add(list(df2), axis = 0)
            elif operation == '-':
                df = df.sub(list(df2), axis = 0)
            elif operation == '*':
                df = df.mul(list(df2), axis = 0)
            elif operation == '/':
                df = df.div(list(df2), axis = 0)
            return df

        elif not single_totals:
            if just_totals:
                if operation == '%':
                    # leaves 0.0 if not found ...
                    df = df * 100.0 / df2.sum()

            else:
                p = ProgressBar(len(list(df.columns)))
                for index, entry in enumerate(list(df.columns)):
                    p.animate(index)
                    if operation == '%':
                        try:
                            df[entry] = df[entry] * 100.0 / df2[entry]
                        except:
                            continue
                        #df.drop(entry, axis = 1, inplace = True)
                        #df[entry] = maths_done
                    elif operation == '+':
                        try:
                            df[entry] = df[entry] + df2[entry]
                        except:
                            continue
                    elif operation == '-':
                        try:
                            df[entry] = df[entry] - df2[entry]
                        except:
                            continue
                    elif operation == '*':
                        try:
                            df[entry] = df[entry] * df2[entry]
                        except:
                            continue
                    elif operation == '/':
                        try:
                            df[entry] = df[entry] / df2[entry]
                        except:
                            continue
                p.animate(len(list(df.columns)))
                if have_ipython:
                    clear_output()
        return df

    def parse_input(input):
        """turn whatever has been passed in into list of words that can be used as pandas indices"""
        import re
        if type(input) == int:
            input = [input]

        elif type(input) == str:
            try:
                regex = re.compile(input)
                parsed_input = [w for w in list(df) if re.search(regex, w)]

            except:
                input = [input]

        if type(input) == list:
            if type(input[0]) == int:
                parsed_input = [word for index, word in enumerate(list(df)) if index in input]
            elif type(input[0]) == str:
                parsed_input = [word for word in input if word in df.columns]

        return parsed_input

    def just_these_entries(df, parsed_input):
        entries = [word for word in list(df) if word not in parsed_input]
        print 'Keeping %d entries:\n    %s\n' % (len(parsed_input), '\n    '.join(parsed_input[:20]))
        if len(parsed_input) > 20:
            print '... and %d more ... \n' % (len(parsed_input) - 20)
        df = df.drop(entries, axis = 1)
        return df

    def skip_these_entries(df, parsed_input):
        print 'Skipping %d entries:\n    %s\n' % (len(parsed_input), '\n    '.join(parsed_input[:20]))
        if len(parsed_input) > 20:
            print '... and %d more ... \n' % len(parsed_input) - 20
        df = df.drop(parsed_input, axis = 1)
        return df

    def newname_getter(df, parsed_input, newname = 'combine'):
        """makes appropriate name for merged entries"""
        if type(newname) == int:
            the_newname = list(df.columns)[i]
        elif type(newname) == str:
            if newname == 'combine':
                the_newname = '/'.join(parsed_input)
            else:
                the_newname = newname
        if newname is False:
            # revise this code
            import operator
            sumdict = {}
            for item in parsed_input:
                summed = sum(list(df[item]))
                sumdict[item] = summed
            the_newname = max(sumdict.iteritems(), key=operator.itemgetter(1))[0]
        if type(the_newname) != unicode:
            the_newname = unicode(the_newname, errors = 'ignore')
        return the_newname

    def merge_these_entries(df, parsed_input, the_newname):
        # make new entry with sum of parsed input
        print 'Merging %d entries as "%s":\n    %s\n' % (len(parsed_input), the_newname, '\n    '.join(parsed_input[:20]))
        if len(parsed_input) > 20:
            print '... and %d more ... \n' % (len(parsed_input) - 20)
        df[the_newname] = sum([df[i] for i in parsed_input])
        # remove old entries
        df = df.drop(parsed_input, axis = 1)
        return df

    def just_these_subcorpora(df, lst_of_subcorpora):
        if type(lst_of_subcorpora[0]) == int:
            lst_of_subcorpora = [str(l) for l in lst_of_subcorpora]
        good_years = [subcorpus for subcorpus in list(df.index) if subcorpus in lst_of_subcorpora]
        print 'Keeping %d subcorpora:\n    %s\n' % (len(good_years), '\n    '.join(good_years[:20]))
        if len(good_years) > 20:
            print '... and %d more ... \n' % len(good_years) - 20
        df = df.drop([subcorpus for subcorpus in list(df.index) if subcorpus not in good_years], axis = 0)
        return df

    def skip_these_subcorpora(df, lst_of_subcorpora):
        if type(lst_of_subcorpora) == int:
            lst_of_subcorpora = [lst_of_subcorpora]
        if type(lst_of_subcorpora[0]) == int:
            lst_of_subcorpora = [str(l) for l in lst_of_subcorpora]
        bad_years = [subcorpus for subcorpus in list(df.index) if subcorpus in lst_of_subcorpora]
        print 'Skipping %d subcorpora:\n    %s\n' % (len(bad_years), '\n    '.join(bad_years[:20]))
        if len(bad_years) > 20:
            print '... and %d more ... \n' % len(bad_years) - 20
        df = df.drop([subcorpus for subcorpus in list(df.index) if subcorpus in bad_years], axis = 0)
        return df

    def span_these_subcorpora(df, lst_of_subcorpora):
        non_totals = [subcorpus for subcorpus in list(df.index)]
        good_years = [subcorpus for subcorpus in non_totals if int(subcorpus) >= int(lst_of_subcorpora[0]) and int(subcorpus) <= int(lst_of_subcorpora[-1])]
        print 'Keeping subcorpora:\n    %d--%d' % (int(lst_of_subcorpora[0]), int(lst_of_subcorpora[-1]))
        df = df.drop([subcorpus for subcorpus in list(df.index) if subcorpus not in good_years], axis = 0)
        # retotal needed here
        return df

    def projector(df, list_of_tuples):
        for subcorpus, projection_value in list_of_tuples:
            if type(subcorpus) == int:
                subcorpus = str(subcorpus)
            df.ix[subcorpus] = df.ix[subcorpus] * projection_value
        return df
    
    def merge_these_subcorpora(df, lst_of_subcorpora):
        # handles subcorpus names, not indices, right now
        if type(lst_of_subcorpora) == int:
            lst_of_subcorpora = [lst_of_subcorpora]
        if type(lst_of_subcorpora[0]) == int:
            lst_of_subcorpora = [str(l) for l in lst_of_subcorpora]
        the_newname = '/'.join(sorted(lst_of_subcorpora))
        if type(df) == pandas.core.frame.DataFrame:
            df.ix[the_newname] = sum([df.ix[i] for i in lst_of_subcorpora])
            df = df.drop(lst_of_subcorpora, axis = 0)
        if type(df) == pandas.core.series.Series:
            df[the_newname] = sum([df[i] for i in lst_of_subcorpora])
            df = df.drop(lst_of_subcorpora)
        return df

    def do_stats(df):
        """do linregress and add to df"""
        from scipy.stats import linregress
        entries = []
        slopes = []
        intercepts = []
        rs = []
        ps = []
        stderrs = []
        indices = list(df.index)
        first_year = list(df.index)[0]
        try:
            x = [int(y) - int(first_year) for y in indices]
        except ValueError:
            x = range(len(indices))
        statfields = ['slope', 'intercept', 'r', 'p', 'stderr']
        for entry in list(df.columns):
            entries.append(entry)
            y = list(df[entry])
            slope, intercept, r, p, stderr = linregress(x, y)
            slopes.append(slope)
            intercepts.append(intercept)
            rs.append(r)
            ps.append(p)
            stderrs.append(stderr)
        sl = pd.DataFrame([slopes, intercepts, rs, ps, stderrs], 
                           index = statfields, 
                           columns = list(df.columns))
        df = df.append(sl)
        return df

    def recalc(df, operation = '%'):
        """Add totals to the dataframe1"""

        #df.drop('Total', axis = 0, inplace = True)
        #df.drop('Total', axis = 1, inplace = True)

        df['Total'] = df.sum(axis = 1)
        df = df.T
        df['Total'] = df.sum(axis = 1)
        df = df.T

        # make totals percentages if need be.
        #if operation == '%':
        #    df['Total'] = df['Total'] * 100.0
        #    df['Total'] = df['Total'].div(list(df2), axis = 0)
        #elif operation == '+':
        #    df['Total'] = df['Total'].add(list(df2), axis = 0)
        #elif operation == '-':
        #    df['Total'] = df['Total'].sub(list(df2), axis = 0)
        #elif operation == '*':
        #    df['Total'] = df['Total'].mul(list(df2), axis = 0)
        #elif operation == '/':
        #    df['Total'] = df['Total'].div(list(df2), axis = 0)
        return df

    def resort(df, sort_by = False, keep_stats = False):
        """sort results"""
        # translate options and make sure they are parseable
        options = ['total', 'name', 'infreq', 'increase', 
                   'decrease', 'static', 'most', 'least', 'none']

        if sort_by is True:
            sort_by = 'total'
        if sort_by == 'most':
            sort_by = 'total'
        if sort_by == 'least':
            sort_by = 'infreq'
        if sort_by not in options:
            raise ValueError("sort_by parameter error: '%s' not recognised. Must be True, False, %s" % (sort_by, ', '.join(options)))

        if sort_by == 'total':
            if df1_istotals:
                df = df.T
            df = recalc(df, operation = operation)
            tot = df.ix['Total']
            df = df[tot.argsort()[::-1]]
            df = df.drop('Total', axis = 0)
            df = df.drop('Total', axis = 1)
            if df1_istotals:
                df = df.T
            #df = recalc(df, operation = operation)
        elif sort_by == 'infreq':
            df = recalc(df, operation = operation)
            tot = df.ix['Total']
            df = df[tot.argsort()]
            df = df.drop('Total', axis = 0)
            df = df.drop('Total', axis = 1)
            #df = recalc(df, operation = operation)
        elif sort_by == 'name':
            # currently case sensitive...
            df = df.reindex_axis(sorted(df.columns), axis=1)
            #df = recalc(df, operation = operation)
        else:
            statfields = ['slope', 'intercept', 'r', 'p', 'stderr']
            df = do_stats(df)
            slopes = df.ix['slope']
            if sort_by == 'increase':
                df = df[slopes.argsort()[::-1]]
            elif sort_by == 'decrease':
                df = df[slopes.argsort()]
            
            # untested
            if remove_above_p:
                df = df.T.loc[:, (df.T.p < p)].T
            
            # list of all columns
            move_totals = list(df.columns)
            
            # add total to end           
            #try:
                #move_totals.remove('Total')
                #move_totals.append('Total')
            #except:
                #pass

            # remove stats field by default
            if not keep_stats:
                df = df.drop(statfields, axis = 0)

            # or, remove them from the columns list and add them to the end
            else:
                for stat in statfields:
                    move_totals.remove(stat)
                    move_totals.append(stat)

            # reorder with totals and stats at end
            df = df[move_totals]

            #elif sort_by == 'static':
                #reordered = 

            #if operation != '%':
                #df = recalc(df, operation = operation)
        return df

    def set_threshold(big_list, threshold):
        if type(threshold) == str:
            if threshold.startswith('l'):
                denominator = 10000
            if threshold.startswith('m'):
                denominator = 5000
            if threshold.startswith('h'):
                denominator = 2500

            if type(big_list) == pandas.core.frame.DataFrame:
                tot = big_list.sum().sum()

            if type(big_list) == pandas.core.series.Series:
                tot = big_list.sum()
            the_threshold = float(tot) / float(denominator)

        else:
            the_threshold = threshold
        
        print 'Threshold: %d' % the_threshold
        return the_threshold

#####################################################


    # check if we're in concordance mode
    try:
        if list(dataframe1.columns) == ['l', 'm', 'r']:
            conc_lines = True
        else:
            conc_lines = False
    except:
        conc_lines = False

    # copy dataframe to be very safe
    df = dataframe1.copy()

    if conc_lines:
        df = dataframe1.copy()

        if just_entries:
            if type(just_entries) == int:
                just_entries = [just_entries]
            if type(just_entries) == list:
                if type(just_entries[0]) != int:
                    raise ValueError('just_entries must be int or list of ints when working with concordance lines.')
                else:
                    df = df.ix[just_entries].reset_index(drop = True)

        if skip_entries:
            if type(skip_entries) == int:
                skip_entries = [skip_entries]
            if type(skip_entries) == list:
                if type(skip_entries[0]) != int:
                    raise ValueError('skip_entries must be int or list of ints when working with concordance lines.')
                else:
                    df = df.ix[[e for e in list(df.index) if e not in skip_entries]].reset_index(drop = True)

        return df


    df1_istotals = False
    if type(df) == pandas.core.series.Series:
        if df.name == 'Totals':
            df1_istotals = True
            df = pandas.DataFrame(df)
        # if just a single result
        else:
            df = pandas.DataFrame(df) # set it the correct name?
    if just_totals:
        df = df.sum()

    #df = df.T
    #if just_totals:
        #df = pd.DataFrame([sum(df[i]) for i in list(df.columns)], index = list(df.columns))
    #else:
        #try:
            #df = df.drop('Total', axis = 0)
        #except:
            #pass
        #try:
            #df = df.drop('Total', axis = 1)
        #except:
            #pass
    
    # figure out if there's a second list
    # copy and remove totals if there is
    single_totals = True
    using_totals = False

    try:
        if dataframe2.empty is False:
            df2 = dataframe2.copy()
            using_totals = True
            #df2 = df2
            if type(df2) == pandas.core.frame.DataFrame:
                if len(df2.columns) > 1:
                    single_totals = False
                else:
                    df2 = pd.Series(df2)
                #if operation != '%':
            elif type(df2) == pandas.core.series.Series:
                single_totals = True
                #if just_totals:
                    # it should already be just_totals
                    #df2 = pd.Series([sum(df2[i]) for i in list(df2.columns)])
            else:
                raise ValueError('dataframe2 not recognised.')   
    except AttributeError:
        pass


    if projection:
        # projection shouldn't do anythign when working with '%'
        # so let's not run df2 through it yet.
        df = projector(df, projection)

    # do all merging before combining anything

    if merge_entries:
        the_newname = newname_getter(df, parse_input(merge_entries), newname = newname)
    if merge_entries:
        df = merge_these_entries(df, parse_input(merge_entries), the_newname)
    if merge_subcorpora:
        df = merge_these_subcorpora(df, merge_subcorpora)

    if using_totals:
        if merge_entries:
            df2 = merge_these_entries(df2, parse_input(merge_entries), the_newname)
        if merge_subcorpora:
            df2 = merge_these_subcorpora(df2, merge_subcorpora)        

    # combine lists
    use_combiney = False
    try:
        if dataframe2.empty is False:
            use_combiney = True
            # set a threshold if just_totals
            if just_totals:
                the_threshold = set_threshold(df2, threshold)
            else:
                the_threshold = 0
            df = combiney(df, df2, operation = operation, threshold = the_threshold, just_totals = just_totals)
    except AttributeError:
        pass

    # chop up data as required

    if just_entries:
        df = just_these_entries(df, parse_input(just_entries))
    if skip_entries:
        df = skip_these_entries(df, parse_input(skip_entries))

    if just_subcorpora:
        df = just_these_subcorpora(df, just_subcorpora)
    if skip_subcorpora:
        df = skip_these_subcorpora(df, skip_subcorpora)
    if span_subcorpora:
        df = span_these_subcorpora(df, span_subcorpora)

    # drop infinites and nans
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.fillna(0.0)

    # resort data
    if sort_by:
        df = resort(df, keep_stats = keep_stats, sort_by = sort_by)
    
    if keep_top:
        if not just_totals:
            df = df[list(df.columns)[:keep_top]]
        else:
            import warnings
            warnings.warn("keep_top has no effect if just_totals is True.")

    # generate totals branch:
    if df1_istotals:
        total = df.copy()
    else:
        if operation != '%':
            total = df.T.sum()
        else:
            if using_totals:
                tot1 = dataframe1.T.sum()
                if single_totals:
                    tot2 = dataframe2
                else:
                    tot2 = dataframe2.T.sum()
                total = tot1 * 100.0 / tot2
            else:
                total = dataframe1.T.sum()


    #make named_tuple
    outputnames = collections.namedtuple('interrogation', ['query', 'results', 'totals'])
    output = outputnames(['coming soon.'], df, total)

    # pandas options
    pd.set_option('display.max_columns', 4)
    pd.set_option('display.max_rows', 5)
    pd.set_option('expand_frame_repr', False)

    print '\nResult (sample)\n'
    print '=' * 80 + '\n'
    print df.head().T

    return output
