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
        return render_template('index.html', terms=terms, show_image='hidden')
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
            print("caught empty field")
            last_image = 'static/images/result_plot.png' if image_display else ''
            show_image = 'visible' if image_display else 'hidden'
            return render_template('index.html', terms=terms, result_image=last_image,
                                   show_image=show_image)

        # get setting for labeling
        overlap_setting = bool(request.form.get('labelSetting'))
        print(overlap_setting)

        x, y = data_collect.collect(xstat, ystat)
        # pixel coords of each logo, used to track where they are in relation to the image on the webpage
        pixels_x, pixels_y = graph_gen.generate(x, y, overlap_check=overlap_setting)

        # mapping each team abbreviation to their x and y pixel coord
        x_pixels = {}
        y_pixels = {}
        data = {}  # have the actual stat data for the actual hover text
        for i in range(30):
            team = data_constants.teams[i]
            x_pixels[team] = pixels_x[i]
            y_pixels[team] = pixels_y[i]
            data[team] = [x[i], y[i]]
        image_display = True
        return render_template('index.html', terms=terms,
                               pixels_x=x_pixels, stat_x=xstat,
                               pixels_y=y_pixels, stat_y=ystat,
                               data=data,
                               result_image='static/images/result_plot.png',
                               show_image='visible')


if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    # app.debug = False
    app.run(threaded=True, debug=False)
