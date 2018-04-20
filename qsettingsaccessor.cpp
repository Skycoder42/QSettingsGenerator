#include "qsettingsaccessor.h"
#include <QCoreApplication>
#include <QGlobalStatic>
#ifdef QT_MVVMCORE_LIB
#include <QtMvvmCore/ServiceRegistry>
#endif

QSettingsAccessor::QSettingsAccessor(QObject *parent) :
	QSettingsAccessor(new QSettings(), parent)
{}

QSettingsAccessor::QSettingsAccessor(QSettings *settings, QObject *parent) :
	ISettingsAccessor(parent),
	_settings(settings)
{
	_settings->setParent(this);
	connect(qApp, &QCoreApplication::aboutToQuit,
			this, &QSettingsAccessor::sync);
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
	emit entryChanged(key, value);
}

void QSettingsAccessor::remove(const QString &key)
{
	_settings->remove(key);
	emit entryRemoved(key);
}

void QSettingsAccessor::sync()
{
	_settings->sync();
}
