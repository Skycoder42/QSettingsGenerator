#ifndef QSETTINGSACCESSOR_H
#define QSETTINGSACCESSOR_H

#include <QObject>
#include <QSettings>
#include "isettingsaccessor.h"

class QSettingsAccessor : public ISettingsAccessor
{
	Q_OBJECT
	Q_INTERFACES(ISettingsAccessor)

public:
	Q_INVOKABLE explicit QSettingsAccessor(QObject *parent = nullptr);
	explicit QSettingsAccessor(QSettings *settings, QObject *parent = nullptr);

	bool contains(const QString &key) const override;
	QVariant load(const QString &key, const QVariant &defaultValue) const override;
	void save(const QString &key, const QVariant &value) override;
	void remove(const QString &key) override;

public Q_SLOTS:
	void sync() override;

private:
	QSettings *_settings;
};

#endif // QSETTINGSACCESSOR_H
