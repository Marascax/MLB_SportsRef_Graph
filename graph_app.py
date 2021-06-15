import sys
import data_constants
import data_collect
import graph_gen

if __name__ == '__main__':
    if len(sys.argv) == 3:
        x_axis = None
        y_axis = None
        if sys.argv[1] in data_constants.stats_to_verbose:
            x_axis = sys.argv[1]
        elif sys.argv[1] in data_constants.stats_from_verbose:
            x_axis = data_constants.stats_from_verbose[sys.argv[1]]

        if sys.argv[2] in data_constants.stats_to_verbose:
            y_axis = sys.argv[2]
        elif sys.argv[2] in data_constants.stats_from_verbose:
            y_axis = data_constants.stats_from_verbose[sys.argv[2]]

        if x_axis and y_axis:
            x, y = data_collect.collect(x_axis, y_axis)
            graph_gen.generate(x, y)