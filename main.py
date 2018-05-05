#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import psycopg2
import urlparse
import datetime
import math
import json
import random
import numpy as np
from flask import Flask, render_template, url_for, request, make_response, redirect

from boto.mturk.connection import MTurkConnection
from boto.mturk.question import ExternalQuestion
from boto.mturk.qualification import Qualifications, PercentAssignmentsApprovedRequirement, NumberHitsApprovedRequirement
from boto.mturk.price import Price

# CONFIG VARIABLES
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
MAPBOX_KEY = os.environ['MAPBOX_API_KEY']

# GMAPS_KEY = os.environ['GMAPS_KEY
# GMAPS_URL = "https://maps.googleapis.com/maps/api/js?key="+GMAPS_KEY+"&callback=initialize"

AWS_MT = False
DEV_ENVIROMENT_BOOLEAN = True
TASK_LIMIT = 5

# This allows us to specify whether we are pushing to the sandbox or live site.
if DEV_ENVIROMENT_BOOLEAN:
    AMAZON_HOST = "https://workersandbox.mturk.com/mturk/externalSubmit"
else:
    AMAZON_HOST = "https://www.mturk.com/mturk/externalSubmit"

# CONNECTING TO POSTGRES
'''
conn_string = "host='localhost' dbname='cs279' user='brianho' password=''"
print "Connecting to database ...\n	-> %s" % (conn_string)
conn = psycopg2.connect(conn_string)
'''
urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(os.environ["HEROKU_POSTGRESQL_ORANGE_URL"])
conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
    )
# conn.cursor will return a cursor object, you can use this cursor to perform queries
cursor = conn.cursor()
print "Connected!\n"

app = Flask(__name__, static_url_path='')
connection = MTurkConnection(aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, host=AMAZON_HOST)

# ROUTES FOR INTERNAL NAVIGATION
@app.route('/')
def main():
    AWS_MT = checkMT(request.args)
    if not AWS_MT:
        return render_template('consent.html')

# @app.route('/map')
# def map():
#     return render_template('map.html')

@app.route('/consent')
def consent():
    return render_template('consentAWS.html')

@app.route('/share', methods=['GET', 'POST'])
def share():

    if request.args.get("assignmentId") == "ASSIGNMENT_ID_NOT_AVAILABLE":
        resp = make_response(render_template("consentAWS.html"))
        resp.headers['x-frame-options'] = 'this_can_be_anything'
        return resp

    render_data = {
        "dev": DEV_ENVIROMENT_BOOLEAN,
        "mapbox_key": MAPBOX_KEY
        }
    resp = make_response(render_template("share.html", data = render_data))
    resp.headers['x-frame-options'] = 'this_can_be_anything'
    return resp

@app.route('/finish', methods=['GET', 'POST'])
def finish():
    return render_template('finish.html')

@app.route('/intro')
def intro():
    return render_template('intro.html')

# @app.route('/sorry')
# def sorry():
#     return render_template('sorry.html')

# ROUTE FOR GUESSING
@app.route('/guess', methods=['GET', 'POST'])
def guess():

    if request.args.get("assignmentId") == "ASSIGNMENT_ID_NOT_AVAILABLE":
        print "Showing AWS consent"
        resp = make_response(render_template("consentAWS.html"))
        resp.headers['x-frame-options'] = 'this_can_be_anything'
        return resp

    print "Starting guess task"

    # Get a random but least-seen image
    query = "SELECT name, url_360, x, y FROM images ORDER BY test_guess ASC, random() LIMIT 5;"
    cursor.execute(query)
    conn.commit()
    results = cursor.fetchall()

    AWS_MT = checkMT(request.args)
    render_data = {
        "dev": DEV_ENVIROMENT_BOOLEAN,
        "aws_MT": AWS_MT,
        "mapbox_key": MAPBOX_KEY,
        "images": [int(result[0]) for result in results],
        "img_urls": [result[1] for result in results],
        "lngs": [result[2] for result in results],
        "lats": [result[3] for result in results],
    }
    if AWS_MT:
        render_data.update({
            "amazon_host": AMAZON_HOST,
            "hitId": request.args.get("hitId"),
            "assignmentId" : request.args.get("assignmentId"),
            "workerId" : request.args.get("workerId")
        })
    else:
        render_data.update({
            "amazon_host":"NA",
            "hitId": "NA",
            "assignmentId" : "NA",
            "workerId" : "NA"
        })

    # print render_data
    resp = make_response(render_template("guess.html", data = render_data))
    resp.headers['x-frame-options'] = 'this_can_be_anything'
    return resp

