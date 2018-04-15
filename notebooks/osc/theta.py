"""
Extensions to the Open Spherical Camera API specific to the Ricoh Theta S.
Documentation here:
https://developers.theta360.com/en/docs/v2/api_reference/

Open Spherical Camera API proposed here:
https://developers.google.com/streetview/open-spherical-camera/reference

The library is an evolution of:
https://github.com/codetricity/theta-s-api-tests/blob/master/thetapylib.py

Usage:
At the top of your Python script, use

  from osc.theta import RicohThetaS

After you import the library, you can use the commands like this:

  thetas = RicohThetaS()
  thetas.state()
  thetas.info()

  # Capture image
  thetas.setCaptureMode( 'image' )
  response = thetas.takePicture()

  # Wait for the stitching to finish
  thetas.waitForProcessing(response['id'])

  # Copy image to computer
  thetas.getLatestImage()

  # Stream the livePreview video to disk
  # for 3 seconds
  thetas.getLivePreview(timeLimitSeconds=3)

  # Capture video
  thetas.setCaptureMode( '_video' )
  thetas.startCapture()
  thetas.stopCapture()

  # Copy video to computer
  thetas.getLatestVideo()

  thetas.closeSession()
"""

import json
import requests
import timeit

import osc

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

__all__ = ['g_ricohOptions',
           'ricohFileFormats',
           'RicohThetaS']

#
# Ricoh Theta S
#

#
# Ricoh-specific options
#

'''
Reference:
https://developers.theta360.com/en/docs/v2/api_reference/options/
'''

g_ricohOptions = [
            # Custom read-only options
            "_wlanChannel",            
            "_remainingVideos",

            # Custom options
            "_captureInterval",
            "_captureIntervalSupport",
            "_captureNumber",
            "_captureNumberSupport",
            "_filter",
            "_filterSupport",
            "_HDMIreso",
            "_HDMIresoSupport",
            "_shutterVolume",
            "_shutterVolumeSupport"
            ]

ricohFileFormats = {
    "image_5k" : {'width': 5376, 'type': 'jpeg', 'height': 2688},
    "image_2k" : {'width': 2048, 'type': 'jpeg', 'height': 1024},
    "video_HD_1080" : {"type": "mp4", "width": 1920, "height": 1080},
    "video_HD_720" : {"type": "mp4", "width": 1280, "height": 720}
}

class RicohThetaS(osc.OpenSphericalCamera):
    # Class variables / methods
    ricohOptions = g_ricohOptions

    def __init__(self, ip_base="192.168.1.1", httpPort=80):
        osc.OpenSphericalCamera.__init__(self, ip_base, httpPort)

    def getOptionNames(self):
        return self.oscOptions + self.ricohOptions

    # 'image', '_video'
    def setCaptureMode(self, mode):
        return self.setOption("captureMode", mode)

    def getCaptureMode(self):
        return self.getOption("captureMode")

    def listAll(self, entryCount = 3, detail = False, sortType = "newest", ):
        """
        entryCount:
                Integer No. of still images and video files to be acquired
        detail:
                Boolean (Optional)  Whether or not file details are acquired
                true is acquired by default. Only values that can be acquired
                when false is specified are "name", "uri", "size" and "dateTime"
        sort:
                String  (Optional) Specify the sort order
                newest (dateTime descending order)/ oldest (dateTime ascending order)
                Default is newest

        Reference:
        https://developers.theta360.com/en/docs/v2/api_reference/commands/camera._list_all.html
        """
        url = self._request("commands/execute")
        body = json.dumps({"name": "camera._listAll",
             "parameters": {
                "entryCount": entryCount,
                "detail": detail,
                "sort": sortType
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

    def finishWlan(self):
        """
        Turns the wireless LAN off.

        Reference:
        https://developers.theta360.com/en/docs/v2/api_reference/commands/camera._finish_wlan.html
        """
        url = self._request("commands/execute")
        body = json.dumps({"name": "camera._finishWlan",
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

    def startCapture(self):
        """
        Begin video capture if the captureMode is _video.  If the
        captureMode is set to image, the camera will take multiple
        still images.  The captureMode can be set in the options.
        Note that this will not work with streaming video using the
        HDMI or USB cable.

        Reference:
        https://developers.theta360.com/en/docs/v2/api_reference/commands/camera._start_capture.html
        """
        url = self._request("commands/execute")
        body = json.dumps({"name": "camera._startCapture",
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

    def stopCapture(self):
        """
        Stop video capture.  If in image mode, will stop
        automatic image taking.

        Reference:
        https://developers.theta360.com/en/docs/v2/api_reference/commands/camera._stop_capture.html
        """
        url = self._request("commands/execute")
        body = json.dumps({"name": "camera._stopCapture",
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

    def getVideo(self, fileUri, imageType="full"):
        """
        Transfer the video file from the camera to computer and save the
        binary data to local storage.  This works, but is clunky.
        There are easier ways to do this. The __type parameter
        can be set to "thumb" for a thumbnail or "full" for the
        full-size video.  The default is "full".

        Reference:
        https://developers.theta360.com/en/docs/v2/api_reference/commands/camera._get_video.html
        """
        acquired = False
        if fileUri:
            url = self._request("commands/execute")
            body = json.dumps({"name": "camera._getVideo",
                 "parameters": {
                    "fileUri": fileUri,
                    "type": imageType
                 }
                 })
            fileName = fileUri.split("/")[1]

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
                self._oscError(req)

        return acquired

    def getLatestVideo(self, imageType="full"):
        """
        Transfer the latest file from the camera to computer and save the
        binary data to local storage.  The __type parameter
        can be set to "thumb" for a thumbnail or "full" for the
        full-size video.  The default is "full".
        """
        fileUri = self.latestFileUri()
        if fileUri:
            self.getVideo(fileUri, imageType)

    def getLivePreview(self, fileNamePrefix = "livePreview", timeLimitSeconds=10):
        """
        Save the live preview video stream to disk as a series of jpegs. 
        The capture mode must be 'image'.

        Credit for jpeq decoding:
        https://stackoverflow.com/questions/21702477/how-to-parse-mjpeg-http-stream-from-ip-camera

        Reference:
        https://developers.theta360.com/en/docs/v2/api_reference/commands/camera._get_live_preview.html
        """
        acquired = False

        url = self._request("commands/execute")
        body = json.dumps({"name": "camera._getLivePreview",
                "parameters": {
                    "sessionId": self.sid
                 }})

        try:
            response = requests.post(url, data=body, stream=True)
        except Exception, e:
            self._httpError(e)
            return acquired

        if response.status_code == 200:
            bytes=''
            t0 = timeit.default_timer()
            i = 0
            for block in response.iter_content(16384):
                bytes += block

                # Search the current block of bytes for the jpq start and end
                a = bytes.find('\xff\xd8')
                b = bytes.find('\xff\xd9')

                # If you have a jpg, write it to disk
                if a !=- 1 and b != -1:
                    #print( "Writing frame %04d - Byte range : %d to %d" % (i, a, b) )
                    # Found a jpg, write to disk
                    frameFileName = "%s.%04d.jpg" % (fileNamePrefix, i)
                    with open(frameFileName, 'wb') as handle:
                        jpg = bytes[a:b+2]
                        handle.write(jpg)

                        # Reset the buffer to point to the next set of bytes
                        bytes = bytes[b+2:]
                        #print( "Wrote frame %04d - %2.2f seconds" % (i, elapsed) )

                    i += 1

                t1 = timeit.default_timer()
                elapsed = t1 - t0
                if elapsed > timeLimitSeconds:
                    #print( "Breaking" )
                    break

            acquired = True
        else:
            self._oscError(response)
# RicohThetaS



