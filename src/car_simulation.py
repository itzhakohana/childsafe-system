from dataclasses import dataclass


@dataclass
class CarEnvironment:
    outside_temp_c: float
    cabin_temp_c: float
    co2_ppm: int
    child_present: bool
    windows_open_pct: int
    ac_on: bool
    heater_on: bool
    car_locked: bool
    engine_on: bool
    sunlight_factor: float  # 0.0 - 1.0

    def step(self, seconds: int) -> None:
        """
        Updates the internal car environment over time.
        Very simple first version:
        - Sun heats the cabin
        - AC cools the cabin
        - Open windows reduce heat and CO2 buildup
        - If a child is inside and ventilation is poor, CO2 rises
        """

        # 1) Cabin temperature change
        heat_gain = (self.outside_temp_c - self.cabin_temp_c) * 0.02
        sun_gain = self.sunlight_factor * 0.15
        ac_cooling = 0.25 if self.ac_on else 0.0
        heater_warming = 0.20 if self.heater_on else 0.0
        window_cooling = (self.windows_open_pct / 100.0) * 0.10

        temp_delta_per_step = heat_gain + sun_gain + heater_warming - ac_cooling - window_cooling
        self.cabin_temp_c += temp_delta_per_step * seconds

        # 2) CO2 change
        if self.child_present:
            co2_rise = 12
        else:
            co2_rise = 2

        ventilation_reduction = int((self.windows_open_pct / 100.0) * 20)
        if self.ac_on:
            ventilation_reduction += 5

        self.co2_ppm += (co2_rise - ventilation_reduction) * seconds

        # 3) Keep values in sensible ranges
        if self.co2_ppm < 400:
            self.co2_ppm = 400

        if self.cabin_temp_c < -10:
            self.cabin_temp_c = -10
        elif self.cabin_temp_c > 80:
            self.cabin_temp_c = 80