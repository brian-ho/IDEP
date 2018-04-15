"""
An implementation of the Open Spherical Camera API proposed here:
https://developers.google.com/streetview/open-spherical-camera/reference

There is minimal error checking, and likely a few places where the expected
workflow isn't adhered to but this should get you started if you're using
Python and a camera that supports the Open Spherical Camera API.

Usage:
At the top of your Python script, use

  from osc.osc import *

After you import the library, you can use the commands like this:

  # Initializing the class starts a session
  camera = OpenSphericalCamera()
  camera.state()
  camera.info()

  # Only need to call this if there was a problem
  # when 'camera' was created
  camera.startSession()

  # Capture image
  response = camera.takePicture()

  # Wait for the stitching to finish
  camera.waitForProcessing(response['id'])

  # Copy image to computer
  camera.getLatestImage()

  camera.closeSession()
"""

import json
import requests
import time

__author__ = 'Haarm-Pieter Duiker'
__copyright__ = 'Copyright (C) 2016 - Duiker Research Corp'
__license__ = ''
__maintainer__ = 'Haarm-Pieter Duiker'
__email__ = 'support@duikerresearch.org'
__status__ = 'Production'

__major_version__ = '1'
__minor_version__ = '0'
__change_version__ = '0'
__version__ = '.'.join((__major_version__,
                        __minor_version__,
                        __change_version__))

__all__ = ['g_oscOptions',
           'shutterSpeedNames',
           'shutterSpeeds',
           'exposurePrograms',
           'whiteBalance',
           'OpenSphericalCamera']

#
# Options
#
'''
Reference:
https://developers.google.com/streetview/open-spherical-camera/reference/options
'''
g_oscOptions = [ 
            # Read-only values
            "remainingPictures",
            "remainingSpace",
            "totalSpace",

            # Reference options
            "gpsInfo",
            "dateTimeZone",

            "aperture",
            "apertureSupport",
            "captureMode",
            "captureModeSupport",
            "exposureCompensation",
            "exposureCompensationSupport",
            "exposureProgram",
            "exposureProgramSupport",
            "fileFormat",
            "fileFormatSupport",
            "iso",
            "isoSupport",
            "offDelay",
            "offDelaySupport",
            "shutterSpeed",
            "shutterSpeedSupport",
            "sleepDelay",
            "sleepDelaySupport",
            "whiteBalance",
            "whiteBalanceSupport",

            "exposureDelay",
            "exposureDelaySupport",
            "hdr",
            "hdrSupport",
            "exposureBracket",
            "exposureBracketSupport",
            "gyro",
            "gyroSupport",
            "imageStabilization",
            "imageStabilizationSupport",
            "wifiPassword"
            ]

#
# Known options values
#
shutterSpeedNames = {
    0.00015625 : "1/6400", 
    0.0002 : "1/5000", 
    0.00025 : "1/4000",
    0.0003125 : "1/3200", 
    0.0004 : "1/2500", 
    0.0005 : "1/2000",
    0.000625 : "1/1600", 
    0.0008 : "1/1250", 
    0.001 : "1/1000",
    0.00125 : "1/800", 
    0.0015625 : "1/640", 
    0.002 : "1/500",
    0.0025 : "1/400", 
    0.003125 : "1/320", 
    0.004 : "1/250",
    0.005 : "1/200", 
    0.00625 : "1/160", 
    0.008 : "1/125",
    0.01 : "1/100", 
    0.0125 : "1/80", 
    0.01666666 : "1/60",
    0.02 : "1/50", 
    0.025 : "1/40", 
    0.03333333 : "1/30",
    0.04 : "1/25", 
    0.05 : "1/20", 
    0.06666666 : "1/15",
    0.07692307 : "1/13", 
    0.1 : "1/10", 
    0.125 : "1/8",
    0.16666666 : "1/6", 
    0.2 : "1/5", 
    0.25 : "1/4",
    0.33333333 : "1/3", 
    0.4 : "1/2.5", 
    0.5 : "1/2",
    0.625 : "1/1.6", 
    0.76923076 : "1/1.3", 
    1 : "1",
    1.3 : "1.3", 
    1.6 : "1.6", 
    2 : "2", 
    2.5 : "2.5", 
    3.2 : "3.2", 
    4 : "4", 
    5 : "5",
    6 : "6", 
    8 : "8", 
    10 : "10", 
    13 : "13", 
    15 : "15", 
    20 : "20", 
    25 : "25", 
    30 : "30", 
    60 : "60"
}

