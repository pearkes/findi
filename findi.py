# -*- coding: utf-8 -*-
import urllib
import urllib2
import datetime
import time
import base64

json_available = True
json = None
try:
    import simplejson as json
except ImportError:
    try:
        import json
    except ImportError:
        try:
            # Google Appengine offers simplejson via django
            from django.utils import simplejson as json
        except ImportError:
            json_available = False

class FindMyIPhone(object):
    partition = None

    def __init__(self, username, password, debug=False):
        if not json_available:
            raise Exception("json library required")

        self.devices = []
        self.debug = debug
        self.username = username
        self.password = password
        self.get_partition()
        self.update_devices()

    def get_partition(self):
        # TODO: log if debug
        body = json.dumps({
            "clientContext":{
                "appName":"FindMyiPhone",
                "appVersion":"1.4",
                "buildVersion":"145",
                "deviceUDID":"0000000000000000000000000000000000000000",
                "inactiveTime":2147483647,
                "osVersion":"4.2.1",
                "personID":0,
                "productType":"iPad1,1"
            }
        })
        headers, content = self.post('/fmipservice/device/%s/initClient' % self.username, body, None, True)
        self.partition = headers.get('X-Apple-MMe-Host')

    def locate(self, device_num=0, max_wait=300):
        start = int(time.time())

        while not self.devices[device_num].location_finished:
            # log
            if int(time.time()) - start > max_wait:
                raise Exception("Unable to find location within '%s' seconds" % max_wait)
            time.sleep(5)
            self.update_devices()

        device = self.devices[device_num]
        return {
            'latitude': device.latitude,
            'longitude': device.longitude,
            'accuracy': device.horizontal_accuracy,
            'timestamp': device.location_timestamp,
        }

    def send_message(self, msg, alarm=False, device_num=0, subject='Important Message'):
        device = self.devices[device_num]
        body = json.dumps({
            "clientContext":{
                "appName":"FindMyiPhone",
                "appVersion":"1.4",
                "buildVersion":"145",
                "deviceUDID":"0000000000000000000000000000000000000000",
                "inactiveTime":5911,
                "osVersion":"3.2",
                "productType":"iPad1,1",
                "selectedDevice":device.id,
                "shouldLocate":False
            },
            "device":device.id,
            "serverContext":{
                "callbackIntervalInMS":3000,
                "clientId":"0000000000000000000000000000000000000000",
                "deviceLoadStatus":"203",
                "hasDevices":True,
                "lastSessionExtensionTime":None,
                "maxDeviceLoadTime":60000,
                "maxLocatingTime":90000,
                "preferredLanguage":"en",
                "prefsUpdateTime":1276872996660,
                "sessionLifespan":900000,
                "timezone":{
                    "currentOffset":-25200000,
                    "previousOffset":-28800000,
                    "previousTransition":1268560799999,
                    "tzCurrentName":"Pacific Daylight Time",
                    "tzName":"America/Los_Angeles"
                },
                "validRegion":True
            },
            "sound":alarm,
            "subject":subject,
            "text":msg
        })

        # log 'Sending message...'
        self.post('/fmipservice/device/%s/sendMessage' % self.username, body)
        # log 'Message sent'

    def remote_lock(self, passcode, device_num=0):
        device = self.devices[device_num]
        body = json.dumps({
            "clientContext":{
                "appName":"FindMyiPhone",
                "appVersion":"1.4",
                "buildVersion":"145",
                "deviceUDID":"0000000000000000000000000000000000000000",
                "inactiveTime":5911,
                "osVersion":"3.2",
                "productType":"iPad1,1",
                "selectedDevice":device.id,
                "shouldLocate":False
            },
            "device":device.id,
            "oldPasscode":"",
            "passcode":passcode,
            "serverContext":{
                "callbackIntervalInMS":3000,
                "clientId":"0000000000000000000000000000000000000000",
                "deviceLoadStatus":"203",
                "hasDevices":True,
                "lastSessionExtensionTime":None,
                "maxDeviceLoadTime":60000,
                "maxLocatingTime":90000,
                "preferredLanguage":"en",
                "prefsUpdateTime":1276872996660,
                "sessionLifespan":900000,
                "timezone":{
                    "currentOffset":-25200000,
                    "previousOffset":-28800000,
                    "previousTransition":1268560799999,
                    "tzCurrentName":"Pacific Daylight Time",
                    "tzName":"America/Los_Angeles"
                },
                "validRegion":True
            }
        })
        # log 'Sending remote lock...'
        self.post('/fmipservice/device/%s/remoteLock' % self.username, body)
        # log 'Remote lock sent'

    def remote_wipe(self, device_num=0):
        device = self.devices[device_num]
        body = json.dumps({
            "clientContext":{
                "appName":"FindMyiPhone",
                "appVersion":"1.4",
                "buildVersion":"145",
                "deviceUDID":"0000000000000000000000000000000000000000",
                "inactiveTime":5911,
                "osVersion":"3.2",
                "productType":"iPad1,1",
                "selectedDevice":device.id,
                "shouldLocate":False
            },
            "device":device.id,
            "serverContext":{
                "callbackIntervalInMS":3000,
                "clientId":"0000000000000000000000000000000000000000",
                "deviceLoadStatus":"203",
                "hasDevices":True,
                "lastSessionExtensionTime":None,
                "maxDeviceLoadTime":60000,
                "maxLocatingTime":90000,
                "preferredLanguage":"en",
                "prefsUpdateTime":1276872996660,
                "sessionLifespan":900000,
                "timezone":{
                    "currentOffset":-25200000,
                    "previousOffset":-28800000,
                    "previousTransition":1268560799999,
                    "tzCurrentName":"Pacific Daylight Time",
                    "tzName":"America/Los_Angeles"
                },
                "validRegion":True
            }
        })

        # log 'Sending remote wipe...'
        self.post('/fmipservice/device/%s/remoteWipe' % self.username, body)
        # log 'Remote wipe sent'

    def update_devices(self):
        # log 'updateDevices...'
        body = json.dumps({
            "clientContext":{
                "appName":"FindMyiPhone",
                "appVersion":"1.4",
                "buildVersion":"145",
                "deviceUDID":"0000000000000000000000000000000000000000",
                "inactiveTime":2147483647,
                "osVersion":"4.2.1",
                "personID":0,
                "productType":"iPad1,1"
            }
        })
        header, json_str = self.post('/fmipservice/device/%s/initClient' % self.username, body, None, True)
        json_obj = json.loads(json_str)

        if None == json_obj:
            raise Exception('Error parsing json string')

        if json_obj.get('error') is not None:
            raise Exception('Error from web service: %s' % json_obj['error'])

        self.devices = []
        # log 'Parsing len(json_obj.content) devices...'
        for json_device in json_obj['content']:
            device = Device()
            if json_device.get('location') and type(json_device['location']) is dict:
                device.location_timestamp = datetime.datetime.fromtimestamp(
                    json_device['location']['timeStamp'] / 1000)
                device.location_type = json_device['location']['positionType']
                device.horizontal_accuracy = json_device['location']['horizontalAccuracy']
                device.location_finished = json_device['location']['locationFinished']
                device.longitude = json_device['location']['longitude']
                device.latitude = json_device['location']['latitude']

            device.is_locating = json_device['isLocating']
            device.device_model = json_device['deviceModel']
            device.device_status = json_device['deviceStatus']
            device.id = json_device['id']
            device.name = json_device['name'].encode('utf-8')
            device.deviceClass = json_device['deviceClass']
            device.batteryStatus = json_device['batteryStatus']
            device.batteryLevel = json_device['batteryLevel']

            self.devices.append(device)

    def post(self, url, body, headers=None, return_headers=False):
        if self.partition:
            url = 'https://' + self.partition + url
        else:
            url = 'https://fmipmobile.icloud.com' + url

        # log url
        # log postdata

        if type(body) is dict:
            body = urllib.urlencode(body)

        headers = headers or {}
        headers.update({
            'Content-type': 'application/json; charset=utf-8',
            'X-Apple-Find-Api-Ver': '2.0',
            'X-Apple-Authscheme': 'UserIdGuest',
            'X-Apple-Realm-Support': '1.0',
            'User-agent': 'Find iPhone/1.2 MeKit (iPad: iPhone OS/4.2.1)',
            'X-Client-Name': 'iPad',
            'X-Client-UUID': '0cf3dc501ff812adb0b202baed4f37274b210853',
            'Accept-Language': 'en-us',
            'Connection': 'keep-alive',
            'Authorization': 'Basic %s' % base64.encodestring('%s:%s' % (self.username, self.password,))[:-1],
        })

        opener = urllib2.build_opener(HTTPErrorProcessor())

        req = urllib2.Request(url, '%s' % body, headers)
        resp = opener.open(req)

        if return_headers:
            return resp.headers, resp.read()
        return resp.read()


class Device(object):

    id = '0000000000000000000000000000000000000000'
    name = 'unknown iOS device'

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        return '<Device id="%s" name="%s">' % (self.id, self.name,)


class HTTPErrorProcessor(urllib2.HTTPErrorProcessor):
    """ignores 330 error.
    urllib2 raises 330 error when redirected response did not contains
    any content. (expected: 204 No Contents)
    """
    handler_order = 1000  # after all other processing

    def http_response(self, request, response):
        code, msg, hdrs = response.code, response.msg, response.info()

        if code == 330:
            code = 204
        # According to RFC 2616, "2xx" code indicates that the client's
        # request was successfully received, understood, and accepted.
        if not (200 <= code < 300):
            response = self.parent.error(
                'http', request, response, code, msg, hdrs)

        return response

    https_response = http_response
