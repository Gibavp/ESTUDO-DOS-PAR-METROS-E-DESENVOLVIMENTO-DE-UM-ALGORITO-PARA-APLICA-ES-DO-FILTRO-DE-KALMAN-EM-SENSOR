import board
import busio
import time as delay
from adafruit_vl53l0x import VL53L0X
from digitalio import DigitalInOut

#======================== Variáveis para sensor ========================
      
NORMAL_MODE = 33000 # Peíodo de pulsação do laser = 33 ms
HIGH_SPEED = 20000 # Peíodo de pulsação do laser reduzido = 33 ms
HIGH_ACCURACY = 200000 # Peíodo de pulsação do laser incrementado = 200 ms
vl53 = [] # Declararação do atributo sensor


'''
    Setup dos pinos e declaração de endereçamento I2C para controle dos sensores
'''

#======================= Setup dos pinos I2C e digitais ========================

i2c_address = board.I2C() # Recebe o endereço I2C da placa
delay.sleep(0.5)
xshut = [DigitalInOut(board.D17)] # Seta os pinos digitais para controle
count = 1000
n_medidas = count
soma_s1 = 0
soma_anterior_s1 = 0
#======================= Desligamento os sensores ========================

for power_pin in xshut:
    power_pin.switch_to_output(value=False)

'''
    Teste de hardware e pareamento dos sensores
'''

for i, power_pin in enumerate(xshut):
    power_pin.value = True # Ligado o sensor 'i'
    vl53.insert(i, VL53L0X(i2c_address)) # Endereçamento do sensor 'i'
    if i < len(xshut) - 1:
        vl53[i].set_address(i + 0x30) # Declaração do endereçamento caso o mesmo não esteja em uso
        delay.sleep(0.5) # Delay para configuração (Mínimo de 0.5)
        vl53[i].measurement_timing_budget = HIGH_ACCURACY # Declaração do modo de operação
        delay.sleep(0.5) # Delay para configuração (Mínimo de 0.5)
        
while count:
    #print('\nFaltam {} ciclo para finalização\n'.format(count))
    for index, sensor in enumerate(vl53):
        leitura_atual = sensor.range
                
        if (index + 1) == 1:
            soma_s1 = soma_anterior_s1 + leitura_atual
            soma_anterior_s1 = soma_s1

    count = count - 1

media_s1 = soma_s1 / n_medidas

print(media_s1)