# QSettingsGenerator
A qmake extension to generate a C++ settings wrapper for easier, stringless access.

The general idea is that instead of this:
```cpp
QSettins settings;
int value = settings.value("my/key", 42).toInt();
```

You create a settings file like this:
```xml
<Settings name="Settings">
	<Node key="my">
		<Entry key="key" type="int" default="42"/>
	</Node>
</Settings>
```

And can now access the data like this:
```cpp
int value = Settings::instance()->my.key;
```

## Features
- Access settings via code - no more typos and redundant strings!
- Static typing gives additionl saftey and is easier to use (no `.toType()` calls needed)
- Default values in one single, central place - less error prone and easier to maintain
	- Can be specified as strings in the xml
	- Can be specified as C++ code in the xml
- Use as a global single instance or create local instances
- Support for custom settings backends instead of QSettings alone
	- A backend for [QtDataSync](https://github.com/Skycoder42/QtDataSync) is already included
- Can be used as a [QtMvvm](https://github.com/Skycoder42/QtMvvm) injectable service

## Installation
The package is providet as qpm  package, [`de.skycoder42.qsettingsgenerator`](https://www.qpm.io/packages/de.skycoder42.qsettingsgenerator/index.html). You can install it either via qpmx (preferred) or directly via qpm.

### Via qpmx
[qpmx](https://github.com/Skycoder42/qpmx) is a frontend for qpm (and other tools) with additional features, and is the preferred way to install packages. To use it:

1. Install qpmx (See [GitHub - Installation](https://github.com/Skycoder42/qpmx#installation))
2. Install qpm (See [GitHub - Installing](https://github.com/Cutehacks/qpm/blob/master/README.md#installing), for **windows** see below)
3. In your projects root directory, run `qpmx install de.skycoder42.qsettingsgenerator`

### Via qpm

1. Install qpm (See [GitHub - Installing](https://github.com/Cutehacks/qpm/blob/master/README.md#installing), for **windows** see below)
2. In your projects root directory, run `qpm install de.skycoder42.qsettingsgenerator`
3. Include qpm to your project by adding `include(vendor/vendor.pri)` to your `.pro` file

Check their [GitHub - Usage for App Developers](https://github.com/Cutehacks/qpm/blob/master/README.md#usage-for-app-developers) to learn more about qpm.

**Important for Windows users:** QPM Version *0.10.0* (the one you can download on the website) is currently broken on windows! It's already fixed in master, but not released yet. Until a newer versions gets released, you can download the latest dev build from here:
- https://storage.googleapis.com/www.qpm.io/download/latest/windows_amd64/qpm.exe
- https://storage.googleapis.com/www.qpm.io/download/latest/windows_386/qpm.exe

## Usage
The package adds a custom qmake compiler to you project. All you need to do is to create the settings xml definition and then add it to the pro file as `SETTINGS_GENERATORS += mysettings.xml`. This will create a header named "mysettings.h" you can include. That header contains the C++ generated settings class to access the settings.

### Example
Create a pro file with the package included and add the line:
```pro
SETTINGS_GENERATORS += mysettings.xml
```

Create a file named `mysettings.xml` and fill it:
```xml
<?xml version="1.0" encoding="UTF-8" ?>
<Settings name="MySettings">
	<Node key="my">
		<Entry key="key" type="int" default="42"/>
	</Node>
</Settings>
```

Finally, adjust you main to look like this:
```cpp
#include <QCoreApplication>
#include <QDebug>
#include "mysettings.h"

int main(int argc, char *argv[])
{
	QCoreApplication a(argc, argv);

	int myKey = MySettings::instance()->my.key;
	qDebug() << myKey;

	return 0;
}
```

### Settings XML documentation
The format is rather simple. It consists of nodes and entries. Nodes are simply helpers to group settings entries
and are used for the key generation, but are no entries themselves. Entries are the actual settings entries. The following XML is a copy from the includes sample project and shows what you file can contain:

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<Settings name="Settings" backend="QSettingsAccessor"> <!-- You can use custom backends per file. This is the default one -->
	<!-- Additional includes can be added -->
	<Include>mytype.h</Include>

	<!-- Basic Nodes with entries -->
	<Node key="gui">
		<Entry key="style" type="QString" default="fusion"/>
		<Node key="mainwindow">
			<Entry key="geometry" type="QByteArray"/>
			<Entry key="state" type="QByteArray"/>
		</Node>
		<!-- The default value of entries can be translated -->
		<!-- The value of the "ts" attribute serves as the context -->
		<Entry key="title" type="QString" default="Hello World!" ts="MainWindow"/>
	</Node>

	<!-- Entries can also contain other nodes -->
	<Entry key="generator" type="bool" default="true">
		<Node key="sources">
			<Entry key="normal" type="QString"/>
			<Entry key="extended" type="QString"/>
		</Node>
		<Entry key="timeout" type="int" default="5000"/>
	</Entry>

	<!-- Furthermore you can include C++ code for defaults that cannot easily be represented as a string -->
	<Entry key="myType" type="MyType">
		<Code>
			MyType {true, 42, MyType::someFunc("test")}
		</Code>
	</Entry>
</Settings>
```
