#include "qsettingsaccessor.h"
#include <QCoreApplication>
#ifdef QT_MVVMCORE_LIB
#include <QtMvvmCore/ServiceRegistry>
#endif

QSettingsAccessor::QSettingsAccessor(QObject *parent) :
	QSettingsAccessor(new QSettings(), parent)
{}

QSettingsAccessor::QSettingsAccessor(QSettings *settings, QObject *parent) :
	QObject(parent),
	ISettingsAccessor(),
	_settings(settings)
{
	_settings->setParent(this);
}

bool QSettingsAccessor::contains(const QString &key) const
{
	return _settings->contains(key);
}

QVariant QSettingsAccessor::load(const QString &key, const QVariant &defaultValue) const
{
	return _settings->value(key, defaultValue);
}

void QSettingsAccessor::save(const QString &key, const QVariant &value)
{
	_settings->setValue(key, value);
}

void QSettingsAccessor::remove(const QString &key)
{
	_settings->remove(key);
}
