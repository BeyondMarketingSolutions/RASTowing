


class FileHelper:

    @staticmethod
    def retrieve_postcodes_data():
        with open('./static/UK_PostCodes.txt', 'r', encoding='utf-8') as file_read:
            return [str(data) for data in file_read.readlines()]