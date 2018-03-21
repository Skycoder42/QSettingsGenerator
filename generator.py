#!/usr/bin/env python3
# Usage: generator.py <in> <out_hdr> <out_src> [<mvvm_xml> ...]

import sys
import os.path
import copy

from enum import Enum
try:
	from defusedxml.ElementTree import parse, ElementTree
except ImportError:
	from xml.etree.ElementTree import parse, ElementTree


class DefaultType(Enum):
	Empty = 0
	Standard = 1,
	Translated = 2,
	Code = 3


class SettingsNode(list):
	key: str

	def child(self, key):
		for node in self:
			if node.key == key:
				return node
		return None

	def __init__(self, key: str):
		super().__init__()
		self.key = key


class SettingsEntry(SettingsNode):
	type: str
	default: str
	default_type: DefaultType = DefaultType.Empty
	ts_key: str = ""

	def __init__(self, key: str, type: str, default: str=""):
		super().__init__(key)
		self.type = map_type(type)
		self.default = default


def map_type(type: str):
	tmap = {
		"switch": "bool",
		"string": "QString",
		"number": "double",
		"date": "QDateTime",
		"list": "QVariant",
		"selection": "QVariant",
		"radiolist": "QVariant",
		"url": "QUrl",
		"action": "void"
	}
	return tmap[type] if type in tmap else type


def parse_element(element: any) -> SettingsNode:
	if element.tag == "Node":
		node = SettingsNode(element.attrib["key"])
	elif element.tag == "Entry":
		node = SettingsEntry(element.attrib["key"], element.attrib["type"])
		if "default" in element.attrib:
			node.default = element.attrib["default"]
			if "ts" in element.attrib:
				node.ts_key = element.attrib["ts"]
				node.default_type = DefaultType.Translated
			else:
				node.default_type = DefaultType.Standard
	else:
		raise Exception("Unexpected Element: " + element.tag)

	for child in element:
		if isinstance(node, SettingsEntry) and child.tag == "Code":
			if node.default_type != DefaultType.Empty:
				raise Exception("An Entry can have at most one <Code> element. You cannot combine it with the \"default\" attribute")
			node.default_type = DefaultType.Code
			node.default = child.text
		else:
			node.append(parse_element(child))

	return node


def add_tree_normal(root_node: SettingsNode, root_element: any) -> list:
	res_list = []
	for child in root_element:
		if child.tag == "Include":
			res_list.append(child.text)
		else:
			root_node.append(parse_element(child))
	return res_list


def add_tree_mvvm(root_node: SettingsNode, root_tree: ElementTree):

	for elem in root_tree.iter("Entry"):
		keys = elem.attrib["key"].split("/")

		current_node = root_node
		for key in keys[:-1]:
			node = current_node.child(key)
			if node is None:
				node = SettingsNode(key)
				current_node.append(node)
			current_node = node

		entry_key = keys[-1]
		if current_node.child(entry_key) is None:
			entry = SettingsEntry(entry_key, elem.attrib["type"])
			if "default" in elem.attrib:
				entry.default = elem.attrib["default"]
				if elem.attrib["tsdefault"] if "tsdefault" in elem.attrib else False:
					node.ts_key = "qtmvvm_settings_xml"
					node.default_type = DefaultType.Translated
				else:
					node.default_type = DefaultType.Standard
			current_node.append(entry)


def flatten(tree: SettingsNode, prefix: str=""):
	for child in tree:
		if isinstance(child, SettingsEntry):
			print(prefix + child.key + ": " + child.type + " = " + child.default)
		flatten(child, prefix + child.key + "/")


def write_header_content(file, parent_node: SettingsNode, intendent: int=1):
	tabs = "\t" * intendent
	for node in parent_node:
		if isinstance(node, SettingsEntry):
			if len(node) == 0:
				file.write(tabs + "SettingsEntry<{}> {};\n".format(node.type, node.key))
			else:
				file.write(tabs + "struct : SettingsEntry<{}> {{\n".format(node.type))
				write_header_content(file, node, intendent+1)
				file.write(tabs + "\tauto &operator=({} value) {{\n".format(node.type))
				file.write(tabs + "\t\t((SettingsEntry<{}>&)*this) = value;\n".format(node.type))
				file.write(tabs + "\t\treturn (*this);\n")
				file.write(tabs + "\t}\n")
				file.write(tabs + "}} {};\n".format(node.key))
		else:
			file.write(tabs + "struct {\n")
			write_header_content(file, node, intendent+1)
			file.write(tabs + "}} {};\n".format(node.key))


