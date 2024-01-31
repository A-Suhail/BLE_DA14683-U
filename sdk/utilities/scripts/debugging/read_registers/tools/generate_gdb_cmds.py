#!/usr/bin/env python

import xml.etree.ElementTree as ET
import xml.dom.minidom as MD
import sys, getopt

gdb_cmd_file = "gdb_cmds"
xml_template_file = "template_register_values.xml"

def usage(argv):
        print "usage: " + argv[0] + " -f <xml_file> [-g, --gdb_cmds] [-x, --xml_template]"
        print ""
        print "e.g " + argv[0] + " -f ../../../../doc/DA14681-00.xml -g"
        print "Generate a gdb script based on the given xml file."
        print ""
        print "e.g " + argv[0] + " -f ../../../../doc/DA14681-00.xml -x"
        print "Generate an xml template based on the given xml file."
        print "Used for validation purposes only."


def create_gdb_cmd_file(root):
        file_handle = open(gdb_cmd_file, 'w')
        header = "target remote :2331\n"
        header += "set pagination off\n"
        header += "set logging on\n"
        file_handle.write(header)

        for peripheral in root.iter('peripheral'):
                p_name = peripheral.find('name').text
                p_base = peripheral.find('baseAddress').text
                cmd0 = "echo __PERIPHERAL__: " + p_name + "\\n" + "\n"
                file_handle.write(cmd0)
                base = int(p_base, 16)
                for register in peripheral.find('registers').iter('register'):
                        r_name = register.find('name').text
                        r_offset = register.find('addressOffset').text
                        r_size = register.find('size').text
                        offset = int(r_offset, 16)
                        address = hex(base + offset)
                        cmd1 = "echo __REG__: " + r_name  + " \ " + "\n"
                        file_handle.write(cmd1)
                        cmd2 = "monitor memU" + r_size + " " + address + "\n"
                        file_handle.write(cmd2)

        footer = "set logging off\n"
        footer += "quit\n"
        file_handle.write(footer)

def create_xml_template(root):
        file_handle = open(xml_template_file, 'w')
        template_p_root =  ET.Element("peripherals")

        for peripheral in root.iter('peripheral'):
                p_name = peripheral.find('name').text
                template_p_name = ET.SubElement(template_p_root, p_name)
                for register in peripheral.find('registers').iter('register'):
                        r_name = register.find('name').text
                        ET.SubElement(template_p_name, "REG", name=r_name).text = "magic_value"

        xmlstr = ET.tostring(template_p_root)
        dom = MD.parseString(xmlstr)
        file_handle.write(dom.toprettyxml())

def main(argv):
        root = None
        try:
                opts, args = getopt.getopt(argv[1:],"hf:gx",["gdb_cmds","xml_template"])
        except getopt.GetoptError:
                usage(argv)
                sys.exit(2)
        if len(argv[1:]) < 3:
                usage(argv)
                sys.exit(1)
        for opt, arg in opts:
                if opt == '-h':
                        usage(argv)
                        sys.exit(0)
                elif opt == '-f':
                        xml_file = arg
                        tree = ET.parse(xml_file)
                        root = tree.getroot()
                elif opt in ("-g", "--gdb_cmds"):
                        create_gdb_cmd_file(root)
                elif opt in ("-x", "--xml_template"):
                        create_xml_template(root)


if __name__ == "__main__":
        main(sys.argv[0:])