shutterSpeeds = [
    0.00015625, 
    0.0002, 
    0.00025,
    0.0003125, 
    0.0004, 
    0.0005,
    0.000625, 
    0.0008, 
    0.001,
    0.00125, 
    0.0015625, 
    0.002,
    0.0025, 
    0.003125, 
    0.004,
    0.005, 
    0.00625, 
    0.008,
    0.01, 
    0.0125, 
    0.01666666,
    0.02, 
    0.025, 
    0.03333333,
    0.04, 
    0.05, 
    0.06666666,
    0.07692307, 
    0.1, 
    0.125,
    0.16666666, 
    0.2, 
    0.25,
    0.33333333, 
    0.4, 
    0.5,
    0.625, 
    0.76923076, 
    1,
    1.3, 
    1.6, 
    2, 
    2.5, 
    3.2, 
    4, 
    5,
    6, 
    8, 
    10, 
    13, 
    15, 
    20, 
    25, 
    30, 
    60
]

exposurePrograms = {
    "manual" : 1,
    "automatic" : 2,
    "shutter priority" : 4,
    "iso priority" : 9
}

whiteBalance = {
    "Auto" : "auto",
    "Outdoor" : "daylight",
    "Shade" : "shade",
    "Cloudy" : "cloudy-daylight",
    "Incandescent light 1" : "incandescent",
    "Incandescent light 2" : "_warmWhiteFluorescent",
    "Fluorescent light 1 (daylight)" : "_dayLightFluorescent",
    "Fluorescent light 2 (natural white)" : "_dayWhiteFluorescent",
    "Fluorescent light 3 (white)" : "fluorescent",
    "Fluorescent light 4 (light bulb color)" : "_bulbFluorescent"
}

#
# Error codes
#

'''
Reference:
https://developers.google.com/streetview/open-spherical-camera/guides/osc/error-handling
https://developers.theta360.com/en/docs/v2/api_reference/protocols/errors.html

Error code - HTTP Status code - Description
unknownCommand          - 400 - Invalid command is issued
missingParameter        - 400 - Insufficient required parameters to issue the command
invalidParameterName    - 400 - Parameter name or option name is invalid
invalidParameterValue   - 400 - Parameter value when command was issued is invalid
cameraInExclusiveUse    - 400 - Session start not possible when camera is in exclusive use

disabledCommand         - 403 - Command cannot be executed due to the camera status
invalidSessionId        - 403 - sessionID when command was issued is invalid
corruptedFile           - 403 - Process request for corrupted file
powerOffSequenceRunning - 403 - Process request when power supply is off
invalidFileFormat       - 403 - Invalid file format specified

serviceUnavailable      - 503 - Processing requests cannot be received temporarily
unexpected              - 503 - Other errors
'''

