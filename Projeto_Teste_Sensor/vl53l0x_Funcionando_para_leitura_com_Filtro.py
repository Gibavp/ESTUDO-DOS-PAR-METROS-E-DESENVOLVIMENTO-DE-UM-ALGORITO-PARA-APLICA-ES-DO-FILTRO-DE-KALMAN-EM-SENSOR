#!/usr/bin/env python
#-*- coding: utf-8 -*-

'''
    Código desenvolvido para o TCC conjunto entre Gilberto Vicente Prandi e 
    Victor Zanéli Silva sob a orientação dos professores Dr. Muriell de Rodrigues e Freire
    e Me. Raul Gaspari Santos com o título de Desenvolvimento de um protótipo portátil low cost 
    para inspeção de peças cilíndricas, utilizando tecnologias opensource.
    
    Esse algoritmo backend tem por finalidade ler os 'n' sensores VL53L0x e aplicar um filtro de
    Kalman a sua saída, salvando a posteriori em um arquivo Excel.
'''

'''
    Biliotecas: O trecho abaixo tem por objetivo importar as bibliotecas externas ao python 
    que foram utilizadas no decorrer desse trabalho.

    - time: Utilizada para usar delays;
    - board: Utilizada para acessar as portas do raspberry pi;
    - DigitalInOut: Utilizada para declarar os pinos do raspberry pi como saída e entrada;
    - VL53L0X: Utilizada para controloar os sensores de tempo de voo infravermelhos;
    - pandas: Manipulação e análise de dados;
    - numpy: Utilizado para trabalho com matrizes e arrays;
    - statistics: Biblioteca utilizada para trabalho com pacotes estatísticos;
    - pykalman: Responsável pela aplicação do filtro de kalman.
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
import statistics as stat
from pykalman import KalmanFilter

#======================== Variáveis para sensor ========================
      
#NORMAL_MODE = 33000 # Peíodo de pulsação do laser = 33 ms
#HIGH_SPEED = 20000 # Peíodo de pulsação do laser reduzido = 33 ms
HIGH_ACCURACY = 200000 # Peíodo de pulsação do laser incrementado = 200 ms
vl53 = [] # Declararação do atributo sensor

#======================= Variáveis para leitura ========================
 
count_Leitura = 10 # Número de vezes que cada sensor fará a leitura para média
count_Passo = 1 # Quantidade de passos do motor responsável pelo giro
count_Camada = 130  # Quantidade de camadas a percorrer
diametro_padrao = 0 # Diâmetro padrão informado pelo usuário

camada_util = 100
offset_S1 = 0
offset_S2 = 1
offset_S3 = 2

Aux_Camada = count_Camada
Aux_Leitura = count_Leitura
Aux_Passo = count_Passo
ajuste_count_Passo = count_Passo
ajuste_count_Camada = count_Camada
leituras_S1 = []
leituras_S2 = []
leituras_S3 = []
lista_Media_S1 = []
lista_Media_S2 = []
lista_Media_S3 = []
lista_count_Passo = []
lista_count_Camada = []
df_data = pd.DataFrame()

#===================== Definição dos limites de leitura ======================
S1_inicial = Aux_Camada - offset_S1
S1_final = Aux_Camada - camada_util - offset_S1
S2_inicial = Aux_Camada - offset_S2
S2_final = Aux_Camada - camada_util - offset_S2
S3_inicial = Aux_Camada - offset_S3
S3_final = Aux_Camada - camada_util - offset_S3

#===================== Instância Filtro de Kalman ======================
kf = KalmanFilter(transition_matrices = [1],
                  observation_matrices = [1],
                  initial_state_mean = diametro_padrao,
                  initial_state_covariance = 0.001,
                  observation_covariance = 1,
                  transition_covariance = .0001)

#======================= Setup dos pinos I2C e digitais ========================

i2c_address = board.I2C() # Recebe o endereço I2C da placa
delay.sleep(0.5)
xshut = [DigitalInOut(board.D17), DigitalInOut(board.D22), DigitalInOut(board.D27)] # Seta os pinos digitais para controle
delay.sleep(0.2)

#======================= Desligamento dos sensores =======================

for power_pin in xshut:
    power_pin.switch_to_output(value=False)
    delay.sleep(0.2)

'''
    Teste de hardware e pareamento dos sensores
