from enum import Enum


class SessionDataEnum(Enum):
    DRIVERS = 'drivers'
    ESTIMATED_TOTAL_PAYMENT = 'total_payment_price'
    ESTIMATED_ADVANCE_PAYMENT = 'advanced_payment_price'
    SERVICE = 'type_of_service'
    CUSTOMER_LOCATION = 'origin'
    CUSTOMER_DESTINATION = 'destination'
    NOTES = 'description'