#
# Generic OpenSphericalCamera
#
class OpenSphericalCamera:
    # Class variables / methods
    oscOptions = g_oscOptions

    # Instance variables / methods
    def __init__(self, ip_base="192.168.1.1", httpPort=80):
        self.sid = None
        self.fingerprint = None
        self._api = None

        self._ip = ip_base
        self._httpPort = httpPort
        self._httpUpdatesPort = httpPort

        # Try to start a session
        self.startSession()

        # Use 'info' command to retrieve more information
        self._info = self.info()
        if self._info:
            self._api = self._info['api']
            self._httpPort = self._info['endpoints']['httpPort']
            self._httpUpdatesPort = self._info['endpoints']['httpUpdatesPort']

    def __del__(self):
        if self.sid:
            self.closeSession()

    def _request(self, url_request, update=False):
        """
        Generate the URI to send to the Open Spherical Camera.
        All calls start with /osc/
        """
        osc_request = unicode("/osc/" + url_request)

        url_base = "http://%s:%s" % (self._ip, self._httpPort if not update else self._httpUpdatesPort)

        if self._api:
            if osc_request in self._api:
                url = url_base + osc_request
            else:
                print( "OSC Error - Unsupported API  : %s" % osc_request )
                print( "OSC Error - Supported API is : %s" % self._api )
                url = None
        else:
                url = url_base + osc_request

        return url

    def _httpError(self, exception):
        print( "HTTP Error - begin" )
        print( repr(exception) )
        print( "HTTP Error - end" )

    def _oscError(self, request):
        status = request.status_code

        try:
            error = request.json()

            print( "OSC Error - HTTP Status : %s" % status)
            if 'error' in error:
                print( "OSC Error - Code        : %s" % error['error']['code'])
                print( "OSC Error - Message     : %s" % error['error']['message'])
            print( "OSC Error - Name        : %s" % error['name'])
            print( "OSC Error - State       : %s" % error['state'])
        except:
            print( "OSC Error - HTTP Status : %s" % status)

        return status

    def getOptionNames(self):
        return self.oscOptions

    def info(self):
        """
        Get basic information on the camera.  Note that this is a GET call
        and not a POST.  Most of the calls are POST.

        Reference:
        https://developers.google.com/streetview/open-spherical-camera/guides/osc/info
        """
        url = self._request("info")
        try:
            req = requests.get(url)
        except Exception, e:
            self._httpError(e)
            return None

        if req.status_code == 200:
            response = req.json()
        else:
            self._oscError(req)
            response = None
        return response

    def state(self):
        """
        Get the state of the camera, which will include the sessionsId and also the
        latestFileUri if you've just taken a picture.

        Reference:
        https://developers.google.com/streetview/open-spherical-camera/guides/osc/state
        """
        url = self._request("state")
        try:
            req = requests.post(url)
        except Exception, e:
            self._httpError(e)
            return None

        if req.status_code == 200:
            response = req.json()
            self.fingerprint = response['fingerprint']
            state = response['state']
        else:
            self._oscError(req)
            state = None
        return state

    def status(self, command_id):
        """
        Returns the status for previous inProgress commands.

        Reference:
        https://developers.google.com/streetview/open-spherical-camera/guides/osc/commands/status
        """
        url = self._request("commands/status")
        body = json.dumps({"id": command_id})
        try:
            req = requests.post(url, data=body)
        except Exception, e:
            self._httpError(e)
            return None

        if req.status_code == 200:
            response = req.json()
            state = response['state']
        else:
            self._oscError(req)
            state = None
        return state

    def checkForUpdates(self):
        """
        Check for updates on the camera, using the current state fingerprint.

        Reference:
        https://developers.google.com/streetview/open-spherical-camera/guides/osc/checkforupdates
        """
        if self.fingerprint is None:
            self.state()

        url = self._request("checkForUpdates")
        body = json.dumps({"stateFingerprint": self.fingerprint})
        try:
            req = requests.post(url, data=body)
        except Exception, e:
            self._httpError(e)
            return False

        if req.status_code == 200:
            response = req.json()
            newFingerprint = response['stateFingerprint']
            if newFingerprint != self.fingerprint:
                print( "Update - new, old fingerprint : %s, %s" % (newFingerprint, self.fingerprint) )
                self.fingerprint = newFingerprint
                response = True
            else:
                print( "No update - fingerprint : %s" % self.fingerprint )
                response = False
        else:
            self._oscError(req)
            response = False
        return response

    def waitForProcessing(self, command_id, maxWait=20):
        """
        Helper function that will poll the camera until the status to changes 
        to 'done' or the timeout is hit.

        Reference:
        https://developers.google.com/streetview/open-spherical-camera/guides/osc/commands/status
        """

        print( "Waiting for processing")
        for i in range(maxWait):
            status = self.status(command_id)
            if status == "done":
                print( "Image processing finished" )
                break
            elif not status or "error" in status:
                print( "Status failed. Stopping wait." )
                break
            print( "%d - %s" % (i, status) )
            time.sleep( 1 )

        return

    def startSession(self):
        """
        Start a new session.  Grab the sessionId number and return it.
        You'll need the sessionId to take a video or image.

        Reference:
        https://developers.google.com/streetview/open-spherical-camera/reference/camera/startsession
        """
        url = self._request("commands/execute")
        body = json.dumps({"name": "camera.startSession",
             "parameters": {}
             })
        try:
            req = requests.post(url, data=body)
        except Exception, e:
            self._httpError(e)
            self.sid = None
            return self.sid

        if req.status_code == 200:
            response = req.json()
            self.sid = (response["results"]["sessionId"])
        else:
            self._oscError(req)
            self.sid = None
        return self.sid

    def updateSession(self):
        """
        Update a session, using the sessionId.

        Reference:
        https://developers.google.com/streetview/open-spherical-camera/reference/camera/updatesession
        """
        url = self._request("commands/execute")
        body = json.dumps({"name": "camera.updateSession",
             "parameters": { "sessionId":self.sid }
             })
        try:
            req = requests.post(url, data=body)
        except Exception, e:
            self._httpError(e)
            return None

        response = None
        if req.status_code == 200:
            response = req.json()
        else:
            self._oscError(req)
            response = None

        return response

    def closeSession(self):
        """
        Close a session.

        Reference:
        https://developers.google.com/streetview/open-spherical-camera/reference/camera/closesession
        """
        url = self._request("commands/execute")
        body = json.dumps({"name": "camera.closeSession",
             "parameters": { "sessionId":self.sid }
             })
        try:
            req = requests.post(url, data=body)
        except Exception, e:
            self._httpError(e)
            return None

        if req.status_code == 200:
            response = req.json()
            self.sid = None
        else:
            self._oscError(req)
            response = None

        return response

    def takePicture(self):
        """
        Take a still image.  The sessionId is either taken from
        startSession or from state.  You can change the mode
        from video to image with captureMode in the options.

        Reference:
        https://developers.google.com/streetview/open-spherical-camera/reference/camera/takepicture
        """
        if self.sid == None:
            response = None
            return response
        url = self._request("commands/execute")
        body = json.dumps({"name": "camera.takePicture",
             "parameters": {
                "sessionId": self.sid
             }
             })
        try:
            req = requests.post(url, data=body)
        except Exception, e:
            self._httpError(e)
            return None

        if req.status_code == 200:
            response = req.json()
        else:
            self._oscError(req)
            response = None
        return response

    def listImages(self, entryCount = 3, maxSize = None, 
        continuationToken = None, includeThumb = True ):
        """
        entryCount:
                Integer No. of still images and video files to be acquired
        maxSize:
                Integer (Optional) Maximum size of thumbnail images; 
                max(thumbnail_width, thumbnail_height).
        continuationToken
                String (Optional) An opaque continuation token of type string, 
                returned by previous listImages call, used to retrieve next 
                images. Omit this parameter for the first listImages
        includeThumb:
                Boolean (Optional) Defaults to true. Use false to omit 
                thumbnail images from the result.

        Reference:
        https://developers.google.com/streetview/open-spherical-camera/reference/camera/listimages
        """
        parameters = {
                "entryCount": entryCount,
                "includeThumb": includeThumb,
             }
        if maxSize is not None:
            parameters['maxSize'] = maxSize
        if continuationToken is not None:
            parameters['continuationToken'] = continuationToken

        url = self._request("commands/execute")
        body = json.dumps({"name": "camera.listImages",
             "parameters": parameters
             })
        try:
            req = requests.post(url, data=body)
        except Exception, e:
            self._httpError(e)
            return None

        if req.status_code == 200:
            response = req.json()
        else:
            self._oscError(req)
            response = None
        return response

    def delete(self, fileUri):
        """
        Delete the image with the named fileUri

        Reference:
        https://developers.google.com/streetview/open-spherical-camera/reference/camera/delete
        """
        url = self._request("commands/execute")
        body = json.dumps({"name": "camera.delete",
             "parameters": {
                "fileUri": fileUri
             }
             })
        try:
            req = requests.post(url, data=body)
        except Exception, e:
            self._httpError(e)
            return None

        if req.status_code == 200:
            response = req.json()
        else:
            self._oscError(req)
            response = None
        return response

    def getImage(self, fileUri, imageType="image"):
        """
        Transfer the file from the camera to computer and save the
        binary data to local storage.  This works, but is clunky.
        There are easier ways to do this. The __type parameter
        can be set to "thumb" for a thumbnail or "image" for the
        full-size image.  The default is "image".

        Reference:
        https://developers.google.com/streetview/open-spherical-camera/reference/camera/getimage
        """
        url = self._request("commands/execute")
        body = json.dumps({"name": "camera.getImage",
             "parameters": {
                "fileUri": fileUri,
                "_type": imageType
             }
             })
        fileName = fileUri.split("/")[1]
        print( "Writing image : %s" % fileName )

        acquired = False
        try:
            response = requests.post(url, data=body, stream=True)
        except Exception, e:
            self._httpError(e)
            return acquired

        if response.status_code == 200:
            with open(fileName, 'wb') as handle:
                for block in response.iter_content(1024):
                    handle.write(block)
            acquired = True
        else:
            self._oscError(response)

        return acquired

    def getMetadata(self, fileUri):
        """
        Get the exif and xmp metadata associated with the named fileUri

        Reference:
        https://developers.google.com/streetview/open-spherical-camera/reference/camera/getmetadata
        """
        url = self._request("commands/execute")
        body = json.dumps({"name": "camera.getMetadata",
             "parameters": {
                "fileUri": fileUri
             }
             })
        try:
            req = requests.post(url, data=body)
        except Exception, e:
            self._httpError(e)
            return None

        if req.status_code == 200:
            response = req.json()
        else:
            self._oscError(req)
            response = None

        return response

    def setOption(self, option, value):
        """
        Set an option to a value. The validity of the option is checked. The
        validity of the value is not.  

        Reference:
        https://developers.google.com/streetview/open-spherical-camera/reference/camera/setoptions
        https://developers.theta360.com/en/docs/v2/api_reference/commands/camera.set_options.html
        """
        if self.sid == None or option not in self.getOptionNames():
            response = None
            return response

        print( "setOption - %s : %s" % (option, value) )

        url = self._request("commands/execute")
        body = json.dumps({"name": "camera.setOptions",
             "parameters": {
                "sessionId": self.sid,
                "options": {
                        option: value,
                        }
             }
             })
        try:
            req = requests.post(url, data=body)
        except Exception, e:
            self._httpError(e)
            return None

        if req.status_code == 200:
            response = req.json()
            #print( "setOption suceeeded - %s " % response )
        else:
            self._oscError(req)
            response = None

        return response

    def getOption(self, option):
        """
        Get an option value. The validity of the option is not checked.

        Reference:
        https://developers.google.com/streetview/open-spherical-camera/reference/camera/getoptions
        https://developers.theta360.com/en/docs/v2/api_reference/commands/camera.get_options.html
        """
        url = self._request("commands/execute")
        body = json.dumps({"name": "camera.getOptions",
             "parameters": {
                "sessionId": self.sid,
                "optionNames": [
                        option]
             }
             })
        try:
            req = requests.post(url, data=body)
        except Exception, e:
            self._httpError(e)
            return None

        if req.status_code == 200:
            response = req.json()
            value = response["results"]["options"][option]
        else:
            self._oscError(req)
            value = None
        return value

    def getSid(self):
        """
        Helper function that will refresh the cache of the sessionsId and 
        return it's value
        """
        url = self._request("state")
        try:
            req = requests.post(url)
        except Exception, e:
            self._httpError(e)
            self.sid = None
            return None

        if req.status_code == 200:
            response = req.json()
            self.sid = response["state"]["sessionId"]
        else:
            self._oscError(req)
            self.sid = None
        return self.sid

    # Extensions
    def getAllOptions(self):
        """
        Helper function that will get the value for all options.
        """
        url = self._request("commands/execute")
        body = json.dumps({"name": "camera.getOptions",
                 "parameters": {
                    "sessionId": self.sid,
                    "optionNames": self.getOptionNames()
                 }
             })
        try:
            req = requests.post(url, data=body)
        except Exception, e:
            self._httpError(e)
            return None

        if req.status_code == 200:
            response = req.json()
            returnOptions = response["results"]["options"]
        else:
            self._oscError(req)
            returnOptions = None
        return returnOptions

    def latestFileUri(self):
        """
        Get the name of the last captured image or video from the state
        """
        try:
            state_data = self.state()
        except:
            return None
        if state_data:
            latestFileUri = state_data["_latestFileUri"]
        else:
            latestFileUri = None
        return latestFileUri

    def getLatestImage(self, imageType="image"):
        """
        Transfer the latest file from the camera to computer and save the
        binary data to local storage.  The __type parameter
        can be set to "thumb" for a thumbnail or "image" for the
        full-size image.  The default is "image".
        """
        fileUri = self.latestFileUri()
        if fileUri:
            self.getImage(fileUri, imageType)

    def getLatestImageMetadata(self):
        """
        Get the metadata for the last image
        """
        fileUri = self.latestFileUri()
        if fileUri:
            metadata = self.getImageMetadata(fileUri)
        else:
            metadata = None
        return metadata

# OpenSphericalCamera

