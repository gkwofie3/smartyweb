USER_TYPE_CHOICES={
    ('superadmin', 'Super Admin'),
    ('admin', 'Admin'),
}
PROTOCOL_CHOICES = (
    ("ModbusTCP", "Modbus TCP"),
    ("ModbusRTU", "Modbus RTU"),
    ("BACnetIP", "BACnet IP"),
    ("BACnetMSTP", "BACnet MS/TP"),
    ("Mqtt", "MQTT"),
)
DEVICE_TYPE_CHOICES = [
    ('AVR', 'AVR'),
    ('FIRE SYSTEM', 'Fire System'),
    ('ATS', 'ATS'),
    ('GENERATOR', 'Generator'),
    ('HVAC SYSTEM', 'HVAC System'),
    ('TRANSFORMER', 'Transformer'),
    ('UPS', 'UPS'),
    ('ENERGY METER', 'Energy Meter'),
    ('WATER METER', 'Water Meter'),
    ('LIFT', 'Lift'),
    ('LIGHTING CONTROL SYSTEM', 'Lighting Control System'),
    ('ACCESS CONTROL', 'Access Control'),
    ('SECURITY SYSTEM', 'Security System'),
    ('SURVEILLANCE SYSTEM', 'Surveillance System'),
    ('ENVIRONMENTAL SENSOR', 'Environmental Sensor'),
    ('UTILITY MANAGEMENT', 'Utility Management System'),
    ('GAS DETECTION SYSTEM', 'Gas Detection System'),
    ('PUMP CONTROLLER', 'Pump Controller'),
    ('VFD', 'VFD'),
    ('AUDIO VISUAL SYSTEM', 'Audio Visual System'),
]
MODBUS_BAUD_RATE_CHOICES = (
    (1200, "1200"),
    (2400, "2400"),
    (4800, "4800"),
    (9600, "9600"),
    (19200, "19200"),
    (38400, "38400"),
    (57600, "57600"),
    (115200, "115200"),
)
MODBUS_PARITY_CHOICES = (
    ("None", "None"),
    ("Even", "Even"),
    ("Odd", "Odd"),
)
MODBUS_STOP_BITS_CHOICES = (
    (1, "1"),
    (2, "2"),
)
SIGNAL_TYPE_CHOICES = (
    ("Digital", "Digital"),
    ("Analog", "Analog"),
    ("Pulse", "Pulse"),
    ("Multistate", "Multistate")
)
IO_TYPE_CHOICES = (
    ('REGISTER', 'Register Value'),
    ('VARIABLE', 'Variable Display'),
    ('DATA', 'Data'),
)
IO_DATA_TYPE_CHOICES = (
    ("Integer", "Integer"),
    ("Float", "Float"),
    ("Real", "Real"),
    ("Boolean", "Boolean"),
    ('String', 'String'),
    ("List", "List"),
    ("Object", "Object")
)
READ_FUNCTION_CODES = (
    ("01", "01 - Read Coils"),
    ("02", "02 - Read Discrete Inputs"),
    ("03", "03 - Read Holding Registers"),
    ("04", "04 - Read Input Registers"),
)
WRITE_FUNCTION_CODES = (
    ("05", "05 - Write Single Coil"),
    ("06", "06 - Write Single Register"),
    ("15", "15 - Write Multiple Coils"),
    ("16", "16 - Write Multiple Registers"),
)
BACNET_OBJECT_TYPE_CHOICES = (
    (0, "Analog Input"),
    (1, "Analog Output"),
    (2, "Analog Value"),
    (3, "Binary Input"),
    (4, "Binary Output"),
    (5, "Binary Value"),
    (13, "Multi-state Input"),
    (14, "Multi-state Output"),
    (19, "Multi-state Value"),
)
DIRECTION_CHOICES = (
    ("Input", "Input"),
    ("Output", "Output"),
)
DATA_TYPE_CHOICES = (
    ("Integer", "Integer"),
    ("Float", "Float"),
    ("Real", "Real"),
    ("Boolean", "Boolean"),
)
ERROR_STATUS_CHOICES = (
    ('OK', 'OK'),
    ('FAULT', 'Hardware Fault'),
    ('COMM_ERROR', 'Communication Error'),
    ('RANGE_ERROR', 'Out of Range'),
)
PAGE_TYPE_CHOICES = [
    ('STANDARD', 'Standard'),
    ('HTML', 'Raw HTML'),
]
HTML_SOURCE_CHOICES = [
    ('CODE', 'Direct Code Entry'),
    ('FILE', 'External HTML File'),
]
WIDGET_TYPE_CHOICES = [
    ('gauge', 'Gauge Chart'),
    ('status_card', 'Status Card'),
    ('control', 'Control Panel'),
    ('line_chart', 'Line Chart'),
    ('bar_chart', 'Bar Chart'),
    ('pie_chart', 'Pie Chart'),
    ('stat_panel', 'Statistics Panel'),
]
COMPONENT_TYPE_CHOICES = [
    ('TEXT', 'Text Block'),
    ('VARIABLE', 'Variable Display'),
    ('DATA', 'Data'),
    ('READOUT', 'Value Readout'),
]
