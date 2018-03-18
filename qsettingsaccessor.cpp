#include "qsettingsaccessor.h"
#include <QCoreApplication>
#ifdef QT_MVVMCORE_LIB
#include <QtMvvmCore/ServiceRegistry>
#endif

namespace {

void setupDefaultAccessor()
{
#ifdef QT_MVVMCORE_LIB
	QtMvvm::registerInterfaceConverter<ISettingsAccessor>();
	QtMvvm::ServiceRegistry::instance()->registerInterface<ISettingsAccessor, QSettingsAccessor>(true);
#endif
}

}
Q_COREAPP_STARTUP_FUNCTION(setupDefaultAccessor)

QSettingsAccessor::QSettingsAccessor(QObject *parent) :
	QSettingsAccessor(new QSettings(), parent)
{}

QSettingsAccessor::QSettingsAccessor(QSettings *settings, QObject *parent) :
	QObject(parent),
	_settings(settings)
{
	_settings->setParent(this);
}

QVariant QSettingsAccessor::load(const QString &key, const QVariant &defaultValue)
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
