#include "mytype.h"

MyType::MyType(bool, int, QByteArray) {}

QByteArray MyType::someFunc(const char *text)
{
	return QByteArray(text).toBase64();
}
