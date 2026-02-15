import enum

class DestinationValidation(enum.Enum):
    DV_OK = 2401
    DV_ERR_QUERY_TIME = 2402
    DV_ERR_DESTINATION_ID = 2403
    DV_UNKNOWN = 2404
