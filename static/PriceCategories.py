from enum import Enum


class PriceCategories(Enum):
    CALL_OUT = 'Call out'
    BREAKDOWN_RECOVERY_SERVICE = 'Breakdown Recovery'
    JUMPSTART_SERVICE = 'Jumpstart'
    BATTERY_SERVICE = 'Battery Services'
    TYRE_SERVICE = 'Tyre Services'
    WRONG_FUEL_SERVICE = 'Tyre Services'
    WEEKEND = 'Weekend'
    NIGHT_RATE = 'Night Rate'
    CARAVAN_TRAILER = 'Caravan/ Trailer'
    ADDITIONAL_TOOLS = 'Whells Dolly/ Stick'

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_
