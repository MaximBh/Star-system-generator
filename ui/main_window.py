from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout,
    QMenuBar, QMenu, QFileDialog, QPushButton,
    QDialog, QVBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QTabWidget
)
from PyQt6.QtGui import QAction
from core.generator import SystemManager
from core.database import get_connection
from ui.star_system_view import SystemView
from ui.planet_info_widget import PlanetInfoWidget

# темы
LIGHT_THEME = """
QWidget { background-color: #eaf2ff; color: #111; font-size: 15px; }
QPushButton { background-color: #d7e6ff; border-radius: 8px; padding: 6px 10px; }
QMenuBar, QMenu { background-color: #cddfff; }
"""
DARK_THEME = """
QWidget { background-color: #0b1220; color: #e8eef8; font-size: 15px; }
QPushButton { background-color: #263244; color: #fff; border-radius: 8px; padding: 6px 10px; }
QMenuBar, QMenu { background-color: #0a1526; color: #e8eef8; }
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Star System Generator")
        self.resize(1250, 1250)

        self.manager = SystemManager()

        # центральная компоновка
        central = QWidget()
        self.setCentralWidget(central)
        self.v = QVBoxLayout(central)

        # панель кнопок
        bar = QHBoxLayout()
        self.btn_generate = QPushButton("Сгенерировать систему")
        self.btn_theme = QPushButton("Сменить тему")
        bar.addWidget(self.btn_generate)
        bar.addWidget(self.btn_theme)
        bar.addStretch()
        self.v.addLayout(bar)

        # вид системы
        self.system_view = SystemView(
            self.manager,
            show_planet_callback=self.show_planet_info,
            show_star_callback=self.show_star_info
        )
        # вид инфо
        self.info_view = PlanetInfoWidget(self.manager, back_callback=self.back_to_system)

        self.v.addWidget(self.system_view)
        self.v.addWidget(self.info_view)
        self.info_view.hide()

        # меню
        self._build_menu()

        # события
        self.btn_generate.clicked.connect(self.on_generate)
        self.btn_theme.clicked.connect(self.toggle_theme)

        # тема по умолчанию
        self.dark_mode = True
        self.apply_theme()

    # Построение меню

    def _build_menu(self):
        mb = QMenuBar(self)
        self.setMenuBar(mb)

        # Меню "Файл"
        file_menu = QMenu("Файл", self)
        mb.addMenu(file_menu)

        act_save = QAction("Сохранить в CSV", self)
        act_load = QAction("Импорт из CSV", self)
        act_load_db = QAction("Загрузить все системы из БД", self)
        act_clear_db = QAction("Очистить базу данных", self)
        act_clear_list = QAction("Очистить список систем", self)
        act_show_db = QAction("Показать данные в БД", self)
        act_exit = QAction("Выход", self)

        file_menu.addActions([
            act_save, act_load, act_load_db,
            act_clear_db, act_clear_list, act_show_db
        ])
        file_menu.addSeparator()
        file_menu.addAction(act_exit)

        act_save.triggered.connect(self.on_save_csv)
        act_load.triggered.connect(self.on_load_csv)
        act_load_db.triggered.connect(self.on_load_all_from_db)
        act_clear_db.triggered.connect(self.on_clear_db)
        act_clear_list.triggered.connect(self.on_clear_list)
        act_show_db.triggered.connect(self.show_database_contents)
        act_exit.triggered.connect(self.close)

        # Меню "Система"
        self.system_menu = QMenu("Система", self)
        mb.addMenu(self.system_menu)
        self.rebuild_system_menu()

    def rebuild_system_menu(self):
        """Пересобирает меню 'Система' — без дублей, Солнечная всегда первая."""
        self.system_menu.clear()

        # сортируем — чтобы Солнечная всегда была первой
        systems_sorted = sorted(
            self.manager.systems,
            key=lambda s: 0 if s.name.strip().lower() in ("солнечная система", "солнечная") else 1
        )

        # пересобираем меню
        for idx, system in enumerate(systems_sorted):
            title = "Солнечная" if system.name.strip().lower() in ("солнечная система", "солнечная") else system.name
            act = QAction(title, self)
            act.triggered.connect(lambda _, i=self.manager.systems.index(system): self.switch_system(i))
            self.system_menu.addAction(act)

    # Основные функции

    def on_generate(self):
        """Создание новой случайной системы."""
        new_system = self.manager.generate_random_system()
        self.rebuild_system_menu()
        self.system_view.refresh_system()
        QMessageBox.information(self, "Успех", f"Система '{new_system.name}' создана и сохранена в БД.")

    def on_save_csv(self):
        """Сохранение текущей системы в CSV."""
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить систему", "", "CSV Files (*.csv)")
        if path:
            try:
                self.manager.save_system_to_csv(path)
                QMessageBox.information(self, "Успех", f"Система '{self.manager.system.name}' сохранена в файл CSV.")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", str(e))

    def on_load_csv(self):
        """Импорт системы из CSV."""
        path, _ = QFileDialog.getOpenFileName(self, "Выбрать CSV", "", "CSV Files (*.csv)")
        if path:
            try:
                sys_obj = self.manager.load_system_from_csv(path)
                self.manager.save_system_to_db(sys_obj)
                self.rebuild_system_menu()
                QMessageBox.information(self, "Успех", f"Система '{sys_obj.name}' импортирована и добавлена в БД.")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", str(e))

    def on_load_all_from_db(self):
        """Загрузка всех систем из базы данных."""
        try:
            systems = self.manager.load_all_systems_from_db()
            if not systems:
                QMessageBox.information(self, "Информация", "База данных пуста.")
            else:
                self.manager.systems = systems
                self.manager.current_index = 0
                self.rebuild_system_menu()
                self.system_view.refresh_system()
                QMessageBox.information(self, "Успех", f"Загружено {len(systems)} систем из базы данных.")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить системы: {e}")

    def on_clear_db(self):
        """Очистка базы данных."""
        reply = QMessageBox.question(self, "Подтверждение", "Удалить все данные из базы данных?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("DELETE FROM planets")
                cur.execute("DELETE FROM systems")
                conn.commit()
                conn.close()
                QMessageBox.information(self, "Готово", "База данных очищена.")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось очистить базу: {e}")

    def on_clear_list(self):
        """Очищает список систем, оставляя только Солнечную."""
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Очистить все системы, кроме Солнечной?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            # очищаем данные у менеджера
            self.manager.clear_system_list()

            # обновляем визуально
            self.rebuild_system_menu()
            self.system_view.refresh_system()
            self.info_view.hide()
            self.system_view.show()

            QMessageBox.information(
                self,
                "Готово",
                "Список систем очищен.\nОставлена только Солнечная система."
            )

    def go_to_solar(self):
        """Перейти к существующей Солнечной системе, иначе создать её один раз."""
        solar_idx = None
        for i, s in enumerate(self.manager.systems):
            if s.name.strip().lower() in ("солнечная система", "солнечная"):
                solar_idx = i
                break

        if solar_idx is not None:
            self.switch_system(solar_idx)
            return

        # если нет — создаём один раз и добавляем
        solar = self.manager.load_solar_system()
        try:
            self.manager.save_system_to_db(solar)
        except Exception as e:
            print(f"[WARN] Не удалось сохранить Солнечную в БД: {e}")
        self.manager.add_system(solar, make_current=True)
        self.rebuild_system_menu()
        self.system_view.refresh_system()

    def show_database_contents(self):
        """Показать реальные данные из таблиц 'systems' и 'planets'."""
        try:
            conn = get_connection()
            cur = conn.cursor()

            # Считываем обе таблицы
            cur.execute("SELECT * FROM systems")
            systems_data = cur.fetchall()
            systems_columns = [desc[0] for desc in cur.description]

            cur.execute("SELECT * FROM planets")
            planets_data = cur.fetchall()
            planets_columns = [desc[0] for desc in cur.description]

            conn.close()

            dialog = QDialog(self)
            dialog.setWindowTitle("Данные в БД")
            dialog.resize(1200, 700)
            layout = QVBoxLayout(dialog)
            layout.addWidget(QLabel("Содержимое БД:"))

            tabs = QTabWidget()
            layout.addWidget(tabs)

            # Таблица systems
            sys_table = QTableWidget()
            sys_table.setColumnCount(len(systems_columns))
            sys_table.setHorizontalHeaderLabels(systems_columns)
            sys_table.setRowCount(len(systems_data))
            for i, row in enumerate(systems_data):
                for j, val in enumerate(row):
                    sys_table.setItem(i, j, QTableWidgetItem(str(val)))
            sys_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            tabs.addTab(sys_table, "Системы")

            # Таблица planets
            pl_table = QTableWidget()
            pl_table.setColumnCount(len(planets_columns))
            pl_table.setHorizontalHeaderLabels(planets_columns)
            pl_table.setRowCount(len(planets_data))
            for i, row in enumerate(planets_data):
                for j, val in enumerate(row):
                    pl_table.setItem(i, j, QTableWidgetItem(str(val)))
            pl_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            tabs.addTab(pl_table, "Планеты")

            dialog.setLayout(layout)
            dialog.exec()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные из базы:\n{e}")

    def toggle_theme(self):
        """Смена темы."""
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_theme(self):
        """Применяет текущую тему."""
        self.setStyleSheet(DARK_THEME if self.dark_mode else LIGHT_THEME)

    def switch_system(self, index: int):
        """Переключение между системами."""
        self.manager.switch_to(index)
        self.system_view.refresh_system()
        self.info_view.hide()
        self.system_view.show()

    def show_planet_info(self, idx: int):
        """Показ информации о планете."""
        self.info_view.set_planet(idx)
        self.system_view.hide()
        self.info_view.show()

    def show_star_info(self):
        """Показ информации о звезде."""
        self.info_view.set_star()
        self.system_view.hide()
        self.info_view.show()

    def back_to_system(self):
        """Возврат к отображению системы."""
        self.info_view.hide()
        self.system_view.show()
