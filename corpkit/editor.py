
def editor(dataframe1, 
            operation = '%',
            dataframe2 = False,
            sort_by = False,
            keep_stats = True,
            keep_top = False,
            just_totals = False,
            threshold = 'medium',
            just_entries = False,
            skip_entries = False,
            merge_entries = False,
            newname = 'combine',
            just_subcorpora = False,
            skip_subcorpora = False,
            span_subcorpora = False,
            merge_subcorpora = False,
            new_subcorpus_name = False,
            projection = False,
            remove_above_p = False,
            p = 0.05, 
            revert_year = True,
            print_info = True,
            **kwargs
            ):
    """Edit results of corpus interrogation"""

    import pandas
    import pandas as pd
    import numpy as np
    import collections
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

    the_time_started = strftime("%Y-%m-%d %H:%M:%S")

    def combiney(df, df2, operation = '%', threshold = 'medium', prinf = True):
        """mash df and df2 together in appropriate way"""
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
                            print 'Removing %d entries below threshold:\n    %s' % (len(to_drop), '\n    '.join(to_show))
                        if len(to_drop) > 10:
                            print '... and %d more ... \n' % (len(to_drop) - len(to_show) + 1)
                        else:
                            print ''
                else:
                    denom = df2
        else:
            denom = list(df2)
        if single_totals:
            if operation == '%':
                df = df * 100.0
                df = df.div(denom, axis = 0)
            elif operation == '+':
                df = df.add(denom, axis = 0)
            elif operation == '-':
                df = df.sub(denom, axis = 0)
            elif operation == '*':
                df = df.mul(denom, axis = 0)
            elif operation == '/':
                df = df.div(denom, axis = 0)
            return df

        elif not single_totals:
            #p = ProgressBar(len(list(df.columns)))
            for index, entry in enumerate(list(df.columns)):
                #p.animate(index)
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
            #p.animate(len(list(df.columns)))
            #if have_ipython:
                #clear_output()
        return df

    def parse_input(df, input):
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

    def just_these_entries(df, parsed_input, prinf = True):
        entries = [word for word in list(df) if word not in parsed_input]
        if prinf:
            print 'Keeping %d entries:\n    %s' % (len(parsed_input), '\n    '.join(parsed_input[:10]))
            if len(parsed_input) > 10:
                print '... and %d more ... \n' % (len(parsed_input) - 10)
            else:
                print ''
        df = df.drop(entries, axis = 1)
        return df

    def skip_these_entries(df, parsed_input, prinf = True):
        if prinf:     
            print 'Skipping %d entries:\n    %s' % (len(parsed_input), '\n    '.join(parsed_input[:10]))
            if len(parsed_input) > 10:
                print '... and %d more ... \n' % (len(parsed_input) - 10)
            else:
                print ''
        df = df.drop(parsed_input, axis = 1)
        return df

    def newname_getter(df, parsed_input, newname = 'combine', prinf = True):
        """makes appropriate name for merged entries"""
        if type(newname) == int:
            the_newname = list(df.columns)[newname]
        elif type(newname) == str:
            if newname == 'combine':
                if len(parsed_input) <= 3:
                    the_newname = '/'.join(parsed_input)
                elif len(parsed_input) > 3:
                    the_newname = '/'.join(parsed_input[:3]) + '...'
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

    def merge_these_entries(df, parsed_input, the_newname, prinf = True):
        # make new entry with sum of parsed input
        if prinf:
            print 'Merging %d entries as "%s":\n    %s' % (len(parsed_input), the_newname, '\n    '.join(parsed_input[:10]))
            if len(parsed_input) > 10:
                print '... and %d more ... \n' % (len(parsed_input) - 10)
            else:
                print ''
        # remove old entries
        temp = sum([df[i] for i in parsed_input])
        df = df.drop(parsed_input, axis = 1)
        df[the_newname] = temp
        return df

    def just_these_subcorpora(df, lst_of_subcorpora, prinf = True):        
        if type(lst_of_subcorpora[0]) == int:
            lst_of_subcorpora = [str(l) for l in lst_of_subcorpora]
        good_years = [subcorpus for subcorpus in list(df.index) if subcorpus in lst_of_subcorpora]
        if prinf:
            print 'Keeping %d subcorpora:\n    %s' % (len(good_years), '\n    '.join(good_years[:10]))
            if len(good_years) > 10:
                print '... and %d more ... \n' % (len(good_years) - 10)
            else:
                print ''
        df = df.drop([subcorpus for subcorpus in list(df.index) if subcorpus not in good_years], axis = 0)
        return df

    def skip_these_subcorpora(df, lst_of_subcorpora, prinf = True):
        if type(lst_of_subcorpora) == int:
            lst_of_subcorpora = [lst_of_subcorpora]
        if type(lst_of_subcorpora[0]) == int:
            lst_of_subcorpora = [str(l) for l in lst_of_subcorpora]
        bad_years = [subcorpus for subcorpus in list(df.index) if subcorpus in lst_of_subcorpora]
        if prinf:       
            print 'Skipping %d subcorpora:\n    %s' % (len(bad_years), '\n    '.join([str(i) for i in bad_years[:10]]))
            if len(bad_years) > 10:
                print '... and %d more ... \n' % (len(bad_years) - 10)
            else:
                print ''
        df = df.drop([subcorpus for subcorpus in list(df.index) if subcorpus in bad_years], axis = 0)
        return df

    def span_these_subcorpora(df, lst_of_subcorpora, prinf = True):
        non_totals = [subcorpus for subcorpus in list(df.index)]
        good_years = [subcorpus for subcorpus in non_totals if int(subcorpus) >= int(lst_of_subcorpora[0]) and int(subcorpus) <= int(lst_of_subcorpora[-1])]
        if prinf:        
            print 'Keeping subcorpora:\n    %d--%d\n' % (int(lst_of_subcorpora[0]), int(lst_of_subcorpora[-1]))
        df = df.drop([subcorpus for subcorpus in list(df.index) if subcorpus not in good_years], axis = 0)
        # retotal needed here
        return df

    def projector(df, list_of_tuples, prinf = True):
        for subcorpus, projection_value in list_of_tuples:
            if type(subcorpus) == int:
                subcorpus = str(subcorpus)
            df.ix[subcorpus] = df.ix[subcorpus] * projection_value
            if prinf:
                if type(projection_value) == float:
                    print 'Projection: %s * %s' % (subcorpus, projection_value)
                if type(projection_value) == int:
                    print 'Projection: %s * %d' % (subcorpus, projection_value)
        if prinf:
            print ''
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

        df['temp-Total'] = df.sum(axis = 1)
        df = df.T
        df['temp-Total'] = df.sum(axis = 1)
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
        
        options = ['total', 'name', 'infreq', 'increase', 'turbulent',
                   'decrease', 'static', 'most', 'least', 'none']

        if sort_by is True:
            sort_by = 'total'
        if sort_by == 'most':
            sort_by = 'total'
        if sort_by == 'least':
            sort_by = 'infreq'
        if sort_by not in options:
            raise ValueError("sort_by parameter error: '%s' not recognised. Must be True, False, %s" % (sort_by, ', '.join(options)))

        if just_totals:
            if sort_by == 'infreq':
                df = df.sort(columns = 'Combined total', ascending = True)
            elif sort_by == 'total':
                df = df.sort(columns = 'Combined total', ascending = False)
            elif sort_by == 'name':
                df = df.sort_index()
            return df

        # this is really shitty now that i know how to sort, like in the above
        if keep_stats:
            df = do_stats(df)
        if sort_by == 'total':
            if df1_istotals:
                df = df.T
            df = recalc(df, operation = operation)
            tot = df.ix['temp-Total']
            df = df[tot.argsort()[::-1]]
            df = df.drop('temp-Total', axis = 0)
            df = df.drop('temp-Total', axis = 1)
            if df1_istotals:
                df = df.T
        elif sort_by == 'infreq':
            if df1_istotals:
                df = df.T
            df = recalc(df, operation = operation)
            tot = df.ix['temp-Total']
            df = df[tot.argsort()]
            df = df.drop('temp-Total', axis = 0)
            df = df.drop('temp-Total', axis = 1)
            if df1_istotals:
                df = df.T
        elif sort_by == 'name':
            # currently case sensitive...
            df = df.reindex_axis(sorted(df.columns), axis=1)
        else:
            statfields = ['slope', 'intercept', 'r', 'p', 'stderr']
            
            if not keep_stats:
                df = do_stats(df)

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
                # the easy way to do it!
                df = df.T
                df = df[df['p'] <= p]
                df = df.T

            # remove stats field by default
            if not keep_stats:
                df = df.drop(statfields, axis = 0)

        return df

    def set_threshold(big_list, threshold, prinf = True):
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
        
        if prinf:
            print 'Threshold: %d\n' % the_threshold
            printed_th = True
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


    # do concordance work
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

    if print_info:
        print '\n***Processing results***\n========================\n'

    df1_istotals = False
    if type(df) == pandas.core.series.Series:
        df1_istotals = True
        df = pandas.DataFrame(df)
        # if just a single result
    else:
        df = pandas.DataFrame(df) # set it the correct name?
    
    # figure out if there's a second list
    # copy and remove totals if there is
    single_totals = True
    using_totals = False
    outputmode = False
    printed_th = False

    try:
        if dataframe2.empty is False:            
            df2 = dataframe2.copy()
            using_totals = True

            if type(df2) == pandas.core.frame.DataFrame:
                if len(df2.columns) > 1:
                    single_totals = False
                else:
                    df2 = pd.Series(df2)
            elif type(df2) == pandas.core.series.Series:
                single_totals = True
            else:
                raise ValueError('dataframe2 not recognised.')   
    except AttributeError:
        if dataframe2 == 'self':
            outputmode = True

    if projection:
        # projection shouldn't do anything when working with '%', remember.
        df = projector(df, projection)
        if using_totals:
            df2 = projector(df2, projection)

    # merging
    if merge_entries:
        the_newname = newname_getter(df, parse_input(df, merge_entries), newname = newname, prinf = print_info)
    
    if merge_entries:
        df = merge_these_entries(df, parse_input(df, merge_entries), the_newname, prinf = print_info)
        if not single_totals:
            df2 = merge_these_entries(df2, parse_input(df, merge_entries), the_newname, prinf = False)
    
    if merge_subcorpora:
        the_newname = newname_getter(df.T, parse_input(df.T, merge_subcorpora), newname = new_subcorpus_name, prinf = print_info)
        df = merge_these_entries(df.T, parse_input(df.T, merge_subcorpora), the_newname, prinf = print_info).T
        if using_totals:
            df2 = merge_these_entries(df2.T, parse_input(df.T, merge_subcorpora), the_newname, prinf = print_info).T
    
    if just_subcorpora:
        df = just_these_subcorpora(df, just_subcorpora, prinf = print_info)
        if using_totals:
            df2 = just_these_subcorpora(df2, just_subcorpora, prinf = False)
    
    if skip_subcorpora:
        df = skip_these_subcorpora(df, skip_subcorpora, prinf = print_info)
        if using_totals:
            df2 = skip_these_subcorpora(df2, skip_subcorpora, prinf = False)
    
    if span_subcorpora:
        df = span_these_subcorpora(df, span_subcorpora, prinf = print_info)
        if using_totals:
            df2 = span_these_subcorpora(df2, span_subcorpora, prinf = False)

    if just_entries:
        df = just_these_entries(df, parse_input(df, just_entries), prinf = print_info)
        if not single_totals:
            df2 = just_these_entries(df2, parse_input(df, just_entries), prinf = False)
    if skip_entries:
        df = skip_these_entries(df, parse_input(df, skip_entries), prinf = print_info)
        if not single_totals:
            df2 = skip_these_entries(df2, parse_input(df, skip_entries), prinf = False)

    # drop infinites and nans
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.fillna(0.0)

    # make just_totals as dataframe
    just_one_total_number = False
    if just_totals:
        df = pd.DataFrame(df.sum(), columns = ['Combined total'])
        if using_totals:
            if not single_totals:
                df2 = pd.DataFrame(df2.sum(), columns = ['Combined total'])
            else:
                just_one_total_number = True
                df2 = df2.sum()

    # generate '%' totals here ...
    if using_totals:
        if operation == '%':
            tot1 = df.T.sum()
            if single_totals:
                tot2 = df2
            else:
                tot2 = df2.T.sum()
            total = tot1 * 100.0 / tot2

    # combine lists
    if using_totals or outputmode:
        the_threshold = 0
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
                the_threshold = set_threshold(df2, threshold, prinf = print_info)
        df = combiney(df, df2, operation = operation, threshold = the_threshold, prinf = print_info)

    # resort data
    if sort_by:
        df = resort(df, keep_stats = keep_stats, sort_by = sort_by)
    
    if keep_top:
        if not just_totals:
            df = df[list(df.columns)[:keep_top]]
        else:
            df = df.head(keep_top)

    if just_totals:
        # turn just_totals into series:
        df = pd.Series(df['Combined total'], name = 'Combined total')
    # generate totals branch if not percentage results:
    if df1_istotals:
        total = pd.Series(df['Total'], name = 'Total')
        #total = df.copy()
    else:
        # might be wrong if using division or something...
        total = df.T.sum()

    if type(df) == pandas.core.frame.DataFrame:
        datatype = df.ix[0].dtype
    else:
        datatype = df.dtype
    #make named_tuple
    the_operation = 'none'
    if using_totals:
        the_operation = operation

    the_options = {}
    the_options['time_started'] = the_time_started
    the_options['function'] = 'editor'
    the_options['dataframe1'] = dataframe1
    the_options['operation'] = the_operation
    the_options['dataframe2'] = dataframe2
    the_options['datatype'] = datatype
    the_options['sort_by'] = sort_by
    the_options['keep_stats'] = keep_stats
    the_options['just_totals'] = just_totals
    the_options['threshold'] = threshold
    the_options['just_entries'] = just_entries
    the_options['just_entries'] = just_entries
    the_options['skip_entries'] = skip_entries
    the_options['merge_entries'] = merge_entries
    the_options['newname'] = newname
    the_options['just_subcorpora'] = just_subcorpora
    the_options['skip_subcorpora'] = skip_subcorpora
    the_options['span_subcorpora'] = span_subcorpora
    the_options['merge_subcorpora'] = merge_subcorpora
    the_options['new_subcorpus_name'] = new_subcorpus_name
    the_options['projection'] = projection
    the_options['remove_above_p'] = remove_above_p
    the_options['p'] = p
    the_options['revert_year'] = revert_year
    the_options['print_info'] = print_info

    outputnames = collections.namedtuple('edited_interrogation', ['query', 'results', 'totals'])
    output = outputnames(the_options, df, total)

    #print '\nResult (sample)\n'
    if print_info:
        #if merge_entries or merge_subcorpora or span_subcorpora or just_subcorpora or \
           #just_entries or skip_entries or skip_subcorpora or printed_th or projection:
        print '***Done!***\n========================\n'
    #print df.head().T
    #print ''

    pd.set_option('display.max_rows', 10)
    pd.set_option('display.max_columns', 8)
    pd.set_option('max_colwidth',70)
    pd.set_option('display.width', 800)
    pd.set_option('expand_frame_repr', False)

    return output
