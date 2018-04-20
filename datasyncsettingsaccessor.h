#ifndef DATASYNCSETTINGSGENERATOR_H
#define DATASYNCSETTINGSGENERATOR_H

#include <QObject>
#include <QtDataSync/CachingDataTypeStore>
#include "isettingsaccessor.h"

struct DataSyncSettingsEntry
{
	Q_GADGET

public:
	Q_PROPERTY(QString key MEMBER key USER true)
	Q_PROPERTY(QByteArray value MEMBER value)

	QString key;
	QByteArray value;
};

class DataSyncSettingsAccessor : public ISettingsAccessor
{
	Q_OBJECT
	Q_INTERFACES(ISettingsAccessor)

public:
	Q_INVOKABLE explicit DataSyncSettingsAccessor(QObject *parent = nullptr);
	explicit DataSyncSettingsAccessor(const QString &setup, QObject *parent = nullptr);

	bool contains(const QString &key) const override;
	QVariant load(const QString &key, const QVariant &defaultValue) const override;
	void save(const QString &key, const QVariant &value) override;
	void remove(const QString &key) override;

public Q_SLOTS:
	void sync() override;

private Q_SLOTS:
	void dataChanged(const QString &key, const QVariant &value);

private:
	QtDataSync::CachingDataTypeStore<DataSyncSettingsEntry> *_store;
};

#endif // DATASYNCSETTINGSGENERATOR_H
