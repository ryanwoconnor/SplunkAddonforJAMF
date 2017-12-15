#!/usr/bin/python
# -*- coding: utf-8 -*-
####################################################################################################
#
# Copyright (c) 2015, JAMF Software, LLC.  All rights reserved.
#
#       Redistribution and use in source and binary forms, with or without
#       modification, are permitted provided that the following conditions are met:
#               * Redistributions of source code must retain the above copyright
#                 notice, this list of conditions and the following disclaimer.
#               * Redistributions in binary form must reproduce the above copyright
#                 notice, this list of conditions and the following disclaimer in the
#                 documentation and/or other materials provided with the distribution.
#               * Neither the name of the JAMF Software, LLC nor the
#                 names of its contributors may be used to endorse or promote products
#                 derived from this software without specific prior written permission.
#
#       THIS SOFTWARE IS PROVIDED BY JAMF SOFTWARE, LLC "AS IS" AND ANY
#       EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#       WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#       DISCLAIMED. IN NO EVENT SHALL JAMF SOFTWARE, LLC BE LIABLE FOR ANY
#       DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#       (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#       LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#       ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#       (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#       SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
####################################################################################################
#
# SUPPORT FOR THIS PROGRAM
#
#       This program is distributed "as is" by JAMF Software, LLC.
#
####################################################################################################
#
# ABOUT THIS PROGRAM
#
# NAME
#    updateDeviceInventory.py -- Update Mobile Device Inventory
#
# SYNOPSIS
#    /usr/bin/python updateDeviceInventory.py
#
# DESCRIPTION
#    This script was designed to update all mobile device inventory in a JSS.
#
#    For the script to function properly, users must be running the JSS version 7.31 or later and
#    the account provided must have API privileges to "READ" and "UPDATE" mobile devices in the JSS.
#
####################################################################################################
#
# HISTORY
#
#    Version: 1.2
#
#    - Created by Nick Amundsen on June 23, 2011
#    - Updated by Bram Cohen on May 12, 2016
#       Added TLSv1 and new JSON Response on 9.6+
#
#####################################################################################################
#
# DEFINE VARIABLES & READ IN PARAMETERS
#
#####################################################################################################
#
# HARDCODED VALUES SET HERE
#
jss_host = "127.0.0.1" #Example: 127.0.0.1 if run on server
jss_port = 8443
jss_path = "" #Example: "jss" for a JSS at https://www.company.com:8443/jss
jss_username = "admin"
jss_password = "jamf1234"
jss_computer_output_file = '/path/to/file/devices.json'

##DONT EDIT BELOW THIS LINE
import json
import httplib
import base64
import urllib2
import ssl
import socket

##Computer Object Definition
class Device:
    id = -1

##Check variable
def verifyVariable(name, value):
    if value == "":
        print "Error: Please specify a value for variable \"" + name + "\""
        sys.exit(1)

## the main function.
def main():
    #verifyVariable("jss_host",jss_host)
    #verifyVariable("jss_port",jss_port)
    #verifyVariable("jss_username",jss_username)
    #verifyVariable("jss_password",jss_password)
    #verifyVariable("jss_computer_output_file",jss_computer_output_file)
    devices=grabDeviceIDs()
    #updateDeviceInventory(devices)

##Grab and parse computers and return them in an array.
def grabDeviceIDs():

	#create array for devices
    devices=[];
    
    #grab device list into raw JSON
    deviceList = (getDeviceListFromJSS()["computers"])
    
    # output text
	f = open(jss_computer_output_file,'w')
	f.write(deviceList)
	f.close()
	
    ## parse the list
    for deviceListJSON in deviceList:
        d = Device()
        d.id = deviceListJSON.get("id")
        devices.append(d)
    print "Found " + str(len(devices)) + " devices."
    return devices

class TLS1Connection(httplib.HTTPSConnection):
    def __init__(self, host, **kwargs):
        httplib.HTTPSConnection.__init__(self, host, **kwargs)

    def connect(self):
        sock = socket.create_connection((self.host, self.port), self.timeout, self.source_address)
        if getattr(self, '_tunnel_host', None):
            self.sock = sock
            self._tunnel()

        self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file, ssl_version=ssl.PROTOCOL_TLSv1)


class TLS1Handler(urllib2.HTTPSHandler):
    def __init__(self):
        urllib2.HTTPSHandler.__init__(self)

    def https_open(self, req):
        return self.do_open(TLS1Connection, req)



##Create a header for the request
def getAuthHeader(u,p):
    # Compute base64 representation of the authentication token.
    token = base64.b64encode('%s:%s' % (u,p))
    return "Basic %s" % token

##Download a list of all computer devices from the JSS API
def getDeviceListFromJSS():
    print "Getting device list from the JSS..."
    opener = urllib2.build_opener(TLS1Handler())

    request = urllib2.Request("https://" + str(jss_host) + ":" + str(jss_port) + str(jss_path) + "/JSSResource/computers")
    request.add_header("Authorization", "Basic " + base64.b64encode('%s:%s' % (jss_username,jss_password)))
    request.add_header("Accept", "application/json")
    request.get_method = lambda: 'GET'

    try:
        data = opener.open(request)
        return json.load(data)
    except httplib.HTTPException as inst:
        print "Exception: %s" % inst
        sys.exit(1)
    except ValueError as inst:
        print "Exception decoding JSON: %s" % inst
        sys.exit(1)
## Code starts executing here. Just call main.
main()
