#include "datasyncsettingsaccessor.h"
#include <QDataStream>
#include <QMetaProperty>
#include <QDebug>

DataSyncSettingsAccessor::DataSyncSettingsAccessor(QObject *parent) :
	DataSyncSettingsAccessor(QtDataSync::DefaultSetup, parent)
{}

DataSyncSettingsAccessor::DataSyncSettingsAccessor(const QString &setup, QObject *parent) :
	QObject(parent),
	ISettingsAccessor(),
	_store(new QtDataSync::CachingDataTypeStore<DataSyncSettingsEntry>(setup, this))
{}

bool DataSyncSettingsAccessor::contains(const QString &key) const
{
	return _store->contains(key);
}

QVariant DataSyncSettingsAccessor::load(const QString &key, const QVariant &defaultValue) const
{
	if(_store->contains(key)) {
		QVariant value;
		{
			auto data = _store->load(key).value;
			QDataStream stream(data);
			stream >> value;
		}
		return value;
	} else
		return defaultValue;
}

void DataSyncSettingsAccessor::save(const QString &key, const QVariant &value)
{
	try {
		QByteArray data;
		{
			QDataStream stream(&data, QIODevice::WriteOnly);
			stream << value;
		}
		_store->save({key, data});
	} catch (QException &e) {
		qCritical() << "Failed to save entry" << key << "to datasync settings with error:"
					<< e.what();
	}
}

void DataSyncSettingsAccessor::remove(const QString &key)
{
	try {
		_store->remove(key);
	} catch (QException &e) {
		qCritical() << "Failed to remove entry" << key << "from datasync settings with error:"
					<< e.what();
	}
}
