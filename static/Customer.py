class Customer:
    name = ""
    email = ""
    phone = ""

    def __init__(self, name, email, phone):
        self.name = name
        self.email = email
        self.phone = phone

    def set_name(self, name):
        self.name = name

    def set_email(self, email):
        self.email = email

    def set_phone(self, phone):
        self.phone = phone
