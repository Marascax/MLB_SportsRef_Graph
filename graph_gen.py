import math

import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.patheffects as path_effects
import data_constants
import adjustText
import os
from collections import namedtuple
from datetime import date


def get_image(path):
    return OffsetImage(plt.imread(path), zoom=0.3)


Bounds = namedtuple('Bounds', 'bottom_left top_right')
Point = namedtuple('Point', 'x y')

# TODO: future feature included in settings feature, remove any added text labels from overlap \
#  mainly since overlap doesn't account for inner transparent pixels
added_labels = {}
added_arrows = {}


def get_arrow_coordinates(text_bounds, img_bounds):
    ax = plt.gca()
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()

    # for adding text labels, calc small increment in relation to x and y scale
    xincrement = (xmax - xmin) / 1000
    yincrement = (ymax - ymin) / 1000
    increments = 3

    text_width = text_bounds.top_right.x - text_bounds.bottom_left.x
    text_height = text_bounds.top_right.y - text_bounds.bottom_left.y
    text_left, text_right = text_bounds.bottom_left.x, text_bounds.top_right.x
    text_bottom, text_top = text_bounds.bottom_left.y, text_bounds.top_right.y

    img_width = img_bounds.top_right.x - img_bounds.bottom_left.x
    img_height = img_bounds.top_right.y - img_bounds.bottom_left.y
    img_left, img_right = img_bounds.bottom_left.x, img_bounds.top_right.x
    img_bottom, img_top = img_bounds.bottom_left.y, img_bounds.top_right.y

    # left of image
    if text_right < img_left:
        arrow_x = text_right - (increments * xincrement)
    # right of image
    elif text_left > img_right:
        arrow_x = text_left + (increments * xincrement)
    # stuck halfway of image's left side
    elif text_left < img_left < text_right:
        arrow_x = text_right - (increments * xincrement)
    # stuck halfway of image's right side
    elif text_right > img_right > text_left:
        arrow_x = text_left + (increments * xincrement)
    # inbetween left and right
    else:
        arrow_x = text_left + (text_width / 2)

    # above image
    if text_bottom > img_top:
        arrow_y = text_bottom + (increments * yincrement)
    # below image
    elif text_top < img_bottom:
        arrow_y = text_top - (increments * yincrement)
    # stuck halfway of image's bottom
    elif text_bottom < img_bottom < text_top:
        arrow_y = text_top - (increments * yincrement)
    # stuck halfway of image's top
    elif text_top > img_top > text_bottom:
        arrow_y = text_bottom + (increments * yincrement)
    # inbetween top and bottom
    else:
        arrow_y = text_bottom + (text_height / 2)
    return arrow_x, arrow_y


def overlap_percent(bound_a, bound_b):
    # for a and b, get the left, right, top, and bottom side of their bounding box
    a_left, a_right = bound_a.bottom_left.x, bound_a.top_right.x
    a_bottom, a_top = bound_a.bottom_left.y, bound_a.top_right.y

    b_left, b_right = bound_b.bottom_left.x, bound_b.top_right.x
    b_bottom, b_top = bound_b.bottom_left.y, bound_b.top_right.y

    # calc amount of overlap in pixels
    # since they overlap, one's left or right side has to be within another,
    # same goes for top and bottom side
    area_overlap = ((min(a_right, b_right) - max(a_left, b_left))
                    * (min(a_top, b_top) - max(a_bottom, b_bottom)))

    # area of a and b bounding box
    area_bound_a = ((bound_a.top_right.x - bound_a.bottom_left.x)
                    * (bound_a.top_right.y - bound_a.bottom_left.y))
    area_bound_b = ((bound_b.top_right.x - bound_b.bottom_left.x)
                    * (bound_b.top_right.y - bound_b.bottom_left.y))

    # using area of overlap, area of both bounding boxes, calc the percentage of overlap
    overlap_percentage = area_overlap / area_bound_a
    return round(overlap_percentage, 3)


