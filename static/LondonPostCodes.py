from enum import Enum


class LondonPostCodes(Enum):
    EC_DISTRICT = 'EC'
    WC_DISTRICT = 'WC'
    E_DISTRICT = 'E'
    N_DISTRICT = 'N'
    NW_DISTRICT = 'NW'
    SE_DISTRICT = 'SE'
    SW_DISTRICT = 'SW'
    W_DISTRICT = 'W'
    BR_DISTRICT = 'BR'
    CR_DISTRICT = 'CR'
    DA_DISTRICT = 'DA'
    EN_DISTRICT = 'EN'
    HA_DISTRICT = 'HA'
    IG_DISTRICT = 'IG'
    KT_DISTRICT = 'KT'
    RM_DISTRICT = 'RM'
    SM_DISTRICT = 'SM'
    TW_DISTRICT = 'TW'
    UB_DISTRICT = 'UB'
    WD_DISTRICT = 'WD'

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_
