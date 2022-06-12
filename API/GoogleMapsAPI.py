import calendar
import urllib.parse
import itertools
from asyncio import ensure_future, gather
import asyncio
import aiohttp
import time


class GoogleMapsAPI:
    api_key = None
    response = []

    def __init__(self, key):
        self.api_key = key

    def calculate_live_distance(self, origins, destinations, data_to_update=None):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.__request_controller(origins, destinations, data_to_update))
        return self.response

    async def __request_controller(self, origins, destinations, data_to_update):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for paginatedOrigins in [origins[i:i + 25] for i in range(0, len(origins), 25)]:
                for paginatedDestinations in [destinations[i:i + 25] for i in range(0, len(destinations), 25)]:
                    tasks.append(ensure_future(self.__request_worker(session, self.__get_distance_matrix_url(
                        paginatedOrigins,
                        paginatedDestinations), data_to_update)))
            await gather(*tasks)

    async def __request_worker(self, session, url, data_to_update):
        async with session.get(url) as response:
            result = await response.json()
            if 'rows' in result:
                if data_to_update is not None:
                    search_column = "destination_addresses"
                    if len(result["origin_addresses"]) > 1:
                        search_column = "origin_addresses"
                    for index, data in enumerate(result["rows"]):
                        driver_mapping_results = [matching_data for matching_data in data_to_update if
                                                  matching_data["Post Code"] in result[search_column][index]]
                        for matching_elements in driver_mapping_results:
                            distance_matrix_data = data["elements"][0]
                            matching_elements.update(dict((key, distance_matrix_data[key]['value'])
                                                          for key in ['duration_in_traffic', 'distance']))
                else:
                    self.response = [dict((key, (data['elements'][0])[key]['value'])
                                          for key in ['duration_in_traffic', 'distance']
                                          if key in data['elements'][0])
                                     for data in result['rows']]

    def __get_distance_matrix_url(self, origins, destinations):
        url = f'https://maps.googleapis.com/maps/api/distancematrix/json?' \
              f'origins={self.__get_string_of_locations(origins)}' \
              f'&destinations={(self.__get_string_of_locations(destinations))}' \
              f'&departure_time={calendar.timegm(time.gmtime())}&key={self.api_key}'
        return url

    @staticmethod
    def __get_string_of_locations(locations):
        if not isinstance(locations, str) and len(locations) > 1:
            return "|".join(locations)
        else:
            return urllib.parse.quote_plus(locations)
