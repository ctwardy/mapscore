#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# hours_plot_cat.py

"""
Generate a plot of total hours vs. survival rate, given an Excel spreadsheet of
cases, each with the total hours in the first column, the subject status in 
the second column, and the subject category in the third.
"""

import math, sys, xlrd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


CMD_LINE_HELP = '''
Usage: python3 {} [spreadsheet filename] [options]

Options: 
 -H, --help         Show this help
 -C [categories]    Only use data from the listed categories (default: all)
 -L                 Display a trendline
 -B                 Display the variation using boxplots
 -E                 Display the variation using error bars (overrides -B)

For option -C, you can use group together categories with colons: 
 [...] -C Youth:Child Skier:Snowboarder [...]

Categories with spaces in their names should use "_" instead.
 "Substance Abuse" -> "Substance_Abuse"
'''


def read_cases(filename, sheet_index=0):
    book = xlrd.open_workbook(filename)
    sheet = book.sheet_by_index(sheet_index)
    days_slice = np.array(sheet.col_values(0))
    status_slice = np.array(sheet.col_values(1))
    category_slice = np.array(sheet.col_values(2))
    assert len(days_slice) == len(status_slice) == len(category_slice)
    return 24 * days_slice, status_slice, category_slice


def group_by_category(hours_slice, status_slice, category_slice):
    category_map = {}
    cases = zip(hours_slice, status_slice, category_slice)
    for hours, status, category in cases:
        if hours != '' and category != '':
            category, point = category.upper(), (hours, status)
            try:
                category_map[category].append(point)
            except KeyError:
                category_map[category] = [point]
    else:
        return category_map


def get_category_groups(category_map):
    try:
        index = sys.argv.index('-C') + 1
        while index < len(sys.argv):
            if sys.argv[index].startswith('-'):
                break
            yield sys.argv[index].upper().replace('_', ' ').split(':')
            index += 1
    except ValueError: # Default option: include all categories as one group
        yield list(category_map.keys())


def binify(hours, bin_scheme):
    """Return the hours bin for the supplied #hours and bin scheme."""
    if hours < 0:
        raise ValueError("Negative elapsed time passed to binify().")
    if hours is None:
        return -10
    for (lowerbound, upperbound), increment in bin_scheme.items():
        if lowerbound <= hours < upperbound:
            return int(math.ceil(hours / increment) * increment)
    raise ValueError("Unhandled value in binify(): {}".format(hours))


def is_doa(status):
    return 1 if status.upper() == 'DOA' else 0


def survival_rate(DOA_list):
    return (1.0 - float(DOA_list.count(1)) / len(DOA_list)) * 100


def bootstrap_resample(X, n=None):
    """ Bootstrap resample an array_like.

    Used for example, to estimate the variance for a single list of binary outcomes.

    Parameters
    ----------
    X : array_like
      data to resample
    n : int, optional
      length of resampled array, equal to len(X) if n==None
    Results
    -------
    returns X_resamples

    From http://nbviewer.ipython.org/gist/aflaxman/6871948
    """
    if n is None:
        n = len(X)

    resample_i = np.floor(np.random.rand(n) * len(X)).astype(int)
    return X[resample_i]


def add_trendline(x, y, N, color):
    z = np.polyfit(x, y, 1, w=N)
    p = np.poly1d(z)
    plt.plot(x, p(x), color + '-', alpha=0.7)
    print('Trendline: y = {:.3f}x + {:.3f}'.format(*z))


def main():
    if len(sys.argv) < 2 or '-H' in sys.argv or '--help' in sys.argv:
        exit(CMD_LINE_HELP.strip().format(sys.argv[0]))
    else:
        filename = sys.argv[1]

    hours_slice, status_slice, category_slice = read_cases(filename)
    print('Number of cases: {}'.format(len(hours_slice)))

    # Key: category, value: list of (hours, status) points
    category_map = group_by_category(hours_slice, status_slice, category_slice)
    category_groups = list(get_category_groups(category_map))

    # Key: (lowerbound inclusive, upperbound), value: increment size
    bin_scheme = {
        (0, 12): 1, 
        (12, 24): 3, 
        (24, 48): 6, 
        (48, 96): 12, 
        (96, float('inf')): 48
    }

    colors = 'rgbcyk'
    legend_patches, legend_labels = list(), list()
    for index, category_group in enumerate(category_groups):
        print('Group {}: {}'.format(index + 1, ', '.join(category_group)))

        # Key: binned hours, value: list of integers where 
        # "1" means the subject(s) was/were DOA, "0" means otherwise
        outcomes = {}
        for category in category_group:
            for (hours, status) in category_map[category]:
                binned_hours = binify(hours, bin_scheme)
                try:
                    outcomes[binned_hours].append(is_doa(status))
                except KeyError:
                    outcomes[binned_hours] = [is_doa(status)]

        # Lists for each number of total hours
        _x, _y, _N = list(), list(), list()
        for hours in sorted(outcomes.keys()):
            DOA_list = outcomes[hours]
            _x.append(hours)
            _y.append(survival_rate(DOA_list))
            _N.append(len(DOA_list))
            print('Survival rate at {} hours = {:.1f}% (N={})'.format(
                _x[-1], _y[-1], _N[-1]))

        # Lists for each (lowerbound, upperbound)
        x, y, N = list(), list(), list()
        boxplot_data = []
        for lowerbound, upperbound in bin_scheme:
            selected_hours = [hours for hours in _x
                                    if lowerbound <= hours < upperbound]
            survival_rates = [_y[_x.index(hours)] for hours in selected_hours]
            x.append(np.average(selected_hours))
            y.append(np.average(survival_rates))
            N.append(sum(_N[_x.index(hours)] for hours in selected_hours))
            if '-E' in sys.argv:
                stdev_y = np.std(survival_rates)
                plt.errorbar(x[-1], y[-1], 1.96 * stdev_y, 
                    ecolor=colors[index], alpha=0.2)
            elif '-B' in sys.argv:
                boxplot_data.append(survival_rates)

        # The points and variations ploted are for the
        # data within each (lowerbound, upperbound).
        plt.scatter(x, y, c=colors[index], s=N, alpha=0.5)
        label = ', '.join(category_group[:2])
        if len(category_group) > 2:
            label += ', OTHER'
        patch = mpatches.Patch(color=colors[index])
        legend_patches.append(patch)
        legend_labels.append(label)
        if '-T' in sys.argv[2:]:
            add_trendline(_x, _y, _N, colors[index])

        if '-B' in sys.argv[2:] and '-E' not in sys.argv[2:]:
            # To set the whiskers to the 95% range, 
            # use the optional argument whis=[2.5, 97.5]
            # Only works in matplotlib version > 1.4
            plt.boxplot(boxplot_data, positions=x, widths=[10] * len(x))

    plt.title('Total Hours vs. Survival Rate')
    plt.xlabel('Total Hours (hours)')
    plt.ylabel('Survival Rate (percent)')
    plt.legend(legend_patches, legend_labels, prop={'size' : 12})
    plt.xlim((0, 275))
    plt.ylim((0, 100))
    plt.xticks(range(0, 275, 50))
    plt.yticks(range(0, 101, 20))
    plt.get_current_fig_manager().resize(1250, 881)
    plt.show()


if __name__ == '__main__':
    main()
