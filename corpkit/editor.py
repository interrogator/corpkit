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

            only_totals = False,
            remove_above_p = False,
            P = 0.05, 
            revert_year = True
            ):
    """Edit results of corpus interrogation"""

    import pandas as pd
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

    def combiney(df, df2, operation = '%', threshold = 'medium'):
        """mash df and df2 together in appropriate way"""
        if single_totals:
            if operation == '%':
                df = df * 100.0
                # can i make it possible to handle
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
            if just_totals and threshold:
                df = df.T.loc[:, (df.T.sum(axis=0) > threshold)].T

            p = ProgressBar(len(list(df.columns)))
            for index, entry in enumerate(list(df.columns)):
                p.animate(index)
                if operation == '%':
                    try:
                        maths_done = df[entry] * 100.0 / df2[entry]
                    except:
                        continue
                    df.drop(entry, axis = 1, inplace = True)
                    df[entry] = maths_done
                elif operation == '+':
                    try:
                        maths_done = df[entry] + df2[entry]
                    except:
                        continue
                    df.drop(entry, axis = 1, inplace = True)
                    df[entry] = maths_done
                elif operation == '-':
                    try:
                        maths_done = df[entry] - df2[entry]
                    except:
                        continue
                    df.drop(entry, axis = 1, inplace = True)
                    df[entry] = maths_done
                elif operation == '*':
                    try:
                        maths_done = df[entry] * df2[entry]
                    except:
                        continue
                    df.drop(entry, axis = 1, inplace = True)
                    df[entry] = maths_done
                elif operation == '/':
                    try:
                        maths_done = df[entry] / df2[entry]
                    except:
                        continue
                    df.drop(entry, axis = 1, inplace = True)
                    df[entry] = maths_done
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
        non_totals = [subcorpus for subcorpus in list(df.index) if subcorpus != 'Total']
        good_years = [subcorpus for subcorpus in non_totals if int(subcorpus) >= int(lst_of_subcorpora[0]) and int(subcorpus) <= int(lst_of_subcorpora[-1])]
        print 'Keeping subcorpora:\n    %d--%d' % (int(lst_of_subcorpora[0]), int(lst_of_subcorpora[-1]))
        df = df.drop([subcorpus for subcorpus in list(df.index) if subcorpus not in good_years], axis = 0)
        # retotal needed here
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
            df = recalc(df, operation = operation)
            tot = df.ix['Total']
            df = df[tot.argsort()[::-1]]
            df = df.drop('Total', axis = 0)
            df = df.drop('Total', axis = 1)
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

            totals = []
            for each_entry in list(big_list.columns):
                totals.append(sum(list(big_list[each_entry])))
            tot = sum(totals)
            # generate a threshold
            the_threshold = tot / float(denominator)

        elif type(threshold) == int:
            the_threshold = threshold
        
        print 'Threshold: %d' % the_threshold
        return the_threshold

#####################################################

    # start
    print '\nProcessing\n' + ('=' * 80) + '\n'

    # copy, remove totals
    df = dataframe1.copy()
    #df = df.T
    if just_totals:
        df = DataFrame(df.ix['Total'])
    else:
        try:
            df = df.drop('Total', axis = 0)
        except:
            pass
        try:
            df = df.drop('Total', axis = 1)
        except:
            pass
    
    # make df into just totals if need be
    #if just_totals:
        #df = df.ix['Total']

    # figure out if there's a second list
    # copy and remove totals if there is
    single_totals = False
    try:
        if dataframe2.empty is False:
            df2 = dataframe2.copy()
            #df2 = df2
            if type(df2) == pandas.core.frame.DataFrame:
                single_totals = False
                #if operation != '%':
                if just_totals:
                    df2 = DataFrame(df2.ix['Total'])
                else:
                    try:
                        df2 = df2.drop('Total', axis = 0)
                    except:
                        pass
                    try:
                        df2 = df2.drop('Total', axis = 1)
                    except:
                        pass
            elif type(df2) == pandas.core.series.Series:
                single_totals = True
                if just_totals:
                    df2 = DataFrame(df2)
                else:
                    df2 = df2.drop('Total', axis = 0)
            else:
                raise ValueError('dataframe2 not recognised.')   
    except AttributeError:
        pass



    # combine lists
    use_combiney = False
    try:
        if dataframe2.empty is False:
            use_combiney = True
            # set a threshold if just_totals
            if just_totals:
                the_threshold = set_threshold(df2, threshold)
            df = combiney(df, df2, operation = operation, threshold = the_threshold)
    except AttributeError:
        pass

    # chop up data as required
    if merge_entries:
        the_newname = newname_getter(df, parse_input(merge_entries), newname = newname)
    if just_entries:
        df = just_these_entries(df, parse_input(just_entries))
    if skip_entries:
        df = skip_these_entries(df, parse_input(skip_entries))
    if merge_entries:
        df = merge_these_entries(df, parse_input(merge_entries), the_newname)
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
        df = df[list(df.columns)[:keep_top]]

    print '\nResult (sample)'
    print '=' * 80
    print df.head()
    return df
        

