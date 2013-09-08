#! /usr/bin/python3
# vim: fileencoding=utf-8 encoding=utf-8 et sw=4

# Copyright (C) 2009 Jacek Konieczny <jajcus@jajcus.net>
# Copyright (C) 2009 Andrzej Zaborowski <balrogg@gmail.com>
# Copyright (C) 2013 Jason Remillard <remillard.jason@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


"""
Uploads complete osmChange 0.3 or 0.9 files.  Use your login (not email) as username.
"""

__version__ = "$Revision: 21 $"

import os
import subprocess
import sys
import traceback
import base64
import codecs
import optparse
import time

import http.client as httplib
import xml.etree.cElementTree as ElementTree
import urllib.parse as urlparse

class HTTPError(Exception):
    pass

class OSM_API(object):
    url = 'http://api06.dev.openstreetmap.org/'
    def __init__(self, url, username = None, password = None):
        if username and password:
            self.username = username
            self.password = password
        else:
            self.username = ""
            self.password = ""
        self.changeset = None
        self.url = url
        self.debugLogFile = None

    def __del__(self):
        if ( self.debugLogFile ) :
            self.debugLogFile.close()
        pass

    def debugLogFilename(self,filename) :
        if ( self.debugLogFile ) :
            self.debugLogFile.close()
            self.debugLogFile = None
        self.debugLogFile = open( filename,"w")

    def debugMsg(self, mesg):
        if ( self.debugLogFile ) :
            self.debugLogFile.write(mesg )
            self.debugLogFile.flush

    def request(self, conn, method, url, body, headers, progress):
        if progress:
            self.debugMsg("  making request %s\n" % (url,))
            conn.putrequest(method, url)

            self.debugMsg("  sending headers\n")
            if body:
                conn.putheader('Content-Length', str(len(body)))
            for hdr, value in headers.items():
                conn.putheader(hdr, value)

            self.debugMsg("  end of headers\n")
            conn.endheaders()

            self.debugMsg("  Sending data 0%")
            if body:
                start = 0
                size = len(body)
                chunk = size / 100
                if chunk < 16384:
                    chunk = 16384
                while start < size:
                    end = min(size, int(start + chunk))
                    conn.send(body[start:end])
                    start = end
                    self.debugMsg(" %2i%%" % (int(start * 100 / size),))
            self.debugMsg("\n")
        else:
            conn.request(method, url, body, headers)

    def _run_request(self, method, url, body = None, progress = 0, content_type = "text/xml"):
        url = urlparse.urljoin(self.url, url)
        purl = urlparse.urlparse(url)
        if purl.scheme != "http":
            raise ValueError("Unsupported url scheme: %r" % (purl.scheme,))
        if ":" in purl.netloc:
            host, port = purl.netloc.split(":", 1)
            port = int(port)
        else:
            host = purl.netloc
            port = None
        url = purl.path
        if purl.query:
            url += "?" + query
        headers = {}
        if body:
            headers["Content-Type"] = content_type

        try_no_auth = 0

        if not try_no_auth and not self.username:
            raise HTTPError(0, "Need a username")

        try:
            self.debugMsg("  connecting\n")
            conn = httplib.HTTPConnection(host, port)
#            conn.set_debuglevel(10)

            if try_no_auth:
                self.request(conn, method, url, body, headers, progress)
                self.debugMsg("  waiting for status for %s\n" % (url,))
                response = conn.getresponse()

            if not try_no_auth or (response.status == httplib.UNAUTHORIZED and
                    self.username):
                if try_no_auth:
                    conn.close()
                    self.debugMsg("  re-connecting\n")
                    conn = httplib.HTTPConnection(host, port)
#                    conn.set_debuglevel(10)

                creds = self.username + ":" + self.password
                headers["Authorization"] = "Basic " + \
                        base64.b64encode(bytes(creds, "utf8")).decode("utf8")
                        # ^ Seems to be broken in python3 (even the raw
                        # documentation examples don't run for base64)
                self.request(conn, method, url, body, headers, progress)
                self.debugMsg("  waiting for status for %s\n" % (url,))
                response = conn.getresponse()

            if response.status == httplib.OK:
                self.debugMsg("  reading response\n")
                response_body = response.read()
            else:
                err = response.read()
                raise HTTPError(response.status, "%03i: %s (%s)" % (
                    response.status, response.reason, err), err)
        finally:
            conn.close()
        return response_body

    def create_changeset(self, created_by, comment,source,bot):
        if self.changeset is not None:
            raise RuntimeError("Change set already opened")

        self.debugMsg("Creating the change set on %s\n" %( self.url,))

        root = ElementTree.Element("osm")
        tree = ElementTree.ElementTree(root)
        element = ElementTree.SubElement(root, "changeset")
        ElementTree.SubElement(element, "tag", {"k": "created_by", "v": created_by})
        
        if ( comment ) :
            ElementTree.SubElement(element, "tag", {"k": "comment", "v": comment})

        if ( source ) :
            ElementTree.SubElement(element, "tag", {"k": "source", "v": source})
        
        if ( bot ) :
            ElementTree.SubElement(element, "tag", {"k": "bot", "v": "yes"})

        body = ElementTree.tostring(root, "utf-8")
        reply = self._run_request("PUT", "/api/0.6/changeset/create", body)
        changeset = int(reply.strip())
        self.debugMsg("  change set id: %i\n" % (changeset))
        self.changeset = changeset
       
    def upload(self, change):
        if self.changeset is None:
            raise RuntimeError("Change set not opened")
        self.debugMsg("Uploading OSC file\n")

        # add in changeset tag to all of the elements.
        for operation in change:
            if operation.tag not in ("create", "modify", "delete"):
                continue
            for element in operation:
                element.attrib["changeset"] = str(self.changeset)

        body = ElementTree.tostring(change, "utf-8")
        reply = self._run_request("POST", "/api/0.6/changeset/%i/upload"
                                                % (self.changeset,), body)
        self.debugMsg("  upload is done.\n")
        
        return reply

    # Sometimes the server will close a change set on us, need to this function
    # to figure out if we should close it when an error is thrown.
    def is_open_changeset(self) :
        if self.changeset is None:
            return False

        self.debugMsg("  checking if change set is still open.\n");
        reply = self._run_request("GET", "/api/0.6/changeset/%i" % (self.changeset,))

        root = ElementTree.fromstring(reply)

        is_open = False;

        for changeset in root :
            if ( changeset.attrib.get('open') == 'true') :
                self.debugMsg("  still open\n")
                is_open = True;
            else :
                self.debugMsg("  closed\n")

        self.debugMsg("  done\n")

        return is_open

    def close_changeset(self):
        if self.changeset is None:
            raise RuntimeError("Change set not opened")
        self.debugMsg("Closing change set\n");
        reply = self._run_request("PUT", "/api/0.6/changeset/%i/close"
                                                    % (self.changeset,))
        self.changeset = None
        self.debugMsg("  done\n")

    def forget_changeset(self) :
        self.changeset = None
        self.debugMsg("  forgetting change set\n")

