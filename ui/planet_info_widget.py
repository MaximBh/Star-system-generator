from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPainterPath, QColor
from PyQt6.QtCore import Qt


class PlanetInfoWidget(QWidget):
    def __init__(self, manager, back_callback, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.back_callback = back_callback
        self.current_index = None
        self.is_star = False
        self._build_ui()

    def _build_ui(self):
        # изображение
        self.img = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.img.setFixedSize(360, 360)

        # текст
        self.info = QLabel(alignment=Qt.AlignmentFlag.AlignTop)
        self.info.setWordWrap(True)
        font = self.info.font()
        font.setPointSize(font.pointSize() + 2)
        self.info.setFont(font)

        # кнопки
        self.btn_change = QPushButton("Изменить картинку")
        self.btn_back = QPushButton("Назад")

        self.btn_change.clicked.connect(self.change_image)
        self.btn_back.clicked.connect(self.back_callback)

        # расположение кнопок
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.btn_change)
        buttons_layout.addSpacing(12)
        buttons_layout.addWidget(self.btn_back)
        buttons_layout.addStretch()

        # рамположение интерфейса
        content_layout = QHBoxLayout()
        content_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        content_layout.addStretch()
        content_layout.addWidget(self.img)
        content_layout.addSpacing(30)
        content_layout.addWidget(self.info, stretch=1)
        content_layout.addStretch()

        main = QVBoxLayout(self)
        main.addStretch()
        main.addLayout(content_layout)
        main.addSpacing(25)
        main.addLayout(buttons_layout)
        main.addStretch()

    def set_planet(self, idx: int):
        """Установка планеты."""
        self.is_star = False
        self.current_index = idx
        self.refresh()

    def set_star(self):
        """Установка центральной звезды."""
        self.is_star = True
        self.current_index = None
        self.refresh()

    def refresh(self):
        """Информация о планете / звезде."""
        sys = self.manager.system
        if self.is_star:
            t = (
                f"Звезда: {sys.star_name}\n"
                f"Тип: {sys.star_type}\n"
                f"Температура: {sys.star_temperature_k} K\n"
                f"Радиус: {sys.star_radius_solar} R☉\n"
                f"Система: {sys.name}\n\n"
                f"Центральный источник света и тепла."
            )
            # рисуем круглую иконку звезды
            size_px = self.img.width()
            pix = QPixmap(size_px, size_px)
            pix.fill(Qt.GlobalColor.transparent)
            p = QPainter(pix)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            path = QPainterPath()
            path.addEllipse(0, 0, size_px, size_px)
            p.setClipPath(path)
            p.setBrush(QColor(255, 200, 80))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(0, 0, size_px, size_px)
            p.end()
            self.img.setPixmap(pix)
            self.info.setText(t)
            self.btn_change.setEnabled(False)
            return

        if not (0 <= self.current_index < len(sys.planets)):
            return
        pl = sys.planets[self.current_index]

        # если не звезда
        if pl.image_path:
            img = QImage(pl.image_path)
            if not img.isNull():
                size_px = self.img.width()
                pix = QPixmap.fromImage(img).scaled(
                    size_px, size_px,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation
                )
                rounded = QPixmap(size_px, size_px)
                rounded.fill(Qt.GlobalColor.transparent)
                rp = QPainter(rounded)
                rp.setRenderHint(QPainter.RenderHint.Antialiasing)
                path = QPainterPath()
                path.addEllipse(0, 0, size_px, size_px)
                rp.setClipPath(path)
                rp.drawPixmap(0, 0, pix)
                rp.end()
                self.img.setPixmap(rounded)
            else:
                self.img.setText("[нет изображения]")
        else:
            self.img.setText("[нет изображения]")

        txt = (
            f"Имя: {pl.name}\n"
            f"Тип: {pl.planet_type}\n"
            f"Температура: {pl.temperature_c} °C\n"
            f"Радиус: {pl.size_earth} R⊕\n"
            f"Масса: {pl.mass_earth} M⊕\n"
            f"Орбитальный радиус: {pl.orbital_radius_au} AU\n"
            f"Период обращения: {pl.orbital_period_days} дней\n"
            f"Атмосфера: {pl.atmosphere}\n"
            f"Вероятность жизни: {pl.life_probability:.1f}%\n"
            f"Спутники: {pl.satellites}\n"
            f"Описание: {pl.description}\n"
        )
        self.info.setText(txt)
        self.btn_change.setEnabled(True)

    def change_image(self):
        """Изменить картинку планеты."""
        if self.is_star:
            return
        path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение планеты", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            pl = self.manager.system.planets[self.current_index]
            pl.image_path = path
            self.refresh()
