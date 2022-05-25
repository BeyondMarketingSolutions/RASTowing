from enum import Enum


class PriceCategories(Enum):
    CALL_OUT = 'Call out'
    BREAKDOWN_RECOVERY_SERVICE = 'Breakdown Recovery'
    TOTAL_LIFT_RECOVERY = 'Total Lift Recovery'
    JUMPSTART_SERVICE = 'Jumpstart'
    BATTERY_SERVICE = 'Battery Services'
    TYRE_SERVICE = 'Tyre Services'
    WRONG_FUEL_SERVICE = 'Wrong Fuel'
    WEEKEND = 'Weekend'
    NIGHT_RATE = 'Night Rate'
    CARAVAN_TRAILER = 'Caravan/ Trailer'
    ADDITIONAL_TOOLS = 'Whells Dolly/ Stick'

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_
