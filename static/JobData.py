class JobData:
    origin = ""
    destination = None
    service = ""
    weight = "",
    price = "",
    description = ""

    def __init__(self, origin, destination, service, weight, description):
        self.origin = origin
        self.destination = destination
        self.service = service
        self.weight = weight
        self.description = description

    def set_origin(self, origin):
        self.origin = origin

    def set_destination(self, destination):
        self.destination = destination

    def set_service(self, service):
        self.service = service

    def set_weight(self, weight):
        self.weight = weight

    def set_description(self, description):
        self.description = description
