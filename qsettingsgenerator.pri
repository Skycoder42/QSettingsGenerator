INCLUDEPATH += $$PWD

qpmx_static: message(configured for qpmx build)
else: message(configured for source build)

HEADERS += \
	$$PWD/isettingsaccessor.h \
	$$PWD/qsettingsaccessor.h \
	$$PWD/settingsentry.h

SOURCES += \
	$$PWD/qsettingsaccessor.cpp

TRANSLATIONS +=

include($$PWD/qsettingsgenerator.prc)
