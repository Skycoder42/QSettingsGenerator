#ifndef QSETTINGSACCESSOR_H
#define QSETTINGSACCESSOR_H

#include <QObject>
#include <QSettings>
#include "isettingsaccessor.h"

class QSettingsAccessor : public QObject, public ISettingsAccessor
{
	Q_OBJECT
	Q_INTERFACES(ISettingsAccessor)

public:
	Q_INVOKABLE explicit QSettingsAccessor(QObject *parent = nullptr);
	explicit QSettingsAccessor(QSettings *settings, QObject *parent = nullptr);

	QVariant load(const QString &key, const QVariant &defaultValue) override;
	void save(const QString &key, const QVariant &value) override;
	void remove(const QString &key) override;

private:
	QSettings *_settings;
};

#endif // QSETTINGSACCESSOR_H
