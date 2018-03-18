DISTFILES += \
	$$PWD/generator.py

DISTFILES += $$SETTINGS_GENERATORS \
	$$MVVM_SETTINGS_FILES

isEmpty(SETTINGSGENERATOR_DIR):SETTINGSGENERATOR_DIR = .
isEmpty(MOC_DIR):MOC_DIR = .

debug_and_release {
	CONFIG(debug, debug|release):SUFFIX = /debug
	CONFIG(release, debug|release):SUFFIX = /release
}

SETTINGSGENERATOR_DIR = $$SETTINGSGENERATOR_DIR$$SUFFIX

settingsgenerator_c.name = generator.py ${QMAKE_FILE_IN}
settingsgenerator_c.input = SETTINGS_GENERATORS
settingsgenerator_c.variable_out = SETTINGSGENERATOR_HEADERS
settingsgenerator_c.commands = $$PWD/generator.py ${QMAKE_FILE_IN} ${QMAKE_FILE_OUT} $$SETTINGSGENERATOR_DIR/${QMAKE_FILE_BASE}$${first(QMAKE_EXT_CPP)} $$MVVM_SETTINGS_FILES
settingsgenerator_c.output = $$SETTINGSGENERATOR_DIR/${QMAKE_FILE_BASE}$${first(QMAKE_EXT_H)}
settingsgenerator_c.CONFIG += target_predeps
settingsgenerator_c.depends += $$PWD/generator.py

QMAKE_EXTRA_COMPILERS += settingsgenerator_c

settingsgenerator_m.name = generator.py moc ${QMAKE_FILE_IN}
settingsgenerator_m.input = SETTINGSGENERATOR_HEADERS
settingsgenerator_m.variable_out = GENERATED_SOURCES
settingsgenerator_m.commands = ${QMAKE_FUNC_mocCmdBase} ${QMAKE_FILE_IN} -o ${QMAKE_FILE_OUT}
settingsgenerator_m.output = $$MOC_DIR/$${QMAKE_H_MOD_MOC}${QMAKE_FILE_BASE}$${first(QMAKE_EXT_CPP)}
settingsgenerator_m.CONFIG += target_predeps
settingsgenerator_m.depends += $$WIN_INCLUDETEMP $$moc_predefs.output
settingsgenerator_m.dependency_type = TYPE_C

QMAKE_EXTRA_COMPILERS += settingsgenerator_m

settingsgenerator_s.name = generator.py cpp ${QMAKE_FILE_IN}
settingsgenerator_s.input = SETTINGSGENERATOR_HEADERS
settingsgenerator_s.variable_out = GENERATED_SOURCES
settingsgenerator_s.commands = $$escape_expand(\\n) # force creation of rule
settingsgenerator_s.output = $$SETTINGSGENERATOR_DIR/${QMAKE_FILE_BASE}$${first(QMAKE_EXT_CPP)}
settingsgenerator_s.CONFIG += target_predeps

QMAKE_EXTRA_COMPILERS += settingsgenerator_s
