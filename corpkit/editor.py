# a file for working with dataframes. most importantly, make a dataframe plotter.

def peditor(firstlist, 
            secondlist = False,
            operation = '%', 
            sort_by = False,
            
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

    import pandas as pd
    from pandas import DataFrame, Series

    # copy, remove totals
    df = firstlist.copy()
    df.drop('Total', axis = 0, inplace = True)
    df.drop('Total', axis = 1, inplace = True)

    # figure out if there's a second list, and figure out what it is
    single_totals = False
    try:
        if secondlist.empty is False:
            df2 = secondlist.copy()
            if type(df2) == pandas.core.frame.DataFrame:
                single_totals = False
                df2.drop('Total', axis = 0, inplace = True)
                df2.drop('Total', axis = 1, inplace = True)
            elif type(df2) == pandas.core.series.Series:
                single_totals = True
                #df2.drop('Total', axis = 0, inplace = True)
            else:
                raise ValueError('secondlist not recognised.')   

            # figure out what kind of second list we have

    except AttributeError:
        pass

    def combiney(firstlist, secondlist, operation = '%'):
        """mash firstlist and secondlist together in appropriate way"""
        if single_totals:
            print 'here'
            if operation == '%':
                print 'perc'
                edited_firstlist = firstlist * 100.0
                edited_firstlist = edited_firstlist.div(secondlist, axis=0)
            elif operation == '+':
                edited_firstlist = (firstlist.T + secondlist.T).T
            elif operation == '-':
                edited_firstlist = (firstlist.T - secondlist.T).T
            elif operation == '*':
                edited_firstlist = (firstlist.T * secondlist.T).T
            elif operation == '/':
                edited_firstlist = (firstlist.T / secondlist.T).T
            return edited_firstlist

        elif not single_totals:
            for entry in list(firstlist.columns):
                if operation == '%':
                    maths_done = firstlist[entry] * 100.0 / secondlist[entry]
                    firstlist.drop(entry, axis = 1, inplace = True)
                    firstlist[entry] = maths_done
                elif operation == '+':
                    maths_done = firstlist[entry] + secondlist[entry]
                    firstlist.drop(entry, axis = 1, inplace = True)
                    firstlist[entry] = maths_done
                elif operation == '-':
                    maths_done = firstlist[entry] - secondlist[entry]
                    firstlist.drop(entry, axis = 1, inplace = True)
                    firstlist[entry] = maths_done
                elif operation == '*':
                    maths_done = firstlist[entry] * secondlist[entry]
                    firstlist.drop(entry, axis = 1, inplace = True)
                    firstlist[entry] = maths_done
                elif operation == '/':
                    maths_done = firstlist[entry] / secondlist[entry]
                    firstlist.drop(entry, axis = 1, inplace = True)
                    firstlist[entry] = maths_done
        return firstlist

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
        print 'Keeping the following %d entries:\n\n%s\n' % (len(parsed_input), '\n'.join(parsed_input[:20]))
        if len(parsed_input) > 20:
            print '... and %d more ... \n' % len(parseD_input) - 20
        df.drop(entries, axis = 1, inplace = True)

    def skip_these_entries(parsed_input):
        print 'Skipping the following %d entries:\n\n%s\n' % (len(parsed_input), '\n'.join(parsed_input[:20]))
        if len(parsed_input) > 20:
            print '... and %d more ... \n' % len(parsed_input) - 20
        df.drop(parsed_input, axis = 1, inplace = True)

    def newname_getter(df, parsed_input, newname = False):
        """makes appropriate name for merged entries"""
        if type(newname) == int:
            the_newname = list(df.columns)[i]
        elif type(newname) == str:
            if newname == 'combine':
                the_newname = '/'.join(parsed_input)
        if newname is False:
            # revise this code
            import operator
            sumdict = {}
            for item in parsed_input:
                summed = sum(list(df[item]))
                sumdict[item] = summed
            the_newname = max(stats.iteritems(), key=operator.itemgetter(1))[0]
        if type(the_newname) != unicode:
            the_newname = unicode(the_newname, errors = 'ignore')
        return the_newname

    def merge_these_entries(parsed_input):
        # make new entry with sum of parsed input
        print 'Merging the following %d entries:%s' % (len(parsed_input), '\n'.join(parsed_input[:20]))
        if len(parsed_input) > 20:
            print '... and %d more ... \n' % len(parsed_input) - 20
        df[the_newname] = sum([df[i] for i in parsed_input])
        # remove old entries
        df.drop(parsed_input, axis = 1, inplace = True)

    def just_these_subcorpora(lst_of_subcorpora):
        if type(lst_of_subcorpora[0]) == int:
            lst_of_subcorpora = [str(l) for l in lst_of_subcorpora]
        good_years = [subcorpus for subcorpus in list(df.index) if subcorpus in lst_of_subcorpora]
        print 'Keeping the following %d subcorpora:\n\n%s\n' % (len(good_years), '\n'.join(good_years[:20]))
        if len(good_years) > 20:
            print '... and %d more ... \n' % len(good_years) - 20
        df.drop([subcorpus for subcorpus in list(df.index) if subcorpus not in good_years], axis = 0, inplace = True)

    def skip_these_subcorpora(lst_of_subcorpora):
        if type(lst_of_subcorpora) == int:
            lst_of_subcorpora = [lst_of_subcorpora]
        if type(lst_of_subcorpora[0]) == int:
            lst_of_subcorpora = [str(l) for l in lst_of_subcorpora]
        bad_years = [subcorpus for subcorpus in list(df.index) if subcorpus in lst_of_subcorpora]
        print 'Skipping the following %d subcorpora:\n\n%s\n' % (len(bad_years), '\n'.join(bad_years[:20]))
        if len(bad_years) > 20:
            print '... and %d more ... \n' % len(bad_years) - 20
        df.drop([subcorpus for subcorpus in list(df.index) if subcorpus in bad_years], axis = 0, inplace = True)

    def span_these_subcorpora(lst_of_subcorpora):
        good_years = [subcorpus for subcorpus in list(df.index) if int(subcorpus) >= lst_of_subcorpora[0] and int(subcorpus) <= lst_of_subcorpora[-1]]
        print 'Keeping subcorpora %d--%d' % (lst_of_subcorpora[0], lst_of_subcorpora[-1])
        df.drop([subcorpus for subcorpus in list(df.index) if subcorpus not in good_years], axis = 0, inplace = True)
        # retotal needed here
    
    def recalc(df):
        """Add totals to the dataframe"""
        df['Totals'] = df.sum(axis = 1, inplace = True)
        df = df.T
        df['Totals'] = df.sum(axis = 1, inplace = True)
        df = df.T
        return df

    # combine lists
    try:
        if secondlist.empty is False:
            df = combiney(df, df2, operation = '%')
    except AttributeError:
        pass

    if newname:
        the_newname = newname_getter(df, parse_input(merge_entries), newname = newname)
    if just_entries:
        just_these_entries(parse_input(just_entries))
    if skip_entries:
        skip_these_entries(parse_input(skip_entries))
    if merge_entries:
        merge_these_entries(parse_input(merge_entries))
    if just_subcorpora:
        just_these_subcorpora(just_subcorpora)
    if skip_subcorpora:
        skip_these_subcorpora(skip_subcorpora)
    if span_subcorpora:
        span_these_subcorpora(span_subcorpora)

    # drop infinites and nans
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.fillna(0.0)

    #recalculate totals
    df = recalc(df)

    # resort here

    return df
        