from dataclasses import dataclass, field
from core.planet import Planet


@dataclass
class StarSystem:
    """Данные о звёздной системе."""
    name: str
    star_name: str
    star_type: str
    star_temperature_k: int
    star_radius_solar: float
    planets: list[Planet] = field(default_factory=list)

    def average_temperature(self):
        if not self.planets:
            return None
        return sum(p.temperature_c for p in self.planets) / len(self.planets)
