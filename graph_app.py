from flask import Flask, render_template, request, url_for, flash, redirect, jsonify
import matplotlib.pyplot as plt
import re
import sys
import data_constants
import data_collect
import graph_gen

app = Flask(__name__)


image_display = False


@app.route('/', methods=['GET', 'POST'])
def index():
    global image_display
    verbose = data_constants.stats_from_verbose
    terms = []
    for key in verbose:
        terms.append(f'{key} ({verbose[key]})')
    if request.method == 'GET':
        print('GET')
        return render_template('index.html', terms=terms, data=None, show_image='hidden')
    if request.method == 'POST':
        print('POST')
        print(request.form['xstat'], request.form['ystat'])

        # get request form input for x and y stat
        xstat, ystat = request.form['xstat'], request.form['ystat']
        # use regex to extract each stat abbreviation
        stat_pattern = r'.+?\((.+?)\)'
        try:
            xstat = re.search(stat_pattern, xstat).group(1)
            ystat = re.search(stat_pattern, ystat).group(1)
            print(xstat, ystat)
        except AttributeError as ae:
            print("caught bad field")
            last_image = 'static/images/result_plot.png' if image_display else ''
            show_image = 'visible' if image_display else 'hidden'
            return render_template('index.html', terms=terms,
                                   data=None,
                                   result_image=last_image,
                                   show_image=show_image)

        # get setting for labeling
        overlap_setting = bool(request.form.get('labelSetting'))
        print(overlap_setting)

        x, y = data_collect.get_data(xstat, ystat)
        # pixel coords of each logo, used to track where they are in relation to the image on the webpage
        pixels_x, pixels_y = graph_gen.generate(x, y, overlap_check=overlap_setting)

        # mapping each team abbreviation to their x and y pixel coord
        x_pixels = {}
        y_pixels = {}
        plots = {}
        abbrev = data_constants.stats_to_verbose
        # hold everything needed in one dict to clean param passing and readibility
        data = {'xstat': xstat,
                'xround': data_constants.stat_rounding[abbrev[xstat]],
                'ystat': ystat,
                'yround': data_constants.stat_rounding[abbrev[ystat]]}
        for i in range(30):
            team = data_constants.teams[i]
            x_pixels[team] = pixels_x[i]
            y_pixels[team] = pixels_y[i]
            plots[team] = [x[i], y[i]]
        data['xpixels'] = x_pixels
        data['ypixels'] = y_pixels
        data['plots'] = plots
        image_display = True
        return render_template('index.html', terms=terms,
                               data=data,
                               result_image='static/images/result_plot.png',
                               show_image='visible')


if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    # app.debug = False
    app.run(threaded=True, debug=False)
