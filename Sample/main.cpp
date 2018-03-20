#include <QCoreApplication>
#include "mytype.h"
#include "settings.h"
#include <QDebug>

int main(int argc, char *argv[])
{
	QCoreApplication a(argc, argv);
	qRegisterMetaTypeStreamOperators<MyType>();

	//access the settings values for reading, without and with default values
	qDebug() << "gui.mainwindow.geometry:"
			 << Settings::instance()->gui.mainwindow.geometry.isSet()
			 << Settings::instance()->gui.mainwindow.geometry.get();
	qDebug() << "gui.title:"
			 << Settings::instance()->gui.title.isSet()
			 << (QString)Settings::instance()->gui.title;

	//write and reset values
	Settings::instance()->gui.style = QStringLiteral("Premium");
	QString styleNow = Settings::instance()->gui.style;
	Settings::instance()->gui.style.reset();
	QString styleReset = Settings::instance()->gui.style;
	qDebug() << "gui.style (written and resetted):"
			 << styleNow
			 << styleReset
			 << Settings::instance()->gui.style.isSet();

	// entry with sub elements can be used just the same way
	if(!Settings::instance()->generator.isSet()) {
		Settings::instance()->generator = false;
		Settings::instance()->generator.timeout = 42;
	}
	qDebug() << "generator.*:"
			 << Settings::instance()->generator.get()
			 << (int)Settings::instance()->generator.timeout;

	//Entry with a customd datatype
	//read
	MyType myType = Settings::instance()->myType;
	qDebug() << "myType default:"
			 << myType.doIt
			 << myType.when
			 << myType.stuff;
	//write
	myType.when = 666;
	Settings::instance()->myType = myType;
	myType = Settings::instance()->myType;
	qDebug() << "myType written:"
			 << myType.doIt
			 << myType.when
			 << myType.stuff;
	//reset
	Settings::instance()->myType.reset();

	return 0;
}
