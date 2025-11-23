# Star-system-generator
PyQt6 Application for Generating, Visualizing and Managing Star Systems

Overview

Star System Generator is an interactive PyQt6 application that visualizes star systems, allows generation of random planetary systems, displays detailed information about each planet, stores systems in an SQLite database, and supports import/export using CSV files.

The visualization includes moving planets, orbits, satellites, and a clickable central star.
The application is fully offline, lightweight, and modular.

# Features
# Visualization

Static star system view using QPainter

Circular planet icons using masks

Realistic orbital motion (smooth animation)

Clickable planets and central star

Background starfield effect

# Planet Details

Temperature

Radius

Mass

Atmosphere

Planet type

Life probability

Satellites

Description

Planet image (editable by user)

# System Management

Built-in Solar System (auto-loaded)

Random system generation (4–8 planets)

Switching between systems through the menu

# Database (SQLite)

Two linked tables:

systems

system name

star name

temperature, radius, type

planet count

planets

belongs to system

all planet parameters stored separately

All systems are stored permanently.

# Import / Export

Save selected system to CSV

Load system from CSV

Automatic validation and path correction

# Interface

Light/Dark themes

Responsive layout

Clean UI written manually (no Qt Designer)

# Installation
1. Install Python 3.10+
2. Install dependencies:
pip install -r requirements.txt

(only PyQt6 is required)

# Build EXE

pyinstaller main.py --noconsole --onefile --name StarSystemGenerator

# Run:
python main.py or star_system_generator.exe file

//

Star System Generator — интерактивное приложение на PyQt6 для генерации и визуализации звёздных систем.
Позволяет создавать случайные планетные системы, просматривать подробную информацию о каждой планете, сохранять и загружать системы, а также автоматически хранит данные в базе SQLite.

Приложение полностью автономное, не требует интернета и работает на любом ПК.

# Возможности
# Визуализация

Рисование системы через QPainter

Круглые изображения планет

Движение планет по орбитам

Нажатие на планеты и звезду

Фон “звёздного неба”

# Информация о планетах

Температура

Размер

Масса

Атмосфера

Тип планеты

Вероятность жизни

Кол-во спутников

Описание

Возможность смены картинки

# Управление системами

Готовая Солнечная система

Генерация случайных систем

Переключение между системами через меню

# База данных SQLite

Хранятся две таблицы:

systems — данные о звёздных системах

planets — данные о планетах каждой системы

Все данные сохраняются навсегда.

# Импорт / Экспорт CSV

Сохранение системы в CSV

Загрузка системы из CSV

Автоматическая проверка корректности данных

# Интерфейс

Светлая и тёмная тема

Аккуратные виджеты

Компоновка без Qt Designer

# Установка
1. Установить Python 3.10+
2. Установить зависимости:
pip install -r requirements.txt

# Сборка EXE

pyinstaller main.py --noconsole --onefile --name StarSystemGenerator

# Запустить:
python main.py или star_system_generator.exe файл
