# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, url_for, request, make_response
from boto.mturk.connection import MTurkConnection
from boto.mturk.question import ExternalQuestion
from boto.mturk.qualification import Qualifications, PercentAssignmentsApprovedRequirement, NumberHitsApprovedRequirement
from boto.mturk.price import Price
import sys

task = sys.argv[1]
trial = sys.argv[2]

#Start Configuration Variables
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

#This allows us to specify whether we are pushing to the sandbox or live site.
if len(sys.argv) > 3 and sys.argv[3] == 'pub':
    AMAZON_HOST = "mechanicalturk.amazonaws.com"
else:
    AMAZON_HOST = "mechanicalturk.sandbox.amazonaws.com"

connection = MTurkConnection(aws_access_key_id=AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                             host=AMAZON_HOST)

#5 cents per HIT
if task == 'find':
    amount = 0.15
elif task == 'verify':
    amount = 0.10
elif task == 'rank':
    amount = 0.10
else:
    amount = 0.05

#frame_height in pixels
frame_height = 1200
#Here, I create two sample qualifications
qualifications = Qualifications()
# qualifications.add(PercentAssignmentsApprovedRequirement(comparator="GreaterThan", integer_value="90"))
# qualifications.add(NumberHitsApprovedRequirement(comparator="GreaterThan", integer_value="100"))

#This url will be the url of your application, with appropriate GET parameters
url = "https://cs279-final-project.herokuapp.com/%s?trial=%s" % (task, trial)
questionform = ExternalQuestion(url, frame_height)
create_hit_result = connection.create_hit(
    title="Help locate things in Google Street View — one question only!",
    description="Participate in a short study to find things in Google Street View",
    keywords=["find", "locate", "quick"],
    #duration is in seconds
    duration = 60*10,
    #max_assignments will set the amount of independent copies of the task (turkers can only see one)
    max_assignments=5,
    question=questionform,
    reward=Price(amount=amount),
     #Determines information returned by method in API, not super important
    response_groups=('Minimal', 'HITDetail'),
    qualifications=qualifications,
    )

# The response included several fields that will be helpful later
hit_type_id = create_hit_result[0].HITTypeId
hit_id = create_hit_result[0].HITId
print "Your HIT has been created. You can see it at this link:"
if len(sys.argv) > 3 and sys.argv[3] == 'pub':
    print "https://www.mturk.com/mturk/preview?groupId={}".format(hit_type_id)
else:
    print "https://workersandbox.mturk.com/mturk/preview?groupId={}".format(hit_type_id)
print "Your HIT ID is: {}".format(hit_id)