def overlapping_images(x, y, fig, ax, imgs):
    fig.canvas.draw()
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()

    # for adding text labels, calc small increment in relation to x and y scale
    xincrement = (xmax - xmin) / 1000
    yincrement = (ymax - ymin) / 1000

    # amount of overlap needed at minimum to result in editing graph
    overlap_threshold = 0.800
    boxes = []

    # get all the bounding boxes for the logos
    for img in imgs:
        # tight bbox gets bottom left (x0, x1) and top right corner (x1, y1) coords
        bbox = img.get_tightbbox(fig.canvas.get_renderer())
        bottom_left = Point(bbox.x0, bbox.y0)
        top_right = Point(bbox.x1, bbox.y1)
        boxes.append(Bounds(bottom_left, top_right))

    overlapped = []
    overlapper = []

    # iterate all possible pairs of logos to check for any overlap
    for i in range(len(boxes) - 1):
        bound_a = boxes[i]
        # text boxes are added at the end, so the first 30 boxes are actual mlb logos we want
        for j in range(i + 1, 30):
            bound_b = boxes[j]

            # check for intersection
            if not (bound_a.top_right.x < bound_b.bottom_left.x or bound_a.bottom_left.x > bound_b.top_right.x or
                    bound_a.top_right.y < bound_b.bottom_left.y or bound_a.bottom_left.y > bound_b.top_right.y):

                team_a = data_constants.teams[i]
                team_b = data_constants.teams[j]

                overlap_percentage = overlap_percent(bound_a, bound_b)
                if overlap_percentage >= overlap_threshold and i not in overlapped:
                    # print(f'Overlapping {team_a} and {team_b} {overlap_percentage * 100}%')
                    # track the logo being overlapped and logo that is causing the overlap
                    overlapped.append(i)
                    overlapper.append(j)

    # iterate through all logos being overlapped and label them based on the main logo overlapping it and
    # any surrounding logos
    for i, tm_a in enumerate(overlapped):
        team_a = data_constants.teams[tm_a]
        bound_a = boxes[tm_a]
        bound_b = boxes[overlapper[i]]

        # find text spot when only regarding the overlapper
        text_x, text_y = None, None
        coord_l, coord_b = ax.transData.inverted().transform(bound_a.bottom_left)
        coord_r, coord_t = ax.transData.inverted().transform(bound_a.top_right)
        mid_x = (bound_a.bottom_left.x + bound_a.top_right.x) / 2
        mid_y = (bound_a.bottom_left.y + bound_a.top_right.y) / 2
        coord_mx, coord_my = ax.transData.inverted().transform((mid_x, mid_y))

        arrow_x, arrow_y = x[tm_a], y[tm_a]
        # to the right of team b
        if bound_a.bottom_left.x > bound_b.bottom_left.x:
            text_x = coord_r + xincrement
            # print(f'right of b, x = {text_x}')
        # to the left of team b
        elif bound_a.top_right.x < bound_b.top_right.x:
            text_x = coord_l - xincrement
            # print(f'left of b, x = {text_x}')
        # higher than team b
        if bound_a.top_right.y > bound_b.top_right.y:
            text_y = coord_t + yincrement
            # print(f'top of b, y = {text_y}')
        # lower than team b
        elif bound_a.bottom_left.y < bound_b.bottom_left.y:
            text_y = coord_b - yincrement
            # print(f'bottom of b, y = {text_y}')

        # if team a and b 100% overlap (same left, right, top, bottom), it's better to label both teams
        # in the case that user couldn't tell there was another team behind team b
        if text_x is None and text_y is None:
            # default is just to the right of team b
            text_x = coord_r + xincrement
            text_y = coord_my
        # team a and b have the same left and right, set it to the middle
        if text_x is None:
            text_x = coord_mx
        # team a and b have same top and bottom
        if text_y is None:
            text_y = coord_my

        # print(f'text x,y = {text_x},{text_y}')
        # print(f'arrow x,y = {arrow_x},{arrow_y}')

        # create initial text annotation and find it's bounding box
        text = ax.text(text_x, text_y, team_a)
        fig.canvas.draw()
        text_bbox = text.get_window_extent()
        text_bottom_left = Point(text_bbox.x0, text_bbox.y0)
        text_top_right = Point(text_bbox.x1, text_bbox.y1)
        text_bounds = Bounds(text_bottom_left, text_top_right)
        text.remove()

        # get coords of where on label to end arrow
        arrow_x_pixels, arrow_y_pixels = get_arrow_coordinates(text_bounds, bound_a)
        # print(ax.transData.inverted().transform((arrow_x_pixels, arrow_y_pixels)))
        arrow = ax.annotate('', xy=(arrow_x, arrow_y),
                            xytext=ax.transData.inverted().transform((arrow_x_pixels, arrow_y_pixels)),
                            arrowprops=dict(arrowstyle='-', lw=1, color=data_constants.team_hex[tm_a]),
                            fontsize='small',
                            fontstretch='ultra-condensed')
        text = ax.text(text_x, text_y, team_a, weight='bold', color=data_constants.team_hex[tm_a])
        text.set_path_effects([path_effects.Stroke(linewidth=3, foreground='white'), path_effects.Normal()])

        pixel_x0, pixel_y0 = text_bbox.x0, text_bbox.y0
        pixel_x1, pixel_y1 = text_bbox.x1, text_bbox.y1

        text_pixel_width = pixel_x1 - pixel_x0
        text_pixel_height = pixel_y1 - pixel_y0

        # check if text needs to be readjusted since it's overlapped by another plot
        # this is essentially a check and see if only the overlapper is the issue, to avoid extra unneeded work
        readjust = False
        iteration = 0
        for k, box in enumerate(boxes):
            if k == tm_a:
                continue
            # check for any overlap
            if not (text_bounds.top_right.x < box.bottom_left.x or text_bounds.bottom_left.x > box.top_right.x or
                    text_bounds.top_right.y < box.bottom_left.y or text_bounds.bottom_left.y > box.top_right.y):
                text_overlap_percentage = overlap_percent(text_bounds, box)
                # print("box ", box)
                # print("text ", text_bounds)
                # print(f'{team_a} label & {data_constants.teams[k]} overlap {text_overlap_percentage * 100}')

                if text_overlap_percentage > 0.1:
                    readjust = True
                    arrow.remove()
                    text.remove()
                    break

        # more plots are causing overlap issue, continuously readjust until a spot is found
        while readjust:
            # for each iteration, go farther back and try spots around the logo
            iteration = iteration + 1
            xscale = xincrement * iteration
            yscale = yincrement * iteration

            # simplified spots completely around the logo
            coords = [(coord_l - xscale, coord_t + yscale), (coord_l - xscale, coord_b - yscale),
                      (coord_l - xscale, coord_my),
                      (coord_r + xscale, coord_t + yscale), (coord_r + xscale, coord_b - yscale),
                      (coord_r + xscale, coord_my),
                      (coord_mx, coord_t + yscale), (coord_mx, coord_b - yscale)]

            # check each possible text coord with current boxes
            for coord in coords:
                all_teams_clear = True
                # convert the coordinate into pixels and mimick the text's bounding box without drawing it
                coord_pixels_x0, coord_pixels_y0 = ax.transData.transform((coord[0], coord[1]))
                coord_pixels_x1 = coord_pixels_x0 + text_pixel_width
                coord_pixels_y1 = coord_pixels_y0 + text_pixel_height

                text_bottom_left = Point(coord_pixels_x0, coord_pixels_y0)
                text_top_right = Point(coord_pixels_x1, coord_pixels_y1)
                text_bounds = Bounds(text_bottom_left, text_top_right)

                # check theoretical bounding box against other boxes
                for k, box in enumerate(boxes):
                    if k == tm_a:
                        continue
                    if not (
                            text_bounds.top_right.x < box.bottom_left.x or text_bounds.bottom_left.x > box.top_right.x or
                            text_bounds.top_right.y < box.bottom_left.y or text_bounds.bottom_left.y > box.top_right.y):
                        text_overlap_percentage = overlap_percent(text_bounds, box)
                        # print(f'coords {coord[0]}, {coord[1]}')
                        # print(f'{team_a} label & {data_constants.teams[k]} overlap {text_overlap_percentage * 100}')

                        # if text would be covered by over half, stop early and try another
                        if text_overlap_percentage > 0.1:
                            all_teams_clear = False
                            break

                # once coord found that isn't overlapped, add arrow and put text over arrow
                if all_teams_clear:
                    arrow_x_pixels, arrow_y_pixels = get_arrow_coordinates(text_bounds, bound_a)
                    # print(ax.transData.inverted().transform((arrow_x_pixels, arrow_y_pixels)))
                    arrow = ax.annotate('', xy=(arrow_x, arrow_y),
                                        xytext=ax.transData.inverted().transform((arrow_x_pixels, arrow_y_pixels)),
                                        arrowprops=dict(arrowstyle='-', lw=1, color=data_constants.team_hex[tm_a]),
                                        fontsize='small',
                                        fontstretch='ultra-condensed', )
                    text = ax.text(coord[0], coord[1], team_a, weight='bold', color=data_constants.team_hex[tm_a])
                    text.set_path_effects([path_effects.Stroke(linewidth=3, foreground='white'), path_effects.Normal()])
                    readjust = False
                    # print(f'text x,y = {coord[0]},{coord[1]}')
                    # print(f'arrow x,y = {arrow_x},{arrow_y}')
                    break

        # add text to bounding boxes
        text_bbox = text.get_window_extent()
        text_bottom_left = Point(text_bbox.x0, text_bbox.y0)
        text_top_right = Point(text_bbox.x1, text_bbox.y1)
        boxes.append(Bounds(text_bottom_left, text_top_right))

        added_labels[team_a] = text
        added_arrows[team_a] = arrow

    return


