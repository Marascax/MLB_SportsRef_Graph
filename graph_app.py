from flask import Flask, render_template, request, url_for, flash, redirect
import matplotlib.pyplot as plt
import re
import sys
import data_constants
import data_collect
import graph_gen

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
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
        xstat = re.search(stat_pattern, xstat).group(1)
        ystat = re.search(stat_pattern, ystat).group(1)
        print(xstat, ystat)

        x, y = data_collect.collect(xstat, ystat)
        graph_gen.generate(x, y)
        return render_template('index.html', terms=terms, result_image='static/images/result_plot.png', show_image='visible')