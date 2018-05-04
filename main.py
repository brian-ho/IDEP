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
DEV_ENVIROMENT_BOOLEAN = False
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
url = urlparse.urlparse(os.environ["DATABASE_URL"])
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

    if needConsent(request.args):
        return redirect(url_for('consent'))

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

    if needConsent(request.args):
        return redirect(url_for('consent'))

    # Get a random but least-seen image
    query = "SELECT name, url FROM images ORDER BY test_label ASC, random() LIMIT 36;"
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
    print results

    rank_score = [result[0] for result in results].index(id)
    high_score = results[0][1]

    query = "SELECT id, total_time FROM score ORDER BY total_time ASC;"
    cursor.execute(query)
    conn.commit()
    results = cursor.fetchall()
    rank_time = [result[0] for result in results].index(id)
    high_time = results[0][1]

    print rank_score, rank_time
    print high_score, high_time

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

'''
# ROUTE FOR FIND TASK
@app.route('/find', methods=['GET', 'POST'])
def find():
    if request.args.get("assignmentId") == "ASSIGNMENT_ID_NOT_AVAILABLE":
        # Our worker hasn't accepted the HIT (task) yet
        print "CONSENT"
        resp = make_response(render_template("consent.html"))
        resp.headers['x-frame-options'] = 'this_can_be_anything'
        return resp

    else:
        # Our worker accepted the task
        trial_info = getTrialInfo(request.args)
        print "FINDING: TRIAL %i" % trial_info[3]
        if workerIdCheck(request.args, trial_info[3]):
            print "---SORRY!"

            print "---DISABLING HIT"
            connection.disable_hit(request.args.get("hitId"))

            resp = make_response(render_template("sorry.html"))
            resp.headers['x-frame-options'] = 'this_can_be_anything'
            return resp

        else:
            if "hitId" in request.args:

                if get_trial_count('find', trial_info[3], trial_info[4]) >= TASK_LIMIT:
                    print "---SORRY!"
                    resp = make_response(render_template("sorry.html"))
                    resp.headers['x-frame-options'] = 'this_can_be_anything'
                    return resp

                else:
                    render_data = {
                        "amazon_host": AMAZON_HOST,
                        "hit_id": request.args.get("hitId"),
                        "assignment_id" : request.args.get("assignmentId"),
                        "worker_id": request.args.get("workerId"),
                        "trial": trial_info[3],
                        "gen": trial_info[4],
                        "trial_info": {'lat':trial_info[0], 'lng':trial_info[1]},
                        "description": trial_info[2],
                        "gmaps_url": GMAPS_URL
                        }

            else:
                render_data = {
                    "amazon_host": AMAZON_HOST,
                    "hit_id": "dummy_hitId", #request.args.get("hitId"),
                    "assignment_id" : "dummy_assignment_id", #request.args.get("assignmentId"),
                    "worker_id": "dummy_workerId", #request.args.get("workerId"),
                    "trial": trial_info[3],
                    "gen": trial_info[4],
                    "trial_info": {'lat':trial_info[0], 'lng':trial_info[1]},
                    "description": trial_info[2],
                    "gmaps_url": GMAPS_URL
                    }

            log_task_init(render_data, 'find')
            resp = make_response(render_template("find.html", name = render_data))
            resp.headers['x-frame-options'] = 'this_can_be_anything'
            return resp
    return

# ROUTE FOR VERIFY TASK
@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.args.get("assignmentId") == "ASSIGNMENT_ID_NOT_AVAILABLE":
        # Our worker hasn't accepted the HIT (task) yet
        print "CONSENT"
        resp = make_response(render_template("consent.html"))
        resp.headers['x-frame-options'] = 'this_can_be_anything'
        return resp

    else:
        # Our worker accepted the task
        trial_info = getTrialInfo(request.args)
        print "VERIFYING: TRIAL %i" % trial_info[3]
        if workerIdCheck(request.args, trial_info[3]):
            print "---SORRY!"

            print "---DISABLING HIT"
            connection.disable_hit(request.args.get("hitId"))

            resp.headers['x-frame-options'] = 'this_can_be_anything'
            return resp

        else:

            print "---GETTING FIND TASKS"
            # query = "SELECT pitch, heading, zoom, find_id FROM find WHERE trial = %(trial_)s AND gen = %(gen_)s AND hit_id NOT LIKE 'dummy%%' ORDER BY time DESC LIMIT 4;"
            query = "SELECT pitch, heading, zoom, find_id FROM find WHERE trial = %(trial_)s AND gen = %(gen_)s ORDER BY time LIMIT %(limit_)s;"
            cursor.execute(query, {'trial_':trial_info[3], 'gen_':trial_info[4], 'limit_':TASK_LIMIT})
            conn.commit()
            results = cursor.fetchall()

            imgs = []
            for i, result in enumerate(results):
                imgs.append([result[0],result[1],zoom_to_FOV(result[2]),result[3]])

            if "hitId" in request.args:

                if get_trial_count('verify', trial_info[3], trial_info[4]) >= TASK_LIMIT:
                    print "---SORRY!"

                    print "---DISABLING HIT"
                    connection.disable_hit(request.args.get("hitId"))

                    resp = make_response(render_template("sorry.html"))
                    resp.headers['x-frame-options'] = 'this_can_be_anything'
                    return resp

                else:
                    render_data = {
                        "amazon_host": AMAZON_HOST,
                        "hit_id": request.args.get("hitId"),
                        "assignment_id" : request.args.get("assignmentId"),
                        "worker_id": request.args.get("workerId"),
                        "trial": trial_info[3],
                        "gen": trial_info[4],
                        "trial_info": {'lat':trial_info[0], 'lng':trial_info[1]},
                        "description": trial_info[2],
                        "images": imgs,
                        "total": len(imgs),
                        "gmaps_key": GMAPS_KEY
                        }
            else:
                render_data = {
                    "amazon_host": AMAZON_HOST,
                    "hit_id": "dummy_hitId",
                    "assignment_id" : "dummy_assignment_id",
                    "worker_id": "dummy_workerId",
                    "trial": trial_info[3],
                    "gen": trial_info[4],
                    "trial_info": {'lat':trial_info[0], 'lng':trial_info[1]},
                    "description": trial_info[2],
                    "images": imgs,
                    "total": len(imgs),
                    "gmaps_key": GMAPS_KEY
                }
            print "---RENDERING"
            log_task_init(render_data, 'verify')
            resp = make_response(render_template("verify.html", name = render_data))
            resp.headers['x-frame-options'] = 'this_can_be_anything'
            return resp
    return

# ROUTE FOR RANK TASK
@app.route('/rank')#, methods=['GET', 'POST'])
def rank():
    if request.args.get("assignmentId") == "ASSIGNMENT_ID_NOT_AVAILABLE":
        print "CONSENT"
        resp = make_response(render_template("consent.html"))
        resp.headers['x-frame-options'] = 'this_can_be_anything'
        return resp

    else:
        # Our worker accepted the task
        trial_info = getTrialInfo(request.args)
        print "RANKING: TRIAL %i" % trial_info[3]
        if workerIdCheck(request.args, trial_info[3]):
            print "---SORRY!"
            resp = make_response(render_template("sorry.html"))
            resp.headers['x-frame-options'] = 'this_can_be_anything'
            return resp

        # query = "SELECT find_id, updated FROM find WHERE invalid_count <= 1 AND trial = %(trial_)s AND gen = %(gen_)s AND hit_id NOT LIKE 'dummy%%' ORDER BY time DESC LIMIT 8;"
        query = "SELECT find_id, updated FROM find WHERE invalid_count <= 1 AND trial = %(trial_)s AND gen = %(gen_)s ORDER BY time DESC LIMIT %(limit_)s;"
        cursor.execute(query, {'trial_': trial_info[3], 'gen_': trial_info[4], 'limit_':TASK_LIMIT})
        conn.commit()

        results = cursor.fetchall()
        descriptions = []
        descriptions = [{'find_id':result[0],'text':result[1]} for result in results]
        descriptions.append({'find_id':9999, 'text':trial_info[2]})

        if "hitId" in request.args:

            if get_trial_count('rank', trial_info[3], trial_info[4]) >= TASK_LIMIT:
                print "---SORRY!"
                resp = make_response(render_template("sorry.html"))
                resp.headers['x-frame-options'] = 'this_can_be_anything'
                return resp

            else:
                render_data = {
                    "amazon_host": AMAZON_HOST,
                    "hit_id": request.args.get("hitId"),
                    "assignment_id" : request.args.get("assignmentId"),
                    "worker_id": request.args.get("workerId"),
                    "trial": trial_info[3],
                    "gen": trial_info[4],
                    "trial_info": {'lat':trial_info[0], 'lng':trial_info[1]},
                    "descriptions": descriptions,
                    "gmaps_url": GMAPS_URL
                    }
        else:
            render_data = {
                "amazon_host": AMAZON_HOST,
                "hit_id": "dummy_hitId", #request.args.get("hitId"),
                "assignment_id" : "dummy_assignment_id", #request.args.get("assignmentId"),
                "worker_id": "dummy_workerId", #request.args.get("workerId"),
                "trial": trial_info[3],
                "gen": trial_info[4],
                "trial_info": {'lat':trial_info[0], 'lng':trial_info[1]},
                "descriptions": descriptions,
                "gmaps_url": GMAPS_URL
                }

        log_task_init(render_data, 'rank')
        resp = make_response(render_template("rank.html", name = render_data))
        resp.headers['x-frame-options'] = 'this_can_be_anything'
        return resp
    return

# ROUTE FOR SUBMISSION
@app.route('/submit', methods=['GET', 'POST'])
def submit():
    print "SUBMITTED %s TASK" % (request.form['task'].upper())
    for key,value in request.form.iterlists():
        print "---", key, value

    if request.form['task'] == 'find':

        query = "INSERT INTO find (hit_id, assignment_id, worker_id, original, updated, time, pitch, heading, zoom, find_time, trial, gen) VALUES (%(hitId_)s, %(assignmentId_)s, %(workerId_)s, %(original_)s, %(updated_)s, %(time_)s, %(pitch_)s, %(heading_)s, %(zoom_)s, %(findTime_)s, %(trial_)s, %(gen_)s);"
        cursor.execute(query, {
            'hitId_': request.form['hitId'],
            'assignmentId_': request.form['assignmentId'],
            'workerId_': request.form['workerId'],
            'original_': request.form['original'],
            'updated_': request.form['updated'],
            'time_': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z'),
            'pitch_': request.form['pitch'],
            'heading_': request.form['heading'],
            'zoom_': request.form['zoom'],
            'findTime_': request.form['findTime'],
            'trial_': request.form['trial'],
            'gen_': request.form['gen']
            })
        conn.commit()

        count = get_trial_count('find', request.form['trial'], request.form['gen'])
        if count >= TASK_LIMIT:
            print "---DISABLING HIT"
            connection.disable_hit(request.form['hitId'])
            # post_HIT('verify', request.form['trial'])

    elif request.form['task'] == 'verify':
        v = []
        ids = []
        for i in range(1, int(request.form['total'])+1):
            print "---CHECKING IMG %i" %i
            if 'img%i' % i in request.form:
                v.append(1)
                ids.append(request.form['find_id%i' % i])
                query = "UPDATE find SET valid_count = valid_count + 1 WHERE find_id = %(find_id_)s;"
                cursor.execute(query, {'find_id_': request.form['find_id%i' % i]})
                conn.commit()

            else:
                v.append(0)
                ids.append(request.form['find_id%i' % i])
                query = "UPDATE find SET invalid_count = invalid_count + 1 WHERE find_id = %(find_id_)s;"
                cursor.execute(query, {'find_id_': request.form['find_id%i' % i]})
                conn.commit()

        query = "INSERT INTO verify (hit_id, assignment_id, worker_id, time, trial, gen, valid, invalid) VALUES (%(hitId_)s, %(assignmentId_)s, %(workerId_)s, %(time_)s, %(trial_)s, %(gen_)s, %(valid_)s, %(invalid_)s);"
        cursor.execute(query, {
            'hitId_': request.form['hitId'],
            'assignmentId_': request.form['assignmentId'],
            'workerId_': request.form['workerId'],
            'time_': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z'),
            'trial_': request.form['trial'],
            'gen_': request.form['gen'],
            'valid_': [id_ for i, id_ in enumerate(ids) if v[i] == 1],
            'invalid_': [id_ for i, id_ in enumerate(ids) if v[i] == 0],
            })
        conn.commit()

        count = get_trial_count('verify', request.form['trial'], request.form['gen'])
        if count >= TASK_LIMIT:
            print "---DISABLING HIT"
            connection.disable_hit(request.form['hitId'])
            # post_HIT('rank', request.form['trial'])

    elif request.form['task'] == 'rank':

        ranking = json.loads(request.form['order'])
        if len(ranking) < 10:
            for i in range(10-len(ranking)):
                ranking.append(-9999)

        print ranking

        query = "INSERT INTO rank (hit_id, assignment_id, worker_id, time, trial, gen, rank0, rank1, rank2, rank3, rank4, rank5, rank6, rank7, rank8, rank9) VALUES (%(hitId_)s, %(assignmentId_)s, %(workerId_)s, %(time_)s, %(trial_)s, %(gen_)s, %(r0_)s, %(r1_)s, %(r2_)s, %(r3_)s, %(r4_)s, %(r5_)s, %(r6_)s, %(r7_)s, %(r8_)s, %(r9_)s);"
        cursor.execute(query, {
            'hitId_': request.form['hitId'],
            'assignmentId_': request.form['assignmentId'],
            'workerId_': request.form['workerId'],
            'time_': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z'),
            'trial_': request.form['trial'],
            'gen_': request.form['gen'],
            'r0_': ranking[0],
            'r1_': ranking[1],
            'r2_': ranking[2],
            'r3_': ranking[3],
            'r4_': ranking[4],
            'r5_': ranking[5],
            'r6_': ranking[6],
            'r7_': ranking[7],
            'r8_': ranking[8],
            'r9_': ranking[9],
            })
        conn.commit()

        count = get_trial_count('rank', request.form['trial'], request.form['gen'])
        if count >= TASK_LIMIT:
            print "---DISABLING HIT"
            connection.disable_hit(request.form['hitId'])

    resp = make_response(render_template("home.html"))
    resp.headers['x-frame-options'] = 'this_can_be_anything'
    return resp

# FUNCTION TO LOG EACH TASK
def log_task_init(render_data, task_):
    # Retrieve relevant data
    hitId_ = render_data['hit_id']
    assignmentId_ = render_data['assignment_id']
    workerId_ = render_data['worker_id']
    trial_ = render_data['trial']
    gen_ = render_data['gen']

    # Log the HIT
    query = "INSERT INTO tracking (hit_id, assignment_id, worker_id, task, status, time, trial, gen) VALUES (%(hitId_)s, %(assignmentId_)s, %(workerId_)s, %(task_)s, 'started', %(time_)s, %(trial_)s, %(gen_)s) RETURNING id;"
    cursor.execute(query, {
        'time_': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z'),
        'hitId_': hitId_, 'assignmentId_': assignmentId_,
        'workerId_': workerId_,
        'task_': task_,
        'trial_': trial_,
        'gen_': gen_
        })
    conn.commit()
    print "---TRACKING ID", cursor.fetchone()[0]
    return

def getTrialInfo(args_):
    if 'trial' in args_:
        trial = args_['trial']
    else:
        trial = random.randint(0, 2)

    query = "SELECT lat, lng, description, trial, gen FROM descriptions WHERE trial = %(trial_)s ORDER BY gen DESC LIMIT 1;"
    cursor.execute(query, {"trial_":trial})
    conn.commit()
    trial_info = cursor.fetchone()
    return trial_info

def workerIdCheck(args_, trial):
    if 'workerId' in args_:
        print "---CHECKING WORKER %s" % args_['workerId']
        query = "SELECT COUNT(*) FROM find WHERE worker_id = %(workerId_)s and trial = %(trial_)s;"
        cursor.execute(query, {"workerId_":request.args["workerId"], "trial_":trial})
        conn.commit()
        check = cursor.fetchone()[0]

        print "---WORKER HAS DONE TASK %i TIMES" % check
        return check > 0
    else:
        return False

# FUNCTION TO CHECK HOW MANY TASKS PER TRIAL
def get_trial_count(task, trial_, gen_):

    if task == 'find':
        # query = "SELECT COUNT(*) FROM find WHERE hit_id = %(hitId_)s;"
        query = "SELECT COUNT(*) FROM find WHERE trial = %(trial_)s AND gen = %(gen_)s;"
    elif task == 'verify':
        # query = "SELECT COUNT(*) FROM verify WHERE hit_id = %(hitId_)s;"
        query = "SELECT COUNT(*) FROM verify WHERE trial = %(trial_)s AND gen = %(gen_)s;"
    elif task == 'rank':
        # query = "SELECT COUNT(*) FROM rank WHERE hit_id = %(hitId_)s;"
        query = "SELECT COUNT(*) FROM rank WHERE trial = %(trial_)s AND gen = %(gen_)s;"

    cursor.execute(query, {'trial_':trial_, 'gen_':gen_})
    conn.commit()
    count = cursor.fetchone()[0]
    print "---TASK PERFORMED %i TIMES" % count
    return count

def post_HIT(task, trial):
    amount = 0.10
    # Start the verify task
    url = "https://cs279-final-project.herokuapp.com/%s?trial=%s" % (task, trial)
    questionform = ExternalQuestion(url, 1200)
    create_hit_result = connection.create_hit(
        title="Help locate things in Google Street View — one question only!",
        description="Participate in a short study to find things in Google Street View",
        keywords=["find", "locate", "quick"],
        #duration is in seconds
        duration = 60*5,
        #max_assignments will set the amount of independent copies of the task (turkers can only see one)
        max_assignments=TASK_LIMIT,
        question=questionform,
        reward=Price(amount),
         #Determines information returned by method in API, not super important
        response_groups=('Minimal', 'HITDetail'),
        qualifications=Qualifications(),
        )

    # The response included several fields that will be helpful later
    hit_type_id = create_hit_result[0].HITTypeId
    hit_id = create_hit_result[0].HITId
    print "Your HIT has been created. You can see it at this link:"
    print "https://workersandbox.mturk.com/mturk/preview?groupId={}".format(hit_type_id)
    print "Your HIT ID is: {}".format(hit_id)
    return

# HELPER FUNCTION TO CONVERT GSV ZOOM TO FOV
def zoom_to_FOV(zoom):
    # Note that we increase zoom by 1
    return math.atan(2**(1 - (zoom+1))) * 360 / math.pi
'''

def checkMT(args):
    if  "assignmentId" in args:
        return True
    else:
        return False

def needConsent(args):
    if args.get("assignmentId") == "ASSIGNMENT_ID_NOT_AVAILABLE":
        print "CONSENT"
        return True
    else:
        return False

if __name__ == "__main__":
    # app.debug = DEBUG
    app.run(threaded=True)
