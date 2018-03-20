#include "mytype.h"

MyType::MyType(bool doIt, int when, QByteArray stuff) :
	doIt(doIt),
	when(when),
	stuff(stuff)
{}

QByteArray MyType::someFunc(const char *text)
{
	return QByteArray(text).toBase64();
}

QDataStream &operator<<(QDataStream &stream, const MyType &type)
{
	stream << type.doIt
		   << type.when
		   << type.stuff;
	return stream;
}

QDataStream &operator>>(QDataStream &stream, MyType &type)
{
	stream >> type.doIt
		   >> type.when
		   >> type.stuff;
	return stream;
}