def create_settings_file_header(file, name: str, tree: SettingsNode, includes: list, prefix: str):
	# write header
	guard = file.name.replace(".", "_").upper()
	file.write("#ifndef {}\n".format(guard))
	file.write("#define {}\n\n".format(guard))

	file.write("#include <QObject>\n")
	file.write("#include <isettingsaccessor.h>\n")
	file.write("#include <settingsentry.h>\n\n")

	for include in includes:
		file.write("#include <{}>\n".format(include))
	if len(includes) > 0:
		file.write("\n")

	if prefix == "":
		prefix = name
	else:
		prefix += " " + name
	file.write("class {} : public QObject\n".format(prefix))
	file.write("{\n")
	file.write("\tQ_OBJECT\n\n")

	file.write("public:\n")
	file.write("\tQ_INVOKABLE explicit {}(QObject *parent = nullptr);\n".format(name))
	file.write("\texplicit {}(QObject *parent, ISettingsAccessor *accessor);\n\n".format(name))
	file.write("\tstatic {} *instance();\n\n".format(name))

	write_header_content(file, tree)

	file.write("\nprivate:\n")
	file.write("\tISettingsAccessor *_accessor;\n")
	file.write("};\n\n")

	file.write("#endif //{}\n".format(guard))


def write_node_setup(file, parent_node: SettingsNode, prefix: list=None):
	if prefix is None:
		prefix = []

	for node in parent_node:
		nfix = copy.copy(prefix)
		nfix.append(node.key)
		if isinstance(node, SettingsEntry):
			file.write("\t{}.setup(QStringLiteral(\"{}\"), _accessor".format(".".join(nfix), "/".join(nfix)))
			if node.default_type == DefaultType.Empty:
				file.write(");\n")
			elif node.default_type == DefaultType.Standard:
				file.write(", QVariant(QStringLiteral(\"{}\")));\n".format(node.default))
			elif node.default_type == DefaultType.Translated:
				file.write(", QVariant(QCoreApplication::translate(\"{}\", \"{}\")));\n".format(node.ts_key, node.default))
			elif node.default_type == DefaultType.Code:
				file.write(", QVariant::fromValue<{}>({}));\n".format(node.type, node.default.strip()))
		write_node_setup(file, node, nfix)


def create_settings_file_source(file, header: str, name: str, tree: SettingsNode, accessor: str):
	file.write("#include \"{}\"\n".format(header))
	file.write("#include <QCoreApplication>\n")
	file.write("#ifdef QT_MVVMCORE_LIB\n")
	file.write("#include <QtMvvmCore/ServiceRegistry>\n")
	file.write("#else\n")
	file.write("#include <QGlobalStatic>\n")
	file.write("#endif\n")
	file.write("#include <qsettingsaccessor.h>\n")
	file.write("#include <datasyncsettingsaccessor.h>\n\n")

	# setup
	file.write("#ifdef QT_MVVMCORE_LIB\n")
	file.write("namespace {\n\n")
	file.write("void __generated_settings_setup()\n")
	file.write("{\n")
	file.write("\tQtMvvm::ServiceRegistry::instance()->registerObject<{}>();\n".format(name))
	file.write("}\n\n")
	file.write("}\n")
	file.write("Q_COREAPP_STARTUP_FUNCTION(__generated_settings_setup)\n")
	file.write("#else\n")
	file.write("Q_GLOBAL_STATIC({}, settings_instance)\n".format(name))
	file.write("#endif\n\n")

	# constructor 1
	file.write("{}::{}(QObject *parent) :\n".format(name, name))
	file.write("\t{}(parent, new {}())\n".format(name, accessor))
	file.write("{}\n\n")

	# constructor 2
	file.write("{}::{}(QObject *parent, ISettingsAccessor *accessor) :\n".format(name, name))
	file.write("\tQObject(parent),\n")
	file.write("\t_accessor(accessor)\n")
	file.write("{\n")
	file.write("\tdynamic_cast<QObject*>(_accessor)->setParent(this);\n")
	write_node_setup(file, tree)
	file.write("}\n\n")

	# instance
	file.write("{} *{}::instance()\n".format(name, name))
	file.write("{\n")
	file.write("#ifdef QT_MVVMCORE_LIB\n")
	file.write("\treturn QtMvvm::ServiceRegistry::instance()->service<{}>();\n".format(name))
	file.write("#else\n")
	file.write("\treturn settings_instance;\n")
	file.write("#endif\n")
	file.write("}\n\n")


def generate_settings_accessor(in_file: str, out_header: str, out_src: str, mvvm_files: list):
	node_tree = SettingsNode("")

	# parse primary file
	xml = parse(in_file)
	root = xml.getroot()
	includes = add_tree_normal(node_tree, root)

	# additional mvvm files
	for file in mvvm_files:
		xml = parse(file)
		add_tree_mvvm(node_tree, xml)

	# print a flat key list
	flatten(node_tree)

	# create the actual header
	with open(out_header, "w") as file:
		prefix = root.attrib["prefix"] if "prefix" in root.attrib else ""
		create_settings_file_header(file, root.attrib["name"], node_tree, includes, prefix)
	with open(out_src, "w") as file:
		backend = root.attrib["backend"] if "backend" in root.attrib else "QSettingsAccessor"
		create_settings_file_source(file, os.path.basename(out_header), root.attrib["name"], node_tree, backend)


if __name__ == '__main__':
	generate_settings_accessor(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:])
