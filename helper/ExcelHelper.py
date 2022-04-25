import pandas


class ExcelHelper:

    def __init__(self):
        pass

    @staticmethod
    def retrieve_drivers_data():
        towingDrivers_df = pandas.read_excel('./static/DriversDB.xlsx', sheet_name='drivers_data')
        return towingDrivers_df.to_dict('records')

    @staticmethod
    def retrieve_price_list_data():
        towingDrivers_df = pandas.read_excel('./static/DriversDB.xlsx', sheet_name='price_list')
        return towingDrivers_df.to_dict('records')
