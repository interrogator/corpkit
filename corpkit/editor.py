# a file for working with dataframe1s. most importantly, make a dataframe1 plotter.

def editor(dataframe1, 
            operation = '%',
            dataframe2 = False,
            sort_by = False,
            keep_stats = False,
            
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

    print '\nProcessing\n' + ('=' * 40) + '\n'

    # copy, remove totals
    df = dataframe1.copy().T
    #df = df.T
        #df.drop('Total', axis = 0, inplace = True)
        #df.drop('Total', axis = 1, inplace = True)

    # figure out if there's a second list, and figure out what it is
    single_totals = False
    try:
        if dataframe2.empty is False:
            df2 = dataframe2.copy()
            df2 = df2.T
            if type(df2) == pandas.core.frame.DataFrame1:
                single_totals = False
                #if operation != '%':
                #df2.drop('Total', axis = 0, inplace = True)
                #df2.drop('Total', axis = 1, inplace = True)
            elif type(df2) == pandas.core.series.Series:
                single_totals = True
                #if operation != '%':
                    #df2.drop('Total', axis = 0, inplace = True)
            else:
                raise ValueError('dataframe2 not recognised.')   

            # figure out what kind of second list we have

    except AttributeError:
        pass

    def combiney(df, df2, operation = '%'):
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
                df = (df.T / df2.T).T
            return df

        elif not single_totals:
            for entry in list(df.columns):
                if operation == '%':
                    maths_done = df[entry] * 100.0 / df2[entry]
                    df.drop(entry, axis = 1, inplace = True)
                    df[entry] = maths_done
                elif operation == '+':
                    maths_done = df[entry] + df2[entry]
                    df.drop(entry, axis = 1, inplace = True)
                    df[entry] = maths_done
                elif operation == '-':
                    maths_done = df[entry] - df2[entry]
                    df.drop(entry, axis = 1, inplace = True)
                    df[entry] = maths_done
                elif operation == '*':
                    maths_done = df[entry] * df2[entry]
                    df.drop(entry, axis = 1, inplace = True)
                    df[entry] = maths_done
                elif operation == '/':
                    maths_done = df[entry] / df2[entry]
                    df.drop(entry, axis = 1, inplace = True)
                    df[entry] = maths_done
        return df

    def parse_input(input):
        """turn whatever has been passed in into list of words"""
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

    def just_these_entries(parsed_input):
        entries = [word for word in list(df) if word not in parsed_input]
        print 'Keeping %d entries:\n    %s\n' % (len(parsed_input), '\n    '.join(parsed_input[:20]))
        if len(parsed_input) > 20:
            print '... and %d more ... \n' % len(parseD_input) - 20
        df.drop(entries, axis = 1, inplace = True)

    def skip_these_entries(parsed_input):
        print 'Skipping %d entries:\n    %s\n' % (len(parsed_input), '\n    '.join(parsed_input[:20]))
        if len(parsed_input) > 20:
            print '... and %d more ... \n' % len(parsed_input) - 20
        df.drop(parsed_input, axis = 1, inplace = True)

    def newname_getter(df, parsed_input, newname = 'combine'):
        """makes appropriate name for merged entries"""
        print parsed_input
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

    def merge_these_entries(parsed_input, the_newname):
        # make new entry with sum of parsed input
        print 'Merging %d entries as "%s":\n    %s\n' % (len(parsed_input), the_newname, '\n    '.join(parsed_input[:20]))
        if len(parsed_input) > 20:
            print '... and %d more ... \n' % len(parsed_input) - 20
        df[the_newname] = sum([df[i] for i in parsed_input])
        # remove old entries
        df.drop(parsed_input, axis = 1, inplace = True)

    def just_these_subcorpora(lst_of_subcorpora):
        if type(lst_of_subcorpora[0]) == int:
            lst_of_subcorpora = [str(l) for l in lst_of_subcorpora]
        good_years = [subcorpus for subcorpus in list(df.index) if subcorpus in lst_of_subcorpora]
        print 'Keeping %d subcorpora:\n    %s\n' % (len(good_years), '\n    '.join(good_years[:20]))
        if len(good_years) > 20:
            print '... and %d more ... \n' % len(good_years) - 20
        df.drop([subcorpus for subcorpus in list(df.index) if subcorpus not in good_years], axis = 0, inplace = True)

    def skip_these_subcorpora(lst_of_subcorpora):
        if type(lst_of_subcorpora) == int:
            lst_of_subcorpora = [lst_of_subcorpora]
        if type(lst_of_subcorpora[0]) == int:
            lst_of_subcorpora = [str(l) for l in lst_of_subcorpora]
        bad_years = [subcorpus for subcorpus in list(df.index) if subcorpus in lst_of_subcorpora]
        print 'Skipping %d subcorpora:\n    %s\n' % (len(bad_years), '\n    '.join(bad_years[:20]))
        if len(bad_years) > 20:
            print '... and %d more ... \n' % len(bad_years) - 20
        df.drop([subcorpus for subcorpus in list(df.index) if subcorpus in bad_years], axis = 0, inplace = True)

    def span_these_subcorpora(lst_of_subcorpora):
        non_totals = [subcorpus for subcorpus in list(df.index) if subcorpus != 'Total']
        good_years = [subcorpus for subcorpus in non_totals if int(subcorpus) >= int(lst_of_subcorpora[0]) and int(subcorpus) <= int(lst_of_subcorpora[-1])]
        print 'Keeping subcorpora:\n    %d--%d' % (int(lst_of_subcorpora[0]), int(lst_of_subcorpora[-1]))
        df.drop([subcorpus for subcorpus in list(df.index) if subcorpus not in good_years], axis = 0, inplace = True)
        # retotal needed here
    
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
        try:
            df.drop('Total', axis = 0, inplace = True)
        except:
            pass
        try:
            df.drop('Total', axis = 1, inplace = True)
        except:
            pass
        df['Total'] = df.sum(axis = 1, inplace = True)
        df = df.T
        df['Total'] = df.sum(axis = 1, inplace = True)
        df = df.T
        return df

    def resort(df, sort_by, keep_stats = False):
        # translate options and make sure they are parseable
        options = ['total', 'name', 'infreq', 'increase', 'decrease', 'static', 'most', 'least', 'none']
        if sort_by is True:
            sort_by = 'total'
        if sort_by == 'most':
            sort_by = 'total'
        if sort_by == 'least':
            sort_by = 'infreq'
        if sort_by not in options:
            raise ValueError("sort_by parameter error: '%s' not recognised. Must be True, False, %s" % (sort_by, ', '.join(options)))

        if sort_by == 'total':
            df = recalc(df)
            tot = df.ix['Total']
            df = df[tot.argsort()[::-1]]
            df.drop('Total', inplace = True, axis = 1)
            df = recalc(df)
        elif sort_by == 'infreq':
            df = recalc(df)
            tot = df.ix['Total']
            df = df[tot.argsort()]
            df.drop('Total', inplace = True, axis = 1)
            df = recalc(df)
        elif sort_by == 'name':
            # currently case sensitive...
            df = df.reindex_axis(sorted(df.columns), axis=1)
            df = recalc(df)
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
            move_totals.remove('Total')
            move_totals.append('Total')

            # remove stats field by default
            if not keep_stats:
                df.drop(statfields, inplace = True)

            # or, remove them from the columns list and add them to the end
            else:
                for stat in statfields:
                    move_totals.remove(stat)
                    move_totals.append(stat)

            # reorder with totals and stats at end
            df = df[move_totals]

            #elif sort_by == 'static':
                #reordered = 

            if operation != '%':
                df = recalc(df)
        return df

    # combine lists
    use_combiney = False
    try:
        if dataframe2.empty is False:
            use_combiney = True
            df = combiney(df, df2, operation = operation)
    except AttributeError:
        pass

    if merge_entries:
        the_newname = newname_getter(df, parse_input(merge_entries), newname = newname)
    if just_entries:
        just_these_entries(parse_input(just_entries))
    if skip_entries:
        skip_these_entries(parse_input(skip_entries))
    if merge_entries:
        merge_these_entries(parse_input(merge_entries), the_newname)
    if just_subcorpora:
        just_these_subcorpora(just_subcorpora)
    if skip_subcorpora:
        skip_these_subcorpora(skip_subcorpora)
    if span_subcorpora:
        span_these_subcorpora(span_subcorpora)

    # drop infinites and nans
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.fillna(0.0)

    if not use_combiney:
        df = recalc(df)

    # resort here
    if sort_by:
        df = resort(df, keep_stats = keep_stats, sort_by = sort_by)
    
    print '\nResult (sample)'
    print '=' * 40


    print df.head()
    return df
        

