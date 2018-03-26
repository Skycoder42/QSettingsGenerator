#ifndef ISETTINGSACCESSOR_H
#define ISETTINGSACCESSOR_H

#include <QObject>
#include <QString>
#include <QVariant>

class ISettingsAccessor
{
public:
	virtual inline ~ISettingsAccessor() = default;

	virtual bool contains(const QString &key) const = 0;
	virtual QVariant load(const QString &key, const QVariant &defaultValue = {}) const = 0;
	virtual void save(const QString &key, const QVariant &value) = 0;
	virtual void remove(const QString &key) = 0;

public Q_SLOTS:
	virtual void sync() = 0;
};

#define ISettingsAccessorIid "de.skycoder42.qsettingsgenerator.ISettingsAccessor"
Q_DECLARE_INTERFACE(ISettingsAccessor, ISettingsAccessorIid)
Q_DECLARE_METATYPE(ISettingsAccessor*)

#endif // ISETTINGSACCESSOR_H
