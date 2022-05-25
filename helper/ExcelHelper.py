import pandas

from static.PriceCategories import PriceCategories


class ExcelHelper:

    @staticmethod
    def retrieve_drivers_data():
        towingDrivers_df = pandas.read_excel('./static/RAS_DB.xlsx', sheet_name='drivers_data')
        return towingDrivers_df.to_dict('records')

    @staticmethod
    def retrieve_price_mile_by_vehicle_type(vehicle_type):
        price_service_list_df = pandas.read_excel('./static/RAS_DB.xlsx', sheet_name='price_mile_list')
        price_mile_data = price_service_list_df.to_dict('records')
        final_data = [data for data in price_mile_data if data['CategoryType'] == vehicle_type]
        if final_data is not None and 'Price' in final_data[0]:
            return final_data[0]['Price']
        else:
            return 0

    @staticmethod
    def retrieve_from_price_list_service_data(price_category):
        price_service_list_df = pandas.read_excel('./static/RAS_DB.xlsx', sheet_name='price_service_list')
        categoryData = price_service_list_df.to_dict('records')
        if PriceCategories.has_value(price_category):
            return [data for data in categoryData if data['Categories'] == price_category][0]
        else:
            return None
