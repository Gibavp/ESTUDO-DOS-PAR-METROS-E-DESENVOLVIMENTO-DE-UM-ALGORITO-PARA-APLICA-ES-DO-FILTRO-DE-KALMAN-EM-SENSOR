import time
import board
import math
import pandas as pd

from digitalio import DigitalInOut
from adafruit_vl53l0x import VL53L0X 

#pandas
df = pd.DataFrame({'Camada': [], 'Ângulo (Rad)':[], 'Média S1':[], 'Média S2':[], 'Média S3':[], 'Média S1 - x':[], 'Média S1 - y':[], 'Média S2 - x':[], 'Média S2 - y':[], 'Média S3 - x':[], 'Média S3 - y':[], 'Cor':[]})
columns = list(df)
##


i2c_address = board.I2C()
time.sleep(0.5)
xshut = [DigitalInOut(board.D17), DigitalInOut(board.D22), DigitalInOut(board.D27)]

for power_pin in xshut:
    power_pin.switch_to_output(value=False)

# Variáveis

vl53 = []
raio_padrao = 160 #unidade: mm
distancia_total = 180 #unidade: mm
tolerancia = 3 #unidade mm

for i, power_pin in enumerate(xshut):
    power_pin.value = True
    time.sleep(0.5)
    vl53.insert(i, VL53L0X(i2c_address)) # also performs VL53L0X hardware check
    time.sleep(1.0)
    if i < len(xshut) - 1:
        vl53[i].set_address(i + 0x30) # address assigned should NOT be already in use
        time.sleep(1.0)
        vl53[i].measurement_timing_budget = 200000
        time.sleep(0.5)

for i in range(5):
    for j in range(10):
        radianos = math.radians(j*1.8)    

        soma_s1 = 0
        soma_anterior_s1 = 0
        media_s1 = 0
        soma_s2 = 0
        soma_anterior_s2 = 0
        media_s2 = 0
        soma_s3 = 0
        soma_anterior_s3 = 0
        media_s3 = 0
        media_s1_x = 0
        media_s1_y = 0
        media_s2_x = 0
        media_s2_y = 0
        media_s3_x = 0
        media_s3_y = 0
        
        count = 10
        n_medidas = count
        
        while count:
            print('\nFaltam {} ciclo para finalização\n'.format(count))
            for index, sensor in enumerate(vl53):
                leitura_atual = sensor.range
                print('Sensor {} Range: {}mm'.format(index + 1, leitura_atual))
                
                if (index + 1) == 1:
                    soma_s1 = soma_anterior_s1 + leitura_atual
                    soma_anterior_s1 = soma_s1
                
                if (index + 1) == 2:
                    soma_s2 = soma_anterior_s2 + leitura_atual
                    soma_anterior_s2 = soma_s2
                    
                if (index + 1) == 3:
                    soma_s3 = soma_anterior_s3 + leitura_atual
                    soma_anterior_s3 = soma_s3
            count -= 1

        media_s1 = soma_s1 / n_medidas
        media_s2 = soma_s2 / n_medidas
        media_s3 = soma_s3 / n_medidas
        
        media_s1_x = (distancia_total - media_s1) * math.cos(radianos)
        media_s1_y = (distancia_total - media_s1) * math.sin(radianos)
        media_s2_x = (distancia_total - media_s2) * math.cos(radianos)
        media_s2_y = (distancia_total - media_s2) * math.sin(radianos)
        media_s3_x = (distancia_total - media_s3) * math.cos(radianos)
        media_s3_y = (distancia_total - media_s3) * math.sin(radianos) 
    
print("\nMultiple VL53L0X sensors' addresses are assigned properly execute detect_range() to read each sensors range readings\n")
print("Valores médios coletados")
print('Sensor 1 Range: {}mm'.format(media_s1))
print('Sensor 2 Range: {}mm'.format(media_s2))
print('Sensor 3 Range: {}mm'.format(media_s3))
print('Sensor 1 valor x: {}'.format(media_s1_x))
print('Sensor 1 valor y: {}'.format(media_s1_y))
print('Sensor 2 valor x: {}'.format(media_s2_x))
print('Sensor 2 valor y: {}'.format(media_s2_y))
print('Sensor 3 valor x: {}'.format(media_s3_x))
print('Sensor 3 valor y: {}'.format(media_s3_y))