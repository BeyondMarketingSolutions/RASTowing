import pandas


class ExcelHelper:

    def __init__(self):
        pass

    @staticmethod
    def retrieve_drivers_data():
        towingDrivers_df = pandas.read_excel('./static/DriversDB.xlsx', sheet_name='drivers_data')
        return towingDrivers_df.to_dict('records')

    @staticmethod
    def retrieve_service_list_data():
        price_service_list_df = pandas.read_excel('./static/DriversDB.xlsx', sheet_name='price_service_list')
        return price_service_list_df.to_dict('records')

    @staticmethod
    def retrieve_price_mile_list_data():
        price_mile_list_df = pandas.read_excel('./static/DriversDB.xlsx', sheet_name='price_mile_list')
        return price_mile_list_df.to_dict('records')
