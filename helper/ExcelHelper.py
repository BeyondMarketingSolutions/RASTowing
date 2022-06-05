import pandas

from static.PriceCategories import PriceCategories
from static.LondonPostCodes import LondonPostCodes


class ExcelHelper:

    def __init__(self):
        pass

    @staticmethod
    def retrieve_drivers_data(postal_code):
        sheet_name = None
        xls_file = pandas.ExcelFile('./static/RAS_DB.xlsx')
        post_code_initials = ExcelHelper.remove_digits_from_string(postal_code.upper().split()[0])
        if LondonPostCodes.has_value(post_code_initials):
            sheet_name = 'LONDON'
        sheet_name_list = [sheet for sheet in xls_file.sheet_names if post_code_initials in sheet.upper().strip()]
        if  len(sheet_name_list) > 0:
            sheet_name = sheet_name_list[0]
        else:
            return sheet_name
        towingDrivers_df = pandas.read_excel('./static/RAS_DB.xlsx', sheet_name=sheet_name)
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

    @staticmethod
    def remove_digits_from_string(string):
        return ''.join([i for i in string if not i.isdigit()])
