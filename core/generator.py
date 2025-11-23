import random
import csv
from core.planet import Planet
from core.system import StarSystem
from core.database import init_db, get_connection


class SystemManager:
    """Управляет системами: генерация, загрузка, текущая."""

    def __init__(self, images_dir="data/planet_images"):
        """Инициализация менеджера систем и загрузка данных из БД."""
        self.images_dir = images_dir
        self.systems = []
        self.current_index = 0

        # Инициализируем базу данных (создаёт таблицы при первом запуске)
        init_db()

        try:
            # Пробуем загрузить все системы из базы данных
            loaded_systems = self.load_all_systems_from_db()
        except Exception as e:
            print(f"[WARN] Ошибка при чтении из базы: {e}")
            loaded_systems = []

        # Если БД пуста — создаём Солнечную систему
        if not loaded_systems:
            print("[INFO] База данных пуста — создаётся Солнечная система.")
            solar_system = self.load_solar_system()
            self.systems = [solar_system]
            self.current_index = 0
            try:
                self.save_system_to_db(solar_system)
                print("[INFO] Солнечная система успешно добавлена в базу данных.")
            except Exception as e:
                print(f"[WARN] Не удалось сохранить систему в базу: {e}")
        else:
            # Если что-то есть — используем загруженные системы
            self.systems = loaded_systems
            self.current_index = 0
            print(f"[INFO] Загружено систем из базы: {len(self.systems)}")

    @property
    def system(self):
        if not self.systems:
            raise IndexError("Нет систем.")
        return self.systems[self.current_index]

    def add_system(self, system, make_current=True):
        """Добавление системы."""
        self.systems.append(system)
        if make_current:
            self.current_index = len(self.systems) - 1

    def switch_to(self, index):
        """Переключиться на систему по индексу."""
        if 0 <= index < len(self.systems):
            self.current_index = index
        else:
            raise IndexError(f"Неверный индекс системы: {index}")

    # Солнечная система

    def load_solar_system(self):
        """Загружает солнечную систему."""
        base_path = "data/planet_images"
        system = StarSystem("Солнечная система", "Солнце", "Жёлтый карлик", 5778, 1.0)

        planets_data = [
            ("Меркурий", "Каменистая", 167, 0.38, 0, 0, "Наименьшая планета."),
            ("Венера", "Каменистая", 464, 0.95, 0, 0, "Плотная атмосфера и жара."),
            ("Земля", "Каменистая", 15, 1.0, 100, 1, "Единственная планета с жизнью."),
            ("Марс", "Каменистая", -60, 0.53, 10, 2, "Красная планета с пылевыми бурями."),
            ("Юпитер", "Газовый гигант", -110, 11.2, 0, 79, "Крупнейшая планета."),
            ("Сатурн", "Газовый гигант", -140, 9.45, 0, 82, "Известен кольцами."),
            ("Уран", "Ледяная", -195, 4.0, 0, 27, "Планета, вращающаяся боком."),
            ("Нептун", "Ледяная", -200, 3.88, 0, 14, "Самая дальняя планета.")
        ]

        for name, ptype, temp, size, life, moons, desc in planets_data:
            img_path = f"{base_path}/{name.lower()}.png"
            planet = Planet(
                name=name,
                temperature_c=temp,
                size_earth=size,
                mass_earth=round(size * 1.0, 2),
                orbital_radius_au=0.4 + len(system.planets) * 0.4,
                orbital_period_days=round(365 * ((0.4 + len(system.planets) * 0.4) ** 1.5), 1),
                planet_type=ptype,
                atmosphere=random.choice(["CO2", "N2-O2", "H2-He"]),
                life_probability=life,
                satellites=moons,
                image_path=img_path,
                description=desc
            )
            system.planets.append(planet)

        self.add_system(system, make_current=True)
        return system

    def clear_system_list(self):
        """Очищает список систем, оставляя только Солнечную систему."""
        print("[INFO] Очистка списка систем...")
        self.systems.clear()
        self.current_index = 0

        solar = self.load_solar_system()
        self.systems = [solar]
        self.current_index = 0

        try:
            self.save_system_to_db(solar)
            print("[INFO] Солнечная система восстановлена после очистки списка.")
        except Exception as e:
            print(f"[WARN] Не удалось сохранить Солнечную систему после очистки: {e}")

    # Cлучайная система

    def _random_planet_name(self, i=0):
        """Создаёт разнообразные имена планет."""
        prefixes = ["Ari", "Zor", "Orv", "Ke", "Tau", "Pro", "Xen", "Eri", "Vela", "Luma", "Oph", "Hydra", "Draco"]
        suffixes = ["-I", "-II", "-III", "-Prime", "b", "c", "d", "IV", "V", "-α", "-β"]
        return random.choice(prefixes) + random.choice(suffixes) + str(random.randint(1, 999))

    def _random_system_name(self):
        """Имя системы."""
        prefix = random.choice(["Kepler", "Gliese", "Tau", "HD", "Alpha", "Sigma", "Epsilon", "Zeta", "Beta"])
        number = random.randint(10, 999)
        return f"{prefix}-{number}"

    def _random_star_name(self):
        """Имя звезды в системе."""
        return random.choice(["Helios", "Vega", "Altair", "Rigel", "Solis", "Nova", "Aster", "Centra", "Aurion"])

    # Сохранение / загрузка CSV

    def save_system_to_csv(self, path, system=None):
        """Сохраняет систему в CSV."""
        if system is None:
            system = self.system

        try:
            with open(path, "w", encoding="utf-8-sig", newline='') as f:
                writer = csv.writer(f, delimiter=';')

                # данные о системе
                writer.writerow(["SystemName", system.name])
                writer.writerow(["StarName", system.star_name])
                writer.writerow(["StarType", system.star_type])
                writer.writerow(["StarTempK", system.star_temperature_k])
                writer.writerow(["StarRadiusSolar", system.star_radius_solar])
                writer.writerow([
                    "#PlanetName", "Temperature_C", "Size_Earth", "Mass_Earth",
                    "Orbital_Radius_AU", "Orbital_Period_Days", "Planet_Type",
                    "Atmosphere", "Life_Probability", "Satellites",
                    "Sat_Names", "Image_Path", "Description"
                ])

                # планеты
                for pl in system.planets:
                    writer.writerow([
                        pl.name,
                        round(pl.temperature_c, 2),
                        round(pl.size_earth, 2),
                        round(pl.mass_earth, 2),
                        round(pl.orbital_radius_au, 3),
                        round(pl.orbital_period_days, 1),
                        pl.planet_type,
                        pl.atmosphere,
                        round(pl.life_probability, 2),
                        int(pl.satellites),
                        pl.image_path or "",
                        pl.description or ""
                    ])
            print(f"[INFO] Система '{system.name}' успешно сохранена в CSV.")
        except Exception as e:
            raise RuntimeError(f"Не удалось сохранить CSV: {e}")

    def load_system_from_csv(self, path):
        """Загружает систему из CSV."""
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                reader = csv.reader(f, delimiter=';')
                rows = [r for r in reader if r]

            if len(rows) < 6:
                raise ValueError("CSV-файл не содержит достаточных данных.")

            sys_name = rows[0][1] if len(rows[0]) > 1 else "Безымянная система"
            star_name = rows[1][1] if len(rows[1]) > 1 else "Звезда"
            star_type = rows[2][1] if len(rows[2]) > 1 else "Неизвестный тип"
            star_temp = float(rows[3][1]) if len(rows[3]) > 1 else 5778.0
            star_radius = float(rows[4][1]) if len(rows[4]) > 1 else 1.0

            planets = []
            for r in rows[6:]:
                if not r or len(r) < 10:
                    continue
                try:
                    name = r[0]
                    temp = float(r[1])
                    size = float(r[2])
                    mass = float(r[3])
                    orbit = float(r[4])
                    period = float(r[5])
                    ptype = r[6]
                    atm = r[7]
                    life = float(r[8])
                    sats = int(float(r[9]))
                    img = r[10] if len(r) > 10 and r[10] else ""
                    desc = r[11] if len(r) > 11 else ""
                    pl = Planet(
                        name=name,
                        temperature_c=temp,
                        size_earth=size,
                        mass_earth=mass,
                        orbital_radius_au=orbit,
                        orbital_period_days=period,
                        planet_type=ptype,
                        atmosphere=atm,
                        life_probability=life,
                        satellites=sats,
                        image_path=img,
                        description=desc
                    )
                    planets.append(pl)
                except Exception as e:
                    print(f"[WARN] Пропуск строки CSV ({e}): {r}")

            system = StarSystem(
                name=sys_name,
                star_name=star_name,
                star_type=star_type,
                star_temperature_k=star_temp,
                star_radius_solar=star_radius,
                planets=planets
            )

            self.add_system(system, make_current=True)
            self.save_system_to_db(system)
            print(f"[INFO] Система '{sys_name}' успешно загружена из CSV.")
            return system

        except Exception as e:
            raise RuntimeError(f"Ошибка при загрузке CSV: {e}")

    # Генерация случайной системы

    def generate_random_system(self, min_planets=4, max_planets=8):
        print("[DEBUG] Генерация новой системы...")
        count = random.randint(min_planets, max_planets)
        planets = []

        # список всех картинок в папке
        image_files = [
            "data/planet_images/random_planet_1.png",
            "data/planet_images/random_planet_2.png",
            "data/planet_images/random_planet_3.png",
            "data/planet_images/random_planet_4.png",
            "data/planet_images/random_planet_5.png",
            "data/planet_images/random_planet_6.png",
            "data/planet_images/random_planet_7.png",
            "data/planet_images/random_planet_8.png",
            "data/planet_images/black_hole.png"
        ]

        for i in range(count):
            orbit = round(0.4 + i * 0.4, 2)
            temp = round(300 - orbit * random.uniform(25, 60), 1)
            size = round(random.uniform(0.3, 10.0), 2)
            ptype = random.choice(["Каменистая", "Газовый гигант", "Ледяная", "Пустынная", "Океаническая"])
            atm = random.choice(["N2-O2", "CO2", "H2-He", "Methane"])

            img = image_files.pop() if image_files else "data/planet_images/земля.png"

            pl = Planet(
                name=self._random_planet_name(i),
                temperature_c=temp,
                size_earth=size,
                mass_earth=round(size * random.uniform(0.5, 2.5), 2),
                orbital_radius_au=orbit,
                orbital_period_days=round(365 * (orbit ** 1.5), 1),
                planet_type=ptype,
                atmosphere=atm,
                life_probability=round(random.uniform(0, 80), 1),
                satellites=random.randint(0, 5),
                image_path=img,
                description=f"Генерированная планета {ptype}"
            )
            pl.generate_description()
            planets.append(pl)

        # создаём систему
        system = StarSystem(
            name=self._random_system_name(),
            star_name=self._random_star_name(),
            star_type=random.choice(["Жёлтый карлик", "Красный гигант", "Белый карлик"]),
            star_temperature_k=random.randint(3000, 10000),
            star_radius_solar=round(random.uniform(0.5, 2.5), 2),
            planets=planets
        )

        # сохраняем и добавляем в список
        self.save_system_to_db(system)
        self.add_system(system, make_current=True)

        return system

    # Работа с БД

    def save_system_to_db(self, system: StarSystem):
        """Сохраняет систему и планеты в базу данных."""
        print(f"[DEBUG] Сохранение системы '{system.name}' с {len(system.planets)} планетами.")
        conn = get_connection()
        cur = conn.cursor()

        # Удалим дубликаты по имени
        cur.execute("DELETE FROM systems WHERE name = ?", (system.name,))
        cur.execute("DELETE FROM planets WHERE system_name = ?", (system.name,))

        # Сохраняем систему
        cur.execute("""
            INSERT INTO systems (name, star_name, star_type, star_temperature, star_radius, planet_count)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (system.name, system.star_name, system.star_type,
              int(system.star_temperature_k), float(system.star_radius_solar), len(system.planets)))

        # Сохраняем планеты
        for p in system.planets:
            cur.execute("""
                INSERT INTO planets (
                    system_name, name, temperature_c, size_earth, mass_earth,
                    orbital_radius_au, orbital_period_days, planet_type, atmosphere,
                    life_probability, satellites, image_path, description
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                system.name, p.name, float(p.temperature_c), float(p.size_earth),
                float(p.mass_earth), float(p.orbital_radius_au), float(p.orbital_period_days),
                p.planet_type, p.atmosphere, float(p.life_probability),
                int(p.satellites), p.image_path, p.description
            ))

        conn.commit()
        conn.close()

    def load_all_systems_from_db(self):
        """Загружает все системы и планеты из базы."""
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT name, star_name, star_type, star_temperature, star_radius FROM systems")
        systems_raw = cur.fetchall()

        systems = []
        for sys_row in systems_raw:
            name, star_name, star_type, star_temp, star_radius = sys_row
            cur.execute("SELECT * FROM planets WHERE system_name = ?", (name,))
            planet_rows = cur.fetchall()

            planets = []
            for row in planet_rows:
                # индексы в зависимости от таблицы planets
                (_, _, pname, temp, size, mass, orbit, period, ptype, atm, life, sats, img, desc) = row
                pl = Planet(
                    name=pname,
                    temperature_c=float(temp),
                    size_earth=float(size),
                    mass_earth=float(mass),
                    orbital_radius_au=float(orbit),
                    orbital_period_days=float(period),
                    planet_type=ptype,
                    atmosphere=atm,
                    life_probability=float(life),
                    satellites=int(sats),
                    image_path=img,
                    description=desc
                )
                planets.append(pl)

            sys_obj = StarSystem(
                name=name,
                star_name=star_name,
                star_type=star_type,
                star_temperature_k=int(star_temp),
                star_radius_solar=float(star_radius),
                planets=planets
            )
            systems.append(sys_obj)

        conn.close()
        return systems

