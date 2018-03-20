INCLUDEPATH += $$PWD

qtHaveModule(mvvmcore): QT += mvvmcore

HEADERS += \
	$$PWD/isettingsaccessor.h \
	$$PWD/settingsentry.h  \
	$$PWD/qsettingsaccessor.h \
    $$PWD/datasyncsettingsaccessor.h

SOURCES += \
	$$PWD/qsettingsaccessor.cpp \
    $$PWD/datasyncsettingsaccessor.cpp

qtHaveModule(datasync) {
	QT += datasync
	HEADERS +=
	SOURCES +=
}

TRANSLATIONS +=

include($$PWD/qsettingsgenerator.prc)
