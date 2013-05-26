#! /usr/bin/python3
# vim: fileencoding=utf-8 encoding=utf-8 et sw=4

# Copyright (C) 2009 Jacek Konieczny <jajcus@jajcus.net>
# Copyright (C) 2009 Andrzej Zaborowski <balrogg@gmail.com>
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
Convert .osm files to osmChange 0.3 format.
"""

__version__ = "$Revision: 21 $"

import os
import sys
import traceback

import http

import xml.etree.cElementTree as ElementTree

def osmsort(tree, order):
    list = tree[0:len(tree)]
    list.sort(lambda x, y: order.index(x.tag) - order.index(y.tag))
    tree[0:len(tree)] = list

try:
    if len(sys.argv) != 2:
        sys.stderr.write("Synopsis:\n")
        sys.stderr.write("    %s <file-name.osm>\n", (sys.argv[0],))
        sys.exit(1)

    filename = sys.argv[1]
    if not os.path.exists(filename):
        sys.stderr.write("File %r doesn't exist!\n" % (filename,))
        sys.exit(1)
    if filename.endswith(".osm"):
        filename_base = filename[:-4]
    else:
        filename_base = filename

    tree = ElementTree.parse(filename)
    root = tree.getroot()
    if root.tag != "osm" or root.attrib.get("version") != "0.6":
        sys.stderr.write("File %s is not a v0.6 osm file!\n" % (filename,))
        sys.exit(1)

    output_attr = {"version": "0.3", "generator": root.attrib.get("generator")}
    output_root = ElementTree.Element("osmChange", output_attr)
    output_tree = ElementTree.ElementTree(output_root)

    operation = {}
    for opname in [ "create", "modify", "delete" ]:
        operation[opname] = ElementTree.SubElement(output_root,
                opname, output_attr)

    for element in root:
        if "id" in element.attrib and int(element.attrib["id"]) < 0:
            opname = "create"
        elif "action" in element.attrib:
            opname = element.attrib.pop("action")
        else:
            continue
        operation[opname].append(element)

    # Does this account for all cases?  Also, is it needed?
    # (cases like relations containing relations... is that allowed?)
    #osmsort(operation["create"], [ "node", "way", "relation" ])
    #osmsort(operation["delete"], [ "relation", "way", "node" ])

    output_tree.write(filename_base + ".osc", "utf-8")
except Exception as err:
    sys.stderr.write(repr(err) + "\n")
    traceback.print_exc(file = sys.stderr)
    sys.exit(1)
