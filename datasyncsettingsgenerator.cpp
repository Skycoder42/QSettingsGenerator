#include "datasyncsettingsgenerator.h"
#include <QDataStream>
#include <QMetaProperty>
#include <QDebug>

DataSyncSettingsGenerator::DataSyncSettingsGenerator(QObject *parent) :
	DataSyncSettingsGenerator(QtDataSync::DefaultSetup, parent)
{}

DataSyncSettingsGenerator::DataSyncSettingsGenerator(const QString &setup, QObject *parent) :
	QObject(parent),
	ISettingsAccessor(),
	_store(new QtDataSync::CachingDataTypeStore<DataSyncSettingsEntry>(setup, this))
{}

bool DataSyncSettingsGenerator::contains(const QString &key) const
{
	return _store->contains(key);
}

QVariant DataSyncSettingsGenerator::load(const QString &key, const QVariant &defaultValue) const
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

void DataSyncSettingsGenerator::save(const QString &key, const QVariant &value)
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

void DataSyncSettingsGenerator::remove(const QString &key)
{
	try {
		_store->remove(key);
	} catch (QException &e) {
		qCritical() << "Failed to remove entry" << key << "from datasync settings with error:"
					<< e.what();
	}
}
