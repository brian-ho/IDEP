# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, url_for, request, make_response
from boto.mturk.connection import MTurkConnection
from boto.mturk.question import ExternalQuestion
from boto.mturk.qualification import Qualifications, PercentAssignmentsApprovedRequirement, NumberHitsApprovedRequirement
from boto.mturk.price import Price
import pandas as pd
import sys

hit = sys.argv[1]

#Start Configuration Variables
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

if  hit == 'csv':
    csv_path = sys.argv[2]
    df = pd.read_csv(csv_path)

    if len(sys.argv) > 3 and sys.argv[3] == 'pub':
        AMAZON_HOST = "mechanicalturk.amazonaws.com"
    else:
        AMAZON_HOST = "mechanicalturk.sandbox.amazonaws.com"

    connection = MTurkConnection(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                 aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                 host=AMAZON_HOST)

    for i, hit in df.iterrows():
        connection.disable_hit(hit.hitID)
        print 'Disabling HIT: %s' % hit.hitID

else:
    if len(sys.argv) > 2 and sys.argv[2] == 'pub':
        AMAZON_HOST = "mechanicalturk.amazonaws.com"
    else:
        AMAZON_HOST = "mechanicalturk.sandbox.amazonaws.com"

    connection = MTurkConnection(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                 aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                 host=AMAZON_HOST)

    connection.disable_hit(hit)
    print 'Disabling HIT: %s' % hit