'''

for i, power_pin in enumerate(xshut):
    power_pin.value = True # Ligando o sensor número 'i'
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
                if ((index + 1) == 1) and (count_Camada < S1_inicial) and (count_Camada >= S1_final):
                    leituras_S1.append(sensor.range)
                # Sensor 2
                if (index + 1) == 2 and (count_Camada < S2_inicial) and (count_Camada >= S2_final): 
                    leituras_S2.append(sensor.range)
                # Sensor 3
                if (index + 1) == 3 and (count_Camada < S3_inicial) and (count_Camada >= S3_final):
                    leituras_S3.append(sensor.range)
                                                    
            # Decrementar variável de trava do while
            count_Leitura -= 1
        
        # Fim do while das leituras
        
        # Transformação do array do S1, S2 e S3 em Serie para utilizar o filtro de kalman
        leituras_S1_S = pd.Series(leituras_S1)
        leituras_S2_S = pd.Series(leituras_S2)
        leituras_S3_S = pd.Series(leituras_S3)
    
        # Aplica o filtro de kalman para S1, S2 e S3 em cada condicional
        # Aplica Médias móveis e transição para Serie para S1, S2 e S3 em cada condicional
        # Cálculo das médias do sensor S1, S2 e S3 em cada condicional
        # Adição da média de S1, S2 e S3 as listas correspondentes 
        # Limpeza das listas e séries dos sensores 1, 2 e 3
        
        if (count_Camada < S1_inicial) and (count_Camada >= S1_final):
            state_mean_S1, _ = kf.filter(leituras_S1_S.values)
            filtro_S1_S = pd.Series(state_mean_S1.flatten(), index=leituras_S1_S.index)
            media_S1 = stat.mean(filtro_S1_S)
            lista_Media_S1.append(media_S1)
            media_S1 = 0
            leituras_S1.clear()
            state_mean_S1 = []
            filtro_S1_S.drop(axis=0, inplace=True, index=filtro_S1_S.index)
            
        if (count_Camada < S2_inicial) and (count_Camada >= S2_final):
            state_mean_S2, _ = kf.filter(leituras_S2_S.values)
            filtro_S2_S = pd.Series(state_mean_S2.flatten(), index=leituras_S2_S.index)
            media_S2 = stat.mean(filtro_S2_S)
            lista_Media_S2.append(media_S2)
            media_S2 = 0
            leituras_S2.clear()
            state_mean_S2 = []
            filtro_S2_S.drop(axis=0, inplace=True, index=filtro_S2_S.index)
        
        if (count_Camada < S3_inicial) and (count_Camada >= S3_final):
            state_mean_S3, _ = kf.filter(leituras_S3_S.values)
            filtro_S3_S = pd.Series(state_mean_S3.flatten(), index=leituras_S3_S.index)
            media_S3 = stat.mean(filtro_S3_S)
            lista_Media_S3.append(media_S3)
            media_S3 = 0
            leituras_S3.clear()
            state_mean_S3 = []
            filtro_S3_S.drop(axis=0, inplace=True, index=filtro_S3_S.index)            
       
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
    writer = pd.ExcelWriter('/home/pi/Downloads/[NÃO ALTERAR] - Em funcionamento.../Projeto_Teste_Sensor/Arquivos/leitura4.xlsx', engine = 'xlsxwriter')
    
    # Salva o arquivo para excel
    df_data.to_excel(writer, index = True, sheet_name = 'leituras')
    
    # Salva a planilha
    workboot = writer.bookworksheet = writer.sheets['leituras']
    writer.save()

print("\nProcesso Finalizado!")
print(datetime.today())