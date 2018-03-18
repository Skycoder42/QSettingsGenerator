#!/usr/bin/env python3
# Usage: generator.py <in> <out_hdr> <out_src> [<mvvm_xml> ...]

import sys
import os.path
import copy
try:
	from defusedxml.ElementTree import parse, ElementTree
except ImportError:
	from xml.etree.ElementTree import parse, ElementTree


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
	else:
		raise Exception("Unexpected Element: " + element.tag)

	for child in element:
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
	file.write("#ifdef QT_MVVMCORE_LIB\n")
	file.write("#include <QtMvvmCore/Injection>\n")
	file.write("#endif\n")
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
	file.write("\tQ_PROPERTY(ISettingsAccessor* accessor MEMBER _accessor)\n")
	file.write("#ifdef QT_MVVMCORE_LIB\n")
	file.write("\tQTMVVM_INJECT(ISettingsAccessor*, accessor)\n")
	file.write("#endif\n\n")

	file.write("public:\n")
	file.write("\tQ_INVOKABLE explicit {}(QObject *parent = nullptr);\n\n".format(name))
	file.write("\tstatic {} *instance();\n\n".format(name))
	file.write("\tvoid setAccessor(ISettingsAccessor* accessor);\n\n")

	write_header_content(file, tree)

	file.write("\nprivate Q_SLOTS:\n")
	file.write("\tvoid qtmvvm_init();\n\n")
	file.write("private:\n")
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
			if node.default != "":
				file.write(", QVariant(QStringLiteral(\"{}\")));\n".format(node.default))
			else:
				file.write(");\n")
		write_node_setup(file, node, nfix)


def create_settings_file_source(file, header: str, name: str, tree: SettingsNode):
	file.write("#include \"{}\"\n".format(header))
	file.write("#ifdef QT_MVVMCORE_LIB\n")
	file.write("#include <QCoreApplication>\n")
	file.write("#include <QtMvvmCore/ServiceRegistry>\n")
	file.write("#else\n")
	file.write("#include <QGlobalStatic>\n")
	file.write("#endif\n\n")

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
	file.write("Q_GLOBAL_STATIC_ARGS({}*, settings_instance)\n".format(name))
	file.write("#endif\n\n")

	# constructor
	file.write("{}::{}(QObject *parent) :\n".format(name, name))
	file.write("\tQObject(parent),\n")
	file.write("\t_accessor(nullptr)\n")
	file.write("{}\n\n")

	# instance
	file.write("{} *{}::instance()\n".format(name, name))
	file.write("{\n")
	file.write("#ifdef QT_MVVMCORE_LIB\n")
	file.write("\treturn QtMvvm::ServiceRegistry::instance()->service<{}>();\n".format(name))
	file.write("#else\n")
	file.write("\treturn settings_instance;\n")
	file.write("#endif\n")
	file.write("}\n\n")

	# setAccessor
	file.write("void {}::setAccessor(ISettingsAccessor* accessor)\n".format(name))
	file.write("{\n")
	file.write("\t_accessor = accessor;\n")
	file.write("\tqtmvvm_init();\n")
	file.write("}\n\n")

	# qtmvvm_init
	file.write("void {}::qtmvvm_init()\n".format(name))
	file.write("{\n")
	file.write("\tQ_ASSERT_X(_accessor, Q_FUNC_INFO, \"You must set a valid accessor before initializing the settings!\");\n")
	write_node_setup(file, tree)
	file.write("}\n")


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
		create_settings_file_header(file, root.attrib["name"], node_tree, includes, root.attrib["prefix"])
	with open(out_src, "w") as file:
		create_settings_file_source(file, os.path.basename(out_header), root.attrib["name"], node_tree)


if __name__ == '__main__':
	generate_settings_accessor(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:])
