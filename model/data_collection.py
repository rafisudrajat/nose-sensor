import time
import spidev
import csv

# Inisialisasi SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # Bus 0, Device 0
spi.max_speed_hz = 135000

# Pin sensor pada MCP3008
SENSOR_PINS = {
    "MQ-3": 0,      # Alkohol
    "MQ-135": 1,    # Polutan Udara
    "MQ-136": 2,    # H2S
    "TGS 822": 7,   # Uap Organik
    "TGS 2600": 3,  # Gas Umum
    "TGS 2602": 4,  # Gas Polutan
    "TGS 2610": 5,  # LPG
    "TGS 2620": 6   # Alkohol dan gas volatil
}

def read_adc(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    voltage = (data * 3.3) / 1023
    return voltage

data_collected = []
    
try:
    while True:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        sensor_values = {}
        
        for sensor, pin in SENSOR_PINS.items():
            sensor_values[sensor] = read_adc(pin)
            
        data_collected.append([
            timestamp,
            sensor_values["MQ-3"],
            sensor_values["MQ-135"],
            sensor_values["MQ-136"],
            sensor_values["TGS 822"],
            sensor_values["TGS 2600"],
            sensor_values["TGS 2602"],
            sensor_values["TGS 2610"],
            sensor_values["TGS 2620"],
        ])
        
        print("Data tersimpan.")
        print(f"MQ-3: {sensor_values['MQ-3']:.3f} V")
        print(f"MQ-135: {sensor_values['MQ-135']:.3f} V")
        print(f"MQ-136: {sensor_values['MQ-136']:.3f} V")
        print(f"TGS 822: {sensor_values['TGS 822']:.3f} V")
        print(f"TGS 2600: {sensor_values['TGS 2600']:.3f} V")
        print(f"TGS 2602: {sensor_values['TGS 2602']:.3f} V")
        print(f"TGS 2610: {sensor_values['TGS 2610']:.3f} V")
        print(f"TGS 2620: {sensor_values['TGS 2620']:.3f} V")
        time.sleep(2)
except KeyboardInterrupt:
    sample_name = input("Input sample name: ")
    with open(f'{sample_name}.csv', mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(data)
    spi.close()
