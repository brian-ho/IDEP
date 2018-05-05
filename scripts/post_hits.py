# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, url_for, request, make_response
from boto.mturk.connection import MTurkConnection
from boto.mturk.question import ExternalQuestion
from boto.mturk.qualification import Qualifications, PercentAssignmentsApprovedRequirement, NumberHitsApprovedRequirement
from boto.mturk.price import Price
import sys
import pandas as pd

task = sys.argv[1]

#Start Configuration Variables
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

#This allows us to specify whether we are pushing to the sandbox or live site.
if len(sys.argv) > 2 and sys.argv[2] == 'pub':
    AMAZON_HOST = "mechanicalturk.amazonaws.com"
else:
    AMAZON_HOST = "mechanicalturk.sandbox.amazonaws.com"

connection = MTurkConnection(aws_access_key_id=AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                             host=AMAZON_HOST)

#5 cents per HIT
if task == 'guess':
    title = 'Help locate street images of Boston! You can take multiple times. IDEP'
    amount = 0.05
elif task == 'label':
    title = 'Help label street images of Boston! You can take multiple times. IDEP'
    amount = 0.05
elif task == 'share':
    title = 'Help share your memories of Boston! You can take multiple times. IDEP'
    amount = 0.01
else:
    title = 'Help make a city image for Boston! You can take multiple times. IDEP'
    amount = 0.01

totalHITS = 50
urls = []
hitIDs = []
#frame_height in pixels
frame_height = 1200
#Here, I create two sample qualifications
qualifications = Qualifications()
# qualifications.add(PercentAssignmentsApprovedRequirement(comparator="GreaterThan", integer_value="90"))
# qualifications.add(NumberHitsApprovedRequirement(comparator="GreaterThan", integer_value="100"))

#This url will be the url of your application, with appropriate GET parameters
url = "https://new-city-image.herokuapp.com/%s" % (task)
questionform = ExternalQuestion(url, frame_height)

for HIT in range(totalHITS):
    create_hit_result = connection.create_hit(
        title=title,
        description="Participate in a short survey about perception of images of cities!",
        keywords=["city", "perception", "quick"],
        #duration is in seconds
        duration = 60*5,
        #max_assignments will set the amount of independent copies of the task (turkers can only see one)
        max_assignments=10,
        question=questionform,
        reward=Price(amount=amount),
         #Determines information returned by method in API, not super important
        response_groups=('Minimal', 'HITDetail'),
        qualifications=qualifications,
        )

    # The response included several fields that will be helpful later
    hit_type_id = create_hit_result[0].HITTypeId
    hit_id = create_hit_result[0].HITId

    if len(sys.argv) > 2 and sys.argv[2] == 'pub':
        url_preview = "https://www.mturk.com/mturk/preview?groupId={}".format(hit_type_id)
    else:
        url_preview = "https://workersandbox.mturk.com/mturk/preview?groupId={}".format(hit_type_id)

    print "ID is: {} - ".format(hit_id), url_preview
    urls.append(url_preview)
    hitIDs.append(hit_id)

df = pd.DataFrame({'hitID':hitIDs, 'hitURL':urls})
df.to_csv('logs/HITs.csv')
