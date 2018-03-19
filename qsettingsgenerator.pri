INCLUDEPATH += $$PWD

qtHaveModule(mvvmcore): QT += mvvmcore

HEADERS += \
	$$PWD/isettingsaccessor.h \
	$$PWD/settingsentry.h  \
	$$PWD/qsettingsaccessor.h

SOURCES += \
	$$PWD/qsettingsaccessor.cpp

qtHaveModule(datasync) {
	QT += datasync
	HEADERS += $$PWD/datasyncsettingsgenerator.h
	SOURCES += $$PWD/datasyncsettingsgenerator.cpp
}

TRANSLATIONS +=

include($$PWD/qsettingsgenerator.prc)
