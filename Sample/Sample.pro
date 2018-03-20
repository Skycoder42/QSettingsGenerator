QT -= gui

CONFIG += c++14 console
CONFIG -= app_bundle

include(../qsettingsgenerator.pri)

SOURCES += main.cpp \
	mytype.cpp

SETTINGS_GENERATORS += \
	settings.xml

HEADERS += \
	mytype.h

QT -= mvvmcore