def generate(x, y, text=False, overlap_check=True):
    """
    Generated graph given pandas Series for x- & y-axis
    :param overlap_check: check for logos that overlap and try to label hard to see plots
    :param text: use text labels for points instead of images
    :param x: x-axis data
    :param y: y-axis data
    """
    # increase spacing from axis tick label and axis itself
    plt.rcParams['xtick.major.pad'] = '6'
    plt.rcParams['ytick.major.pad'] = '6'

    fig, ax = plt.subplots(figsize=(15, 10))

    # increase axes limits to fit edge images inside graph
    xmin, xmax = x.min(), x.max()
    ymin, ymax = y.min(), y.max()
    xmean = x.mean()
    ymean = y.mean()

    x0, y0, width, height = ax.get_tightbbox(fig.canvas.get_renderer()).bounds

    x_pixels_per_unit = width / (xmax - xmin)
    y_pixels_per_unit = height / (ymax - ymin)

    new_xmin = math.floor((xmin - (75 / x_pixels_per_unit)) * 10) / 10
    new_xmax = math.ceil((xmax + (75 / x_pixels_per_unit)) * 10) / 10

    # set x and y axis to 4 ticks total with even spacing
    ax.set_xlim(new_xmin, new_xmax)
    diff = new_xmax - new_xmin
    xtick_one = round((1 / 3) * diff + new_xmin, 2)
    xtick_two = round(new_xmax - (1 / 3) * diff, 2)
    plt.xticks([new_xmin, xtick_one, xtick_two, new_xmax])

    new_ymin = math.floor((ymin - (75 / y_pixels_per_unit)) * 10) / 10
    new_ymax = math.ceil((ymax + (75 / y_pixels_per_unit)) * 10) / 10

    ax.set_ylim(new_ymin, new_ymax)
    diff = new_ymax - new_ymin
    ytick_one = round((1 / 3) * diff + new_ymin, 2)
    ytick_two = round(new_ymax - (1 / 3) * diff, 2)
    plt.yticks([new_ymin, ytick_one, ytick_two, new_ymax])

    ax.tick_params(axis=u'both', which=u'both', length=0)

    for axis in ['top', 'bottom', 'left', 'right']:
        ax.spines[axis].set_linewidth(0.2)

    # plot intersecting lines of the mean for main quadrants
    # print((new_xmin + new_xmax) / 2, xmean)
    plt.vlines(x=xmean, ymin=new_ymin, ymax=new_ymax,
               colors=(0.0, 0.0, 0.0, 1.0))

    # print((new_ymin + new_ymax) / 2, ymean)
    plt.hlines(y=ymean, xmin=new_xmin, xmax=new_xmax,
               colors=(0.0, 0.0, 0.0, 1.0))

    xincrement = (new_xmax - xtick_two) / 75
    yincrement = (new_ymax - ytick_two) / 75

    ax.text(xmean + xincrement, new_ymax - yincrement, fr'$\mathregular{{\mu}}$ = {round(xmean, 2)}', fontweight='bold',
            va='top')
    ax.text(new_xmax - xincrement, ymean - yincrement, fr'$\mathregular{{\mu}}$ = {round(ymean, 2)}', fontweight='bold',
            ha='right', va='top')

    # plot lines for each tick
    plt.vlines(x=xtick_one, ymin=new_ymin, ymax=new_ymax, linewidth=0.2,
               colors=(0.0, 0.0, 0.0, 0.5))
    plt.vlines(x=xtick_two, ymin=new_ymin, ymax=new_ymax, linewidth=0.2,
               colors=(0.0, 0.0, 0.0, 0.5))
    plt.hlines(y=ytick_one, xmin=new_xmin, xmax=new_xmax, linewidth=0.2,
               colors=(0.0, 0.0, 0.0, 0.5))
    plt.hlines(y=ytick_two, xmin=new_xmin, xmax=new_xmax, linewidth=0.2,
               colors=(0.0, 0.0, 0.0, 0.5))

    # add plot lines for whenever min x and/or y are < 0
    if new_xmin < 0:
        plt.vlines(x=0, ymin=new_ymin, ymax=new_ymax, linewidth=0.2,
                   colors=(0.0, 0.0, 0.0, 0.5))
        plt.xticks([new_xmin, 0, xtick_one, xtick_two, new_xmax])
    if new_ymin < 0:
        plt.hlines(y=0, xmin=new_xmin, xmax=new_xmax, linewidth=0.2,
                   colors=(0.0, 0.0, 0.0, 0.5))
        plt.yticks([new_ymin, 0, ytick_one, ytick_two, new_ymax])

    texts = []
    imgs = []
    for i, tm in enumerate(data_constants.teams):
        if text:
            # ax.annotate(tm, (x[i], y[i]))
            texts.append(ax.text(x[i], y[i], tm))
        else:
            off_image = get_image(
                f'{os.path.dirname(os.path.abspath(__file__))}/static/plot_logos{os.path.sep}{tm}.png')
            imgs.append(
                ax.add_artist(
                    AnnotationBbox(
                        off_image,
                        (x[i], y[i]),
                        xybox=(x[i], y[i]),
                        frameon=False
                    )
                )
            )

    if text:
        adjustText.adjust_text(texts)
    elif overlap_check:
        overlapping_images(x, y, fig, ax, imgs)

    x_abbrev, y_abbrev = x.name, y.name
    x_verbose, y_verbose = data_constants.stats_to_verbose[x_abbrev], data_constants.stats_to_verbose[y_abbrev]

    xincrement = (new_xmax - new_xmin) / 100
    yincrement = (new_ymax - new_ymin) / 100

    # top left
    ax.text(new_xmin + xincrement, new_ymax - yincrement, f'High {y_abbrev}\nLow {x_abbrev}', ha='left', va='top',
            color=(0.0, 0.0, 0.0, 0.4))
    # bottom left
    ax.text(new_xmin + xincrement, new_ymin + yincrement, f'Low {y_abbrev}\nLow {x_abbrev}', ha='left', va='bottom',
            color=(0.0, 0.0, 0.0, 0.4))
    # top right
    ax.text(new_xmax - xincrement, new_ymax - yincrement, f'High {y_abbrev}\nHigh {x_abbrev}', ha='right', va='top',
            color=(0.0, 0.0, 0.0, 0.4))
    # bottom right
    ax.text(new_xmax - xincrement, new_ymin + yincrement, f'Low {y_abbrev}\nHigh {x_abbrev}', ha='right', va='bottom',
            color=(0.0, 0.0, 0.0, 0.4))

    plt.xlabel(x_verbose, size=12)
    plt.ylabel(y_verbose, size=12)

    mid = (fig.subplotpars.right + fig.subplotpars.left) / 2

    d1 = date.today().strftime("%b %d, %Y")
    plt.suptitle(f'{x_verbose} vs {y_verbose}', ha='center', va='center', fontsize=16, weight='bold', x=mid)
    ax.set_title(f'As of {d1}', weight='ultralight', va='top')
    plt.tight_layout()
    fig.subplots_adjust(top=0.95)

    # plt.show()
    plt.draw()
    plt.savefig(f'{os.path.dirname(os.path.abspath(__file__))}/static/images/result_plot.png')

    # get and return the pixel locations for each logo
    graph_width, graph_height = fig.canvas.get_width_height()
    x_pixels = []
    y_pixels = []
    # convert the x and y limits of the graph to pixels
    xl, xr = ax.get_xlim()
    yb, yt = ax.get_ylim()
    xr_pixel, yt_pixel = ax.transData.transform((xr, yt))
    # might need this if the html affects the image resolution on the webpage
    x_diff = graph_width - xr_pixel
    y_diff = graph_height - yt_pixel
    for i in range(30):
        x_pixel, y_pixel = ax.transData.transform((x[i], y[i]))
        x_pixels.append(x_pixel)
        y_pixels.append(graph_height - y_pixel)
    return x_pixels, y_pixels
