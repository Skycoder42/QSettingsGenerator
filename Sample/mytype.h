#ifndef MYTYPE_H
#define MYTYPE_H

#include <QObject>
#include <QByteArray>
#include <QDataStream>

class MyType
{
public:
	MyType(bool doIt = {}, int when = {}, QByteArray stuff = {});

	static QByteArray someFunc(const char *text);

	bool doIt;
	int when;
	QByteArray stuff;
};

QDataStream &operator<<(QDataStream &stream, const MyType &type);
QDataStream &operator>>(QDataStream &stream, MyType &type);

Q_DECLARE_METATYPE(MyType)

#endif // MYTYPE_H