# ROUTE FOR GUESSING
@app.route('/label', methods=['GET', 'POST'])
def label():

    if request.args.get("assignmentId") == "ASSIGNMENT_ID_NOT_AVAILABLE":
        resp = make_response(render_template("consentAWS.html"))
        resp.headers['x-frame-options'] = 'this_can_be_anything'
        return resp

    print "Starting label task"

    # Get a random but least-seen image
    query = "SELECT name, url FROM images ORDER BY test_label ASC, random() LIMIT 54;"
    cursor.execute(query)
    conn.commit()
    results = np.asarray(cursor.fetchall())
    mask = np.random.randint(0, results.shape[0], size=8)
    results_recall = np.asarray(results)[mask]
    # Get a random but least-seen image
    query = "SELECT name, url FROM images ORDER BY test_label ASC, random() LIMIT 12;"
    cursor.execute(query)
    conn.commit()
    results_extra = np.asarray(cursor.fetchall()).tolist()
    results_total = np.concatenate((results_recall, results_extra))
    np.random.shuffle(results_total)

    AWS_MT = checkMT(request.args)
    render_data = {
        "dev": DEV_ENVIROMENT_BOOLEAN,
        "aws_MT": AWS_MT,
        "mapbox_key": MAPBOX_KEY,
        "images": [int(result[0]) for result in results],
        "urls": [result[1] for result in results],
        "images_recall": [int(result[0]) for result in results_total],
        "urls_recall": [result[1] for result in results_total]
    }

    if AWS_MT:
        render_data.update({
            "amazon_host": AMAZON_HOST,
            "hitId": request.args.get("hitId"),
            "assignmentId" : request.args.get("assignmentId"),
            "workerId" : request.args.get("workerId")
        })
    else:
        render_data.update({
            "amazon_host":"NA",
            "hitId": "NA",
            "assignmentId" : "NA",
            "workerId" : "NA"
        })

    # print render_data
    resp = make_response(render_template("label.html", data = render_data))
    resp.headers['x-frame-options'] = 'this_can_be_anything'
    return resp

# ROUTE FOR SUBMISSION
@app.route('/submit', methods=['GET', 'POST'])
def submit():

    for arg in request.form.keys():
        print arg, request.form[arg]

    if request.form['task'] == 'guess':

        query = "INSERT INTO guess (hit_id, assignment_id, worker_id, time, image, guess_x, guess_y, find_time, dev, aws_mt) VALUES (%(hitId_)s, %(assignmentId_)s, %(workerId_)s, %(time_)s, %(image_)s, %(guessX_)s, %(guessY_)s, %(findTime_)s, %(dev_)s, %(aws_mt_)s);"

        cursor.execute(query, {
            'hitId_': request.form['hitId'],
            'assignmentId_': request.form['assignmentId'],
            'workerId_': request.form['workerId'],
            'time_': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z'),
            'image_': request.form['image'],
            'guessX_': request.form['guessX'],
            'guessY_': request.form['guessY'],
            'findTime_': request.form['findTime'],
            'dev_': request.form['dev'],
            'aws_mt_': request.form['aws_mt'],
            })
        conn.commit()

        '''
        count = get_trial_count('find', request.form['trial'], request.form['gen'])
        if count >= TASK_LIMIT:
            print "---DISABLING HIT"
            connection.disable_hit(request.form['hitId'])
        '''
        return redirect(url_for('intro'))

    elif request.form['task'] == 'label':
        # print request.form['labels']

        query = "INSERT INTO label (hit_id, assignment_id, worker_id, time, images, labels, dev, aws_mt) VALUES (%(hitId_)s, %(assignmentId_)s, %(workerId_)s, %(time_)s, %(images_)s, %(labels_)s, %(dev_)s, %(aws_mt_)s);"

        cursor.execute(query, {
            'hitId_': request.form['hitId'],
            'assignmentId_': request.form['assignmentId'],
            'workerId_': request.form['workerId'],
            'time_': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z'),
            'images_': request.form['images'],
            'labels_': request.form['labels'],
            # 'category_': request.form['category'],
            'dev_': request.form['dev'],
            'aws_mt_': request.form['aws_mt']
            })
        conn.commit()

        return redirect(url_for('intro'))

    elif request.form['task'] == 'share':
        query = "INSERT INTO memory (time, memx, memy, memory, name, email) VALUES (%(time_)s, %(memX_)s, %(memY_)s, %(memory_)s, %(name_)s, %(email_)s);"

        cursor.execute(query, {
            'memX_': request.form['memX'],
            'memY_': request.form['memY'],
            'memory_': request.form['memory'],
            'time_': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z'),
            'name_': request.form['username'],
            'email_': request.form['email']
            })
        conn.commit()
        return redirect(url_for('intro'))

# ROUTE FOR SUBMISSION
@app.route('/score', methods=['GET', 'POST'])
def score():
    query = "INSERT INTO score (time, avg_dist, total_time) VALUES (%(time_)s, %(avg_dist_)s, %(total_time_)s) RETURNING id;"

    cursor.execute(query, {
        'time_': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z'),
        'avg_dist_': request.form['avg_dist'],
        'total_time_': request.form['total_time']
        })
    conn.commit()
    id = cursor.fetchone()[0]

    query = "SELECT id, avg_dist FROM score ORDER BY avg_dist ASC;"
    cursor.execute(query)
    conn.commit()
    results = cursor.fetchall()

    rank_score = [result[0] for result in results].index(id) + 1
    high_score = results[0][1]

    query = "SELECT id, total_time FROM score ORDER BY total_time ASC;"
    cursor.execute(query)
    conn.commit()
    results = cursor.fetchall()
    rank_time = [result[0] for result in results].index(id) + 1
    high_time = results[0][1]

    print "Rank: %s %s" % (rank_score, rank_time)

    render_data = {
        "your_score": "%0.2f" % (float(request.form["avg_dist"])),
        "your_time":  "%0.2f" % (float(request.form["total_time"])),
        "your_rank_score" : rank_score,
        "your_rank_time" : rank_time,
        "high_score": "%0.2f" % (high_score),
        "high_time": "%0.2f" % (high_time)
    }

    resp = make_response(render_template("score.html", data = render_data))
    resp.headers['x-frame-options'] = 'this_can_be_anything'
    return resp

def checkMT(args):
    if  "assignmentId" in args:
        return True
    else:
        return False

if __name__ == "__main__":
    # app.debug = DEBUG
    app.run(threaded=True)
