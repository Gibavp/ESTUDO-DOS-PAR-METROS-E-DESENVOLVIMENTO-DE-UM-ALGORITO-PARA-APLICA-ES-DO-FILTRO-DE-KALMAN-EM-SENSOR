'''
    Código desenvolvido para o TCC conjunto entre Gilberto Vicente Prandi e 
    Victor Zanéli Silva sob a orientação dos professores Dr. Muriell de Rodrigues e Freire
    e Me. Raul Gaspari Santos com o título de Desenvolvimento de um protótipo portátil low cost 
    para inspeção de peças cilíndricas, utilizando tecnologias opensource.
'''

'''
    Biliotecas: O trecho abaixo tem por objetivo importar as bibliotecas externas ao python 
    que foram utilizadas no decorrer desse trabalho.

    - time: Utilizada para usar delays
    - board: Utilizada para acessar as portas do raspberry pi
    - DigitalInOut: Utilizada para declarar os pinos do raspberry pi como saída e entrada
    - VL53L0X: Utilizada para controloar os sensores de tempo de voo infravermelhos 
    - pandas: Manipulação e análise de dados
    - numpy: Utilizado para trabalho com matrizes e arrays
    - statistics: Biblioteca utilizada para trabalho com pacotes estatísticos  
'''

from datetime import datetime

print("\nProcesso Inicializado!")
print(datetime.today())

#============================= Bibliotecas =============================
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

#======================== Variáveis para sensor ========================
      
NORMAL_MODE = 33000 # Peíodo de pulsação do laser = 33 ms
HIGH_SPEED = 20000 # Peíodo de pulsação do laser reduzido = 33 ms
HIGH_ACCURACY = 200000 # Peíodo de pulsação do laser incrementado = 200 ms
vl53 = [] # Declararação do atributo sensor

#======================= Variáveis para leitura ========================
 
count_Leitura = 10 # Número de vezes que cada sensor fará a leitura
Aux_Leitura = count_Leitura
count_Passo = 200 # Quantidade de passos do motor responsável pelo giro
Aux_Passo = count_Passo
count_Camada = 30 # Quantidade de camadas a percorrer
ajuste_count_Passo = count_Passo
ajuste_count_Camada = count_Camada
media_S1 = 0
media_S2 = 0
media_S3 = 0
leituras_S1 = []
leituras_S2 = []
leituras_S3 = []
lista_Media_S1 = []
lista_Media_S2 = []
lista_Media_S3 = []
lista_count_Passo = []
lista_count_Camada = []
df_data = pd.DataFrame()

'''
    Setup dos pinos e declaração de endereçamento I2C para controle dos sensores
'''

#======================= Setup dos pinos I2C e digitais ========================

i2c_address = board.I2C() # Recebe o endereço I2C da placa
delay.sleep(0.5)
xshut = [DigitalInOut(board.D17), DigitalInOut(board.D22), DigitalInOut(board.D27)] # Seta os pinos digitais para controle

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

#======================= Void Loop ========================

# While das camadas
while count_Camada:
    #print('\nCamada: {}\n'.format(count_Camada))
    # While dos Passos
    while count_Passo:
        #print('\nPasso: {}\n'.format(count_Passo))
        # While das leituras
        while count_Leitura:
            for index, sensor in enumerate(vl53):
                # Apresentação das leituras em tela
                #print('Sensor {} Range: {}mm'.format(index + 1, sensor.range))
                
                # Separação dos dados lidos por sensor
                # Sensor 1
                if (index + 1) == 1:
                    leituras_S1.append(sensor.range)
                # Sensor 2
                if (index + 1) == 2:
                    leituras_S2.append(sensor.range)
                # Sensor 3
                if (index + 1) == 3:
                    leituras_S3.append(sensor.range)
                                                    
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

        # Cálculo das médias do sensor S3
        media_S3 = mean(leituras_S3)
        # Adição da média do sensor 3 da lista correspondente
        lista_Media_S3.append(media_S3)

        # Limpeza da lista do sensor 1
        leituras_S1.clear()
            
        # Limpeza da lista do sensor 2
        leituras_S2.clear()

        # Limpeza da lista do sensor 3
        leituras_S3.clear()

        # Salva na lista correspondente em qual passo o sistema se encontra
        lista_count_Passo.append(ajuste_count_Passo - count_Passo + 1)
    
        # Salva na lista correspondente em qual camada o sistema se encontra
        lista_count_Camada.append(ajuste_count_Camada - count_Camada + 1)
        
        # Decrementar variável de trava do while dos passos
        count_Passo -= 1
        
        count_Leitura = Aux_Leitura
        
    # Fim do while dos passos
    
    # Decrementar variável de trava do while da camada
    count_Camada -= 1
    
    count_Passo = Aux_Passo
    
    '''
        Salva os dados necessários para um dataframe    
    '''

    lista_Camada_df = pd.DataFrame(lista_count_Camada, columns=['Camada'])
    lista_Passo_df = pd.DataFrame(lista_count_Passo, columns=['Passo'])
    lista_Media_S1_df = pd.DataFrame(lista_Media_S1, columns=['Media S1'])
    lista_Media_S2_df = pd.DataFrame(lista_Media_S2, columns=['Media S2'])
    lista_Media_S3_df = pd.DataFrame(lista_Media_S3, columns=['Media S3'])

    df_data = lista_Camada_df
    df_data = df_data.join(lista_Passo_df)
    df_data = df_data.join(lista_Media_S1_df)
    df_data = df_data.join(lista_Media_S2_df)
    df_data = df_data.join(lista_Media_S3_df)
    
    '''
        Salva um dataframe para excel
    '''
    
    # Cria o parametro para escrita
    writer = pd.ExcelWriter('/home/pi/Desktop/Projeto_Teste_Sensor/Arquivos/leituras1.xlsx', engine = 'xlsxwriter')
    
    # Salva o arquivo para excel
    df_data.to_excel(writer, index = True, sheet_name = 'leituras')
    
    # Salva a planilha
    workboot = writer.bookworksheet = writer.sheets['leituras']
    writer.save()

print("\nProcesso Finalizado!")
print(datetime.today())