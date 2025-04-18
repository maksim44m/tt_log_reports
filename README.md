# Log Report Generator

Утилита для анализа логов Django приложения.

## Подготовка

Загрузите файлы логов в папку `logs`

## Использование

```bash
python main.py logs/app1.log logs/app2.log logs/app3.log --report handlers
```

## Параметры

- `logs` - один или несколько путей к лог-файлам
- `--report` - тип отчета (handlers) 

## Добавление нового отчета

1. Создайте новый класс, наследующий `BaseReport`

2. Зарегистрируйте отчет в `ReportFactory`:
```python
class ReportFactory:
    _reports = {
        'handlers': HandlersReport,
        'my_report': MyReport,  # Добавьте свой отчет
    }
```

3. Используйте новый отчет:
```bash
python main.py logs/new_log.log --report my_report
``` 
