from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import (
    QPainter, QPen, QColor, QPixmap, QImage, QPainterPath, QRadialGradient
)
from PyQt6.QtCore import Qt, QRect, QTimer
import math
import random


class SystemView(QWidget):
    """
    Рендерит текущую систему из manager.system:
      фон со звездами
      центральная звезда
      орбиты
      планеты (круглые картинки) + маленькие спутники вокруг
    Планеты двигаются по орбитам.
    """

    def __init__(self, manager, show_planet_callback, show_star_callback, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.show_planet_callback = show_planet_callback
        self.show_star_callback = show_star_callback

        self.setMinimumHeight(480)

        # фон
        self._stars = self.generate_stars(240)

        # динамика: углы и скорости для планет (в град/кадр)
        self._angles = []
        self._speeds = []
        self.base_speed = 0.25  # базовая скорость (чем больше — тем быстрее вся система, )
        self._click_regions = []

        # таймер для анимации
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(15)  # ~60 FPS

        # инициализируем углы под текущую систему
        self.refresh_system()

    def _cache_images(self):
        """Кэширует изображения всех планет (один раз, при обновлении системы).
           Нужно для того, чтобы визуализация была более плавной и не лагала, если будут загружены картинки с высоким разрешением.
        """
        self._pixmap_cache = []
        sys = self.manager.system
        planet_size = 56
        for pl in sys.planets:
            if pl.image_path:
                img = QImage(pl.image_path)
                if not img.isNull():
                    pix = QPixmap.fromImage(img).scaled(
                        planet_size, planet_size,
                        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    rounded = QPixmap(planet_size, planet_size)
                    rounded.fill(Qt.GlobalColor.transparent)
                    rp = QPainter(rounded)
                    rp.setRenderHint(QPainter.RenderHint.Antialiasing)
                    path = QPainterPath()
                    path.addEllipse(0, 0, planet_size, planet_size)
                    rp.setClipPath(path)
                    rp.drawPixmap(0, 0, pix)
                    rp.end()
                    self._pixmap_cache.append(rounded)
                    continue
            # если нет картинки
            self._pixmap_cache.append(None)

    def refresh_system(self):
        """Обновление системы, чтобы планеты двигались."""
        sys = self.manager.system
        n = len(sys.planets)
        self._angles = []
        self._speeds = []
        for i, p in enumerate(sys.planets):
            self._angles.append((45 + i * 360.0 / max(1, n)) % 360.0)
            period = max(1.0, float(p.orbital_period_days))
            speed = self.base_speed * 365.0 / period
            speed = max(0.05, min(speed, 2.0))
            self._speeds.append(speed)
        self._stars = self.generate_stars(260)
        self._cache_images()
        self.update()

    def generate_stars(self, count):
        """Создание звезд."""
        stars = []
        w = max(900, self.width() or 900)
        h = max(600, self.height() or 600)
        for _ in range(count):
            stars.append((random.randint(0, w), random.randint(0, h), random.choice([1, 2, 3])))
        return stars

    def resizeEvent(self, event):
        self._stars = self.generate_stars(260)
        super().resizeEvent(event)

    def tick(self):
        """Обновление углов."""
        if not self._angles or not self._speeds:
            return
        self._angles = [(a + s) % 360.0 for a, s in zip(self._angles, self._speeds)]
        self.update()

    def paintEvent(self, event):
        """Создание системы."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # фон
        painter.fillRect(self.rect(), QColor(6, 10, 20))

        # звезды на фоне
        for x, y, size in self._stars:
            c = QColor(255, 255, 255, 200 if size == 1 else 150 if size == 2 else 100)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(c)
            painter.drawEllipse(x, y, size, size)

        # центральная звезда
        center = self.rect().center()
        star_r = 30

        glow = QRadialGradient(center.x(), center.y(), star_r * 4)
        glow.setColorAt(0.0, QColor(255, 220, 120, 220))
        glow.setColorAt(0.5, QColor(255, 180, 80, 120))
        glow.setColorAt(1.0, QColor(255, 180, 80, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(glow)
        painter.drawEllipse(center.x() - star_r * 4, center.y() - star_r * 4, star_r * 8, star_r * 8)

        painter.setBrush(QColor(255, 200, 80))
        painter.drawEllipse(center.x() - star_r, center.y() - star_r, star_r * 2, star_r * 2)

        # орбиты и планеты
        sys = self.manager.system
        base_orbit = 90
        gap = 55
        planet_size = 56

        click_regions = []
        # область клика звезды
        star_rect = QRect(center.x() - star_r, center.y() - star_r, star_r * 2, star_r * 2)
        click_regions.append((star_rect, 'star', None))

        for idx, pl in enumerate(sys.planets):
            # орбита
            r = base_orbit + idx * gap
            pen = QPen(QColor(130, 140, 150, 170))
            pen.setWidth(1)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(center, r, r)

            # позиция планеты по углу
            angle_deg = self._angles[idx] if idx < len(self._angles) else (45 + idx * 40)
            rad = math.radians(angle_deg)
            x = center.x() + r * math.cos(rad)
            y = center.y() + r * math.sin(rad)

            # изображения
            if hasattr(self, "_pixmap_cache") and idx < len(self._pixmap_cache) and self._pixmap_cache[idx]:
                pix = self._pixmap_cache[idx]
                painter.drawPixmap(int(x - planet_size / 2), int(y - planet_size / 2), pix)
            else:
                # простая серая планета
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(200, 200, 200))
                painter.drawEllipse(int(x - 12), int(y - 12), 24, 24)

            # подпись
            painter.setPen(QColor(220, 220, 220))
            painter.drawText(int(x + 18), int(y + 6), pl.name)

            # спутники
            sat_count = max(0, int(pl.satellites))
            for s in range(sat_count):
                sat_angle = math.radians((angle_deg * 2 + 360 / max(1, sat_count) * s) % 360)
                sat_r = 18
                sx = x + sat_r * math.cos(sat_angle)
                sy = y + sat_r * math.sin(sat_angle)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(180, 180, 200))
                painter.drawEllipse(int(sx - 3), int(sy - 3), 6, 6)

            # кликабельная область планеты
            rect = QRect(int(x - planet_size / 2), int(y - planet_size / 2), planet_size, planet_size)
            click_regions.append((rect, 'planet', idx))

        self._click_regions = click_regions

    def mousePressEvent(self, event):
        """Обработка клика на объект через положение курсора и объекта."""
        pt = event.position()
        for rect, obj_type, idx in getattr(self, "_click_regions", []):
            if rect.contains(int(pt.x()), int(pt.y())):
                if obj_type == 'planet':
                    self.show_planet_callback(idx)
                elif obj_type == 'star':
                    self.show_star_callback()
                return
        super().mousePressEvent(event)
