#ifndef SETTINGSENTRY_H
#define SETTINGSENTRY_H

#include "isettingsaccessor.h"

template <typename T>
class SettingsEntry
{
	Q_DISABLE_COPY(SettingsEntry)

public:
	T get() const;
	void set(T value);
	void reset();

	SettingsEntry<T> &operator=(T value);
	operator T() const;

	// internal
	void setup(const QString &key, ISettingsAccessor *accessor, const QVariant &defaultValue = {});

private:
	QString _key;
	ISettingsAccessor *_accessor = nullptr;
	QVariant _default;
};

template <>
class SettingsEntry<void>
{
	Q_DISABLE_COPY(SettingsEntry)

public:
	// internal
	void setup(const QString &key, ISettingsAccessor *accessor, const QVariant &defaultValue = {});
};


// ------------- Generic Implementation -------------

template<typename T>
T SettingsEntry<T>::get() const
{
	return _accessor->load(_key, _default).template value<T>();
}

template<typename T>
void SettingsEntry<T>::set(T value)
{
	_accessor->save(_key, QVariant::fromValue(value));
}

template<typename T>
void SettingsEntry<T>::reset()
{
	_accessor->remove(_key);
}

template<typename T>
SettingsEntry<T> &SettingsEntry<T>::operator=(T value)
{
	set(value);
	return (*this);
}
template<typename T>
SettingsEntry<T>::operator T() const
{
	return get();
}

template<typename T>
void SettingsEntry<T>::setup(const QString &key, ISettingsAccessor *accessor, const QVariant &defaultValue)
{
	Q_ASSERT_X(accessor, Q_FUNC_INFO, "You must set a valid accessor before initializing the settings!");
	_key  = key;
	_accessor = accessor;
	_default = defaultValue;
}

template<>
void SettingsEntry<void>::setup(const QString &, ISettingsAccessor *, const QVariant &) {}


#endif // SETTINGSENTRY_H
