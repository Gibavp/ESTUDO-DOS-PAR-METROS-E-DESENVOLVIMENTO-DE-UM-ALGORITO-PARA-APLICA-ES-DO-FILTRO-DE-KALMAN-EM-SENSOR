# -*- coding: utf-8 -*-

#============================= Bibliotecas =========================================
import time as delay
import board
from digitalio import DigitalInOut
from adafruit_vl53l0x import VL53L0X
import pandas as pd
import numpy as np
from statistics import mean

'''
    Variáveis auxiliares
'''   

#== Variáveis para sensor ==
      
NORMAL_MODE = 33000     # Peíodo de pulsação do laser = 33 ms
HIGH_SPEED = 20000      # Peíodo de pulsação do laser reduzido = 20 ms
HIGH_ACCURACY = 200000  # Peíodo de pulsação do laser incrementado = 200 ms
vl53 = []               # Declararação do atributo sensor

#== Variáveis para leitura ==
 
count_Leitura = 2500           # Número de vezes que cada sensor fará a leitura
Aux_Leitura = count_Leitura    # Variável auxiliar para contagem de leituras
media_S1 = 0                   # Variável para média do sensor 1
media_S2 = 0                   # Variável para média do sensor 2
leituras_S1 = []               # Lista para armazenamento das leituras do sensor 1
leituras_S2 = []               # Lista para armazenamento das leituras do sensor 2
lista_count_Leitura = []       # Lista para armazenar a leitura corrente
lista_Media_S1 = []            # Lista para armazenamento das médias do sensor 1
lista_Media_S2 = []            # Lista para armazenamento das médias do sensor 2
lista_Leitura_df = []          # Lista para armazenamento das leituras efetuadas
df_data = pd.DataFrame()       # Data Frame para armazenamento dos dados

'''
    Setup dos pinos e declaração de endereçamento I2C para controle dos sensores
'''

#=== Setup dos pinos I2C e digitais ==

i2c_address = board.I2C()           # Recebe o endereço I2C da placa
delay.sleep(0.5)                    # Delay mínimo para evitar problema de acesso as portas 
xshut = [DigitalInOut(board.D17), 
         DigitalInOut(board.D22)]   # Seta os pinos digitais para controle dos sensores

#== Desligamento os sensores ==

for power_pin in xshut:
    power_pin.switch_to_output(value=False)

'''
    Teste de hardware e pareamento dos sensores
'''

for i, power_pin in enumerate(xshut):
    power_pin.value = True                                  # Liga o sensor 'i'
    vl53.insert(i, VL53L0X(i2c_address))                    # Faz o endereçamento do sensor 'i'
    if i < len(xshut) - 1:
        vl53[i].set_address(i + 0x30)                       # Declaração do endereçamento caso o mesmo não esteja em uso
        delay.sleep(0.5)                                    # Delay para configuração (Mínimo de 0.5)
        vl53[i].measurement_timing_budget = HIGH_ACCURACY   # Declaração do modo de operação
        delay.sleep(0.5)                                    # Delay para configuração (Mínimo de 0.5)

#== Void Loop ==

# While responsável pelas leituras
while count_Leitura:
    for index, sensor in enumerate(vl53):
        '''Descomente a linha abaixo para apresentar os valores lidos em tela (pode ocasionar lentidão)'''
        #print('Sensor {} Range: {}mm'.format(index + 1, sensor.range))
                
        # Separação dos dados lidos por sensor
        # Sensor 1
        if (index + 1) == 1:
            leituras_S1.append(sensor.range)
        # Sensor 2
        if (index + 1) == 2:
            leituras_S2.append(sensor.range)
                                                    
        # Decrementar variável de trava do while
        count_Leitura -= 1
        
    # Fim do while das leituras
        
    # Cálculo das médias do sensor S1
    media_S1 = mean(leituras_S1)
    
    # Adição da média do sensor 1 da lista correspondente 
    lista_Media_S1.append(media_S1)
            
    # Cálculo das médias do sensor S2
    media_S2 = mean(leituras_S2)
    
    # Adição da média do sensor 2 da lista correspondente
    lista_Media_S2.append(media_S2)

    # Limpeza da lista do sensor 1
    leituras_S1.clear()
            
    # Limpeza da lista do sensor 2
    leituras_S2.clear()
        
    count_Leitura = Aux_Leitura
        
    # Salva na lista correspondente em qual leitura o sistema se encontra
    lista_count_Leitura.append(Aux_Leitura)
    
    # Fim do while dos passos    
    # Decrementar variável de trava do while da camada
    
'''
    Salva os dados necessários para um dataframe    
'''

lista_Leitura_df = pd.DataFrame(lista_count_Leitura, columns=['Amostra']) # Salva a lista com o número de leituras corridas
lista_Media_S1_df = pd.DataFrame(lista_Media_S1, columns=['Media S1'])   # Salva a lista com a média do sensor 1
lista_Media_S2_df = pd.DataFrame(lista_Media_S2, columns=['Media S2'])   # Salva a lista com a média do sensor 2

df_data = lista_Leitura_df                  # Salva a lista de leituras para uma Data Frame
df_data = df_data.join(lista_Media_S1_df)   # Anexa à lista de médias do sensor 1 ao data frame criado
df_data = df_data.join(lista_Media_S2_df)   # Anexa à lista de médias do sensor 2 ao data frame criado
    
'''
    Salva um dataframe para excel
'''
    
# Cria o parâmetro para escrita contendo o diretório e o formato
writer = pd.ExcelWriter('/home/pi/Desktop/Projeto_Teste_Sensor/Arquivos/ leituras_Analise.xlsx, engine = 'xlsxwriter')
    
# Indica qual dataframe será exportado e para qual nome de planilha
df_data.to_excel(writer, index = True, sheet_name = 'leituras')
    
# Salva a planilha com os parâmetros escolhidos
workboot = writer.bookworksheet = writer.sheets['leituras']
writer.save()
