from dataclasses import dataclass


@dataclass
class Planet:
    """Данные для одной планеты."""
    name: str  # название
    temperature_c: float  # температура
    size_earth: float  # радиус в единицах радиуса Земли
    mass_earth: float  # масса в массах Земли
    orbital_radius_au: float  # радиус орбиты в а.е.
    orbital_period_days: float  # период обращения (в условных единицах)
    planet_type: str  # тип
    atmosphere: str  # тип атмосферы
    life_probability: float  # 0..100 %
    satellites: int  # кол - во спутников
    image_path: str = ""  # путь к изображению
    description: str = ""  # краткое описание

    def generate_description(self):
        """Создаёт описание на основе типа и параметров."""
        desc_map = {
            "Каменистая": "Твёрдая планета с массивной поверхностью.",
            "Газовый гигант": "Огромный мир с мощной атмосферой.",
            "Ледяная": "Холодная планета с ледяной поверхностью.",
            "Пустынная": "Сухой мир с редкой атмосферой.",
            "Океаническая": "Планета, покрытая водой.",
        }
        base = desc_map.get(self.planet_type, "Необычный мир с загадками.")
        self.description = (f"{base} Средняя температура: {self.temperature_c}°C. "
                            f"Атмосфера: {self.atmosphere}.")