try:
    this_dir = os.path.dirname(__file__)

    parser = optparse.OptionParser(description='Upload Open Street Map OSC files.',usage='upload.py [options] uploadfile1.osc [uploadfile2.osc] ...')
    parser.add_option('-u','--user',help='OSM Username (not email)',dest='user')
    parser.add_option('-p','--password',help='OSM password',dest='password')
    parser.add_option('--sleep',help='Sleep between upload files (s)',dest='sleep')
    parser.add_option('-m','--comment',help='Sets the changeset comment tag value. Can also use .comment file.',dest='comment')
    parser.add_option('--source',help='Sets the changeset source tag value. Can also use .source file',dest='source')
    parser.add_option('--server',help='URL for upload server (url,test,live), required.')
    parser.add_option('--bot',help='Sets the bot=yes changeset tag. Optional',action='store_true',dest='bot')
    (param,filenames) = parser.parse_args()

    if ( not param.server ) :
        parser.print_help()
        print("\n\nerror: --server flag is required.")
        sys.exit(1)
      
    if ( param.server == 'test') :
        param.server = 'http://api06.dev.openstreetmap.org'
    elif (param.server == 'live') :
        param.server = 'http://api.openstreetmap.org'
        
    if ( param.user) :
        login = param.user
    else:
        login = input("OSM login: ")
    if not login:
        sys.exit(1)

    if (param.password) :
        password = param.password
    else:
        password = input("OSM password: ")
    if not password:
        sys.exit(1)

    bot = False
    if (param.bot ) :
      bot = True
    
    api = OSM_API(param.server,login, password)

    changes = []
    for filename in filenames:
        
        print("%-50s " % (filename ,), end='')
        sys.stdout.flush()

        if not os.path.exists(filename):
            print("skipped, does not exist." % (filename,))
            continue

        tree = ElementTree.parse(filename)
        root = tree.getroot()
        if root.tag != "osmChange" or (root.attrib.get("version") != "0.3" and root.attrib.get("version") != "0.6") or not filename.endswith(".osc") :
            print("skipped, must be 0.3 or 0.6 OSC file")
            continue
        
        diff_fn = filename[:-4] + ".diff.xml"
        status_fn = filename[:-4] + "-status.txt"

        if os.path.exists(status_fn) or os.path.exists(diff_fn) :
            print("skipped, already uploaded.")
            continue
                 
        comment_fn = filename[:-4] + ".comment"
        try:
            comment_file = codecs.open(comment_fn, "r", "utf-8")
            comment = comment_file.read().strip()
            comment_file.close()
        except IOError:
            comment = param.comment

        source_fn = filename[:-4] + ".source"
        try:
            source_file = codecs.open(source_fn, "r", "utf-8")
            source = source_file.read().strip()
            source_file.close()
        except IOError:
            source = param.source
             
        api.debugLogFilename( status_fn)
        api.create_changeset("osmupload.py v1.0", comment, source,bot)

        try:
            diff = api.upload(root)

            api.debugMsg( "Writing %s " % (diff_fn,));
            diff_file = codecs.open(diff_fn, "w", "utf-8")
            diff_file.write(diff.decode("utf8"))
            diff_file.close()
            api.debugMsg( "OK\n");

            api.close_changeset()
            api.debugMsg( "Upload completed successfully\n");
            print("OK")

        except HTTPError as e:
            if e.args[0] in [ 404, 409, 412 ] and os.path.exists(diff_fn): 
                # Merge conflict
                os.unlink(diff_fn)

            api.debugMsg( "  error code %d\n\n" % (e.args[0],))

            errstr = e.args[2].decode("utf8")
            api.debugMsg( errstr + "\n\n")
            if ( api.is_open_changeset()) :
                api.close_changeset()
            else :
                api.forget_changeset()

            print("FAIL")

        sys.stdout.flush()
        if ( param.sleep ) : 
            time.sleep ( float(param.sleep));

except HTTPError as err:
    sys.stderr.write(err.args[1])
    sys.exit(1)

except Exception as err:
    sys.stderr.write(repr(err) + "\n")
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)



