#!/usr/bin/env python

import xml.etree.ElementTree as ET
import xml.dom.minidom as MD
import sys, getopt
import re

periph_regex = "^__PERIPHERAL__:\W+(\w+)$"
regist_regex = "^__REG__:\W+(\w+\W+).*\((.*)\)"

def dump2xml(dump_file):
        out_file = dump_file + ".xml"
        dump_file_handle = open(dump_file, 'r')
        xml_file_handle = open(out_file, 'w')
        p_root =  ET.Element("peripherals")

        for line in dump_file_handle:
                p_found = re.findall(periph_regex, line)
                if len(p_found):
                        p_name = ET.SubElement(p_root, p_found[0])
                        continue
                r_found = re.findall(regist_regex, line)
                if len(r_found):
                        r_name = r_found[0][0]
                        r_value = re.sub('Data\W+=\W+', '', r_found[0][1])
                        ET.SubElement(p_name, "REG", name=r_name).text = r_value

        xmlstr = ET.tostring(p_root)
        dom = MD.parseString(xmlstr)
        xml_file_handle.write(dom.toprettyxml())
        print "Output: " + out_file


def usage(argv):
        print "usage: " + argv[0] + " -f <register_dump_file>"
        print ""
        print "e.g " + argv[0] + " -f register_dumps/registers_20160105-1452000871.log"
        print "The generated file is found on the some path given in the -f option."

def main(argv):
        root = None
        try:
                opts, args = getopt.getopt(argv[1:],"hf:")
        except getopt.GetoptError:
                usage(argv)
                sys.exit(2)
        if len(argv[1:]) == 0:
                usage(argv)
                sys.exit(1)
        for opt, arg in opts:
                if opt == '-h':
                        usage(argv)
                        sys.exit(0)
                elif opt == '-f':
                        dump2xml(arg)

if __name__ == "__main__":
        main(sys.argv[0:])
