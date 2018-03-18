INCLUDEPATH += $$PWD

qtHaveModule(mvvmcore): QT += mvvmcore

HEADERS += \
	$$PWD/isettingsaccessor.h \
	$$PWD/qsettingsaccessor.h \
	$$PWD/settingsentry.h

SOURCES += \
	$$PWD/qsettingsaccessor.cpp

TRANSLATIONS +=

include($$PWD/qsettingsgenerator.prc)
