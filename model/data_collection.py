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

# Konstanta untuk konversi ke PPM
CALIBRATION_CONSTANTS = {
    "MQ-3": (0.4, -1.5),
    "MQ-135": (1.2, -1.0),
    "MQ-136": (0.8, -1.3),
    "TGS 822": (1.0, -1.1),
    "TGS 2600": (0.9, -1.2),
    "TGS 2602": (1.1, -1.0),
    "TGS 2610": (0.7, -1.3),
    "TGS 2620": (1.0, -1.1)
}

def read_adc(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    voltage = (data * 3.3) / 1023
    return voltage

def voltage_to_ppm(sensor, voltage):
    A, B = CALIBRATION_CONSTANTS[sensor]
    return A * (voltage / 3.3) ** B

output1 = input("Masukkan nilai Output1: ")
output2 = input("Masukkan nilai Output2: ")

with open("sensor_data.csv", mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow([
        "Waktu", "MQ-3", "MQ-3 (PPM)", "MQ-135", "MQ-135 (PPM)", "MQ-136", "MQ-136 (PPM)",
        "TGS 822", "TGS 822 (PPM)", "TGS 2600", "TGS 2600 (PPM)", "TGS 2602", "TGS 2602 (PPM)",
        "TGS 2610", "TGS 2610 (PPM)", "TGS 2620", "TGS 2620 (PPM)", "Output1", "Output2"
    ])
    
    try:
        while True:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            sensor_values = {}
            sensor_ppm = {}
            
            for sensor, pin in SENSOR_PINS.items():
                sensor_values[sensor] = read_adc(pin)
                sensor_ppm[sensor] = voltage_to_ppm(sensor, sensor_values[sensor])
                
            writer.writerow([
                timestamp,
                sensor_values["MQ-3"], sensor_ppm["MQ-3"],
                sensor_values["MQ-135"], sensor_ppm["MQ-135"],
                sensor_values["MQ-136"], sensor_ppm["MQ-136"],
                sensor_values["TGS 822"], sensor_ppm["TGS 822"],
                sensor_values["TGS 2600"], sensor_ppm["TGS 2600"],
                sensor_values["TGS 2602"], sensor_ppm["TGS 2602"],
                sensor_values["TGS 2610"], sensor_ppm["TGS 2610"],
                sensor_values["TGS 2620"], sensor_ppm["TGS 2620"],
                output1, output2
            ])
            
            print("Data tersimpan.")
            print(f"MQ-3: {sensor_values['MQ-3']:.3f} V | {sensor_ppm['MQ-3']:.2f} ppm")
            print(f"MQ-135: {sensor_values['MQ-135']:.3f} V | {sensor_ppm['MQ-135']:.2f} ppm")
            print(f"MQ-136: {sensor_values['MQ-136']:.3f} V | {sensor_ppm['MQ-136']:.2f} ppm")
            print(f"TGS 822: {sensor_values['TGS 822']:.3f} V | {sensor_ppm['TGS 822']:.2f} ppm")
            print(f"TGS 2600: {sensor_values['TGS 2600']:.3f} V | {sensor_ppm['TGS 2600']:.2f} ppm")
            print(f"TGS 2602: {sensor_values['TGS 2602']:.3f} V | {sensor_ppm['TGS 2602']:.2f} ppm")
            print(f"TGS 2610: {sensor_values['TGS 2610']:.3f} V | {sensor_ppm['TGS 2610']:.2f} ppm")
            print(f"TGS 2620: {sensor_values['TGS 2620']:.3f} V | {sensor_ppm['TGS 2620']:.2f} ppm")
            time.sleep(2)
    except KeyboardInterrupt:
        print("Program dihentikan.")
        spi.close()
