"""
*********************
*********************
*********************
This code has not been tested with a BublCam.
The BublOscClient.js client is the only documentation I can find for the 
custom commands.
*********************
*********************
*********************
"""

"""
Extensions to the Open Spherical Camera API specific to the Bubl Cam.
Documentation / Examples here:
https://bubltechnology.github.io/ScarletTests/
https://github.com/BublTechnology/osc-client/blob/master/lib/BublOscClient.js

Open Spherical Camera API proposed here:
https://developers.google.com/streetview/open-spherical-camera/reference

The library is an evolution of:
https://github.com/codetricity/theta-s-api-tests/blob/master/thetapylib.py

Usage:
At the top of your Python script, use

  from osc.bubl import Bublcam

After you import the library, you can use the commands like this:

  bublcam = Bublcam()
  bublcam.state()
  bublcam.info()

  # Capture image
  response = bublcam.takePicture()

  # Wait for the stitching to finish
  bublcam.waitForProcessing(response['id'])

  # Copy image to computer
  bublcam.getLatestImage()

  # Capture video
  response = bublcam.captureVideo()
  bublcam.stop(response['id'])

  # Get the port and end point for live streaming
  (bublStreamPort, bublStreamEndPoint) = bublcam.stream()

  # For rtsp video streaming, open the following URI
  # rtsp streaming not implemented here.
  rtspUri = "rtsp://%s:%s/%s" % (bubl._ip, bublStreamPort, bublStreamEndPoint)

  # Turn the camera off in 30 seconds
  bublcam.shutdown(30)
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

__all__ = ['Bublcam']

#
# Bubl cam
#
class Bublcam(osc.OpenSphericalCamera):

    def __init__(self, ip_base="192.168.0.100", httpPort=80):
        osc.OpenSphericalCamera.__init__(self, ip_base, httpPort)

    def updateFirmware(self, firmwareFilename):
        """
        _bublUpdate

        Update the camera firmware

        Reference:
        https://github.com/BublTechnology/osc-client/blob/master/lib/BublOscClient.js#L25
        """
        url = self._request("_bublUpdate")
        with open(firmwareFilename, 'rb') as handle:
            body = handle.read()

        try:
            req = requests.post(url, data=body, 
                headers={'Content-Type': 'application/octet-stream'})
        except Exception, e:
            self._httpError(e)
            return None

        if req.status_code == 200:
            response = req.json()
        else:
            self._oscError(req)
            response = None
        return response

    def bublGetImage(self, fileUri):
        """
        _bublGetImage

        Transfer the file from the camera to computer and save the
        binary data to local storage.  This works, but is clunky.
        There are easier ways to do this.

        Not currently applying the equivalent of Javascript's encodeURIComponent
        to the fileUri

        Reference:
        https://github.com/BublTechnology/osc-client/blob/master/lib/BublOscClient.js#L31
        """
        acquired = False
        if fileUri:
            url = self._request("_bublGetImage/%s" % fileUri)
            fileName = fileUri.split("/")[1]

            try:
                response = requests.get(url, stream=True)
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

    def stop(self, commandId):
        """
        _bublStop

        Reference:
        https://github.com/BublTechnology/osc-client/blob/master/lib/BublOscClient.js#L37
        """
        url = self._request("commands/_bublStop")
        body = json.dumps({
                "id": commandId
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

    def poll(self, commandId, fingerprint, waitTimeout):
        """
        _bublPoll

        Reference:
        https://github.com/BublTechnology/osc-client/blob/master/lib/BublOscClient.js#L43
        """
        url = self._request("commands/_bublPoll")
        body = json.dumps({
                "id": commandId,
                "fingerprint" : fingerprint,
                "waitTimeout" : waitTimeout
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

    def captureVideo(self):
        """
        _bublCaptureVideo

        Reference:
        https://github.com/BublTechnology/osc-client/blob/master/lib/BublOscClient.js#L49
        """
        url = self._request("commands/execute")
        body = json.dumps({"name": "camera._bublCaptureVideo",
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

    def shutdown(self, shutdownDelay):
        """
        _bublShutdown

        Reference:
        https://github.com/BublTechnology/osc-client/blob/master/lib/BublOscClient.js#L64
        """
        url = self._request("commands/execute")
        body = json.dumps({"name": "camera._bublShutdown",
             "parameters": {
                "sessionId": self.sid,
                "shutdownDelay" : shutdownDelay
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

    def stream(self):
        """
        _bublStream

        Return the port and end point to use for rtsp video streaming

        Reference:
        https://github.com/BublTechnology/osc-client/blob/master/lib/BublOscClient.js#L59
        """
        acquired = False

        url = self._request("commands/execute")
        body = json.dumps({"name": "camera._bublStream",
                "parameters": {
                    "sessionId": self.sid
                 }})

        try:
            response = requests.post(url, data=body, stream=True)
        except Exception, e:
            self._httpError(e)
            return acquired

        if response.status_code == 200:
            response = req.json()
            bublStreamPort = response['_bublStreamPort']
            bublStreamEndPoint = response['_bublStreamEndPoint']
        else:
            bublStreamPort = None
            bublStreamEndPoint = None
            self._oscError(response)

        return (bublStreamPort, bublStreamEndPoint)
# Bublcam



