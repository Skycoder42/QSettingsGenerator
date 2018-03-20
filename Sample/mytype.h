#ifndef MYTYPE_H
#define MYTYPE_H

#include <QObject>
#include <QByteArray>

class MyType
{
public:
	MyType(bool = {}, int = {}, QByteArray = {});

	static QByteArray someFunc(const char *text);
};

Q_DECLARE_METATYPE(MyType)

#endif // MYTYPE_H
