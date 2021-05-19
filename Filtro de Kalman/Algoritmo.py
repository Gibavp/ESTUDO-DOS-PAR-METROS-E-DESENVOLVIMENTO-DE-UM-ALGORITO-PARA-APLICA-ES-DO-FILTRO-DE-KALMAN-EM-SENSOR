# -*- coding: utf-8 -*-

# Importação das bibliotecas
import numpy
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as m

# Leitura do arquivo com os dados
df = pd.read_excel("leituras_Analise.xlsx")

# Transformação dos dados do arquivo para lista
MedidoS1 = df['Media S1'].tolist()
MedidoS2 = df['Media S2'].tolist()
amostra= df['Amostra'].tolist()

# Implementação do filtro linear de Kalman
class Filtro_Kalman_Linear:
  def __init__(self,_F, _B, _H, _x, _P, _Q, _R):
    self.F = _F                         # Matriz de transição de estados
    self.B = _B                         # Matriz de controle.
    self.H = _H                         # Matriz de observação
    self.estado_estimado_atual = _x     # Estado inicial estimado
    self.estado_estimado_em_teste = _P  # Matriz de variância de estado
    self.Q = _Q                         # Matriz de variância de processo
    self.R = _R                         # Matriz de variância de medição
  def GetCurrentState(self):
    return self.estado_estimado_atual
  def Step(self,vetor_controle,vetor_medicao):
    #--------------------------- Predição -----------------------------
    estimativa_estado_previsto = self.F * self.estado_estimado_atual + self.B * vetor_controle
    estimativa_estado_em_teste = (self.F * self.estado_estimado_em_teste) * numpy.transpose(self.F) + self.Q
    #-------------------------- Observação ----------------------------
    atualizacao = vetor_medicao - self.H*estimativa_estado_previsto
    covariancia_atualizada = self.H*estimativa_estado_em_teste*numpy.transpose(self.H) + self.R
    #-------------------------- Atualização ---------------------------
    ganho_Kalman = estimativa_estado_em_teste * numpy.transpose(self.H) * numpy.linalg.inv(covariancia_atualizada)
    self.estado_estimado_atual = estimativa_estado_previsto + ganho_Kalman * atualizacao
    # Precisamos do tamanho da matriz para que possamos fazer uma matriz de identidade
    tamanho = self.estado_estimado_em_teste.shape[0]
    # eye(n) = nxn matriz de identidade
    self.estado_estimado_em_teste = (numpy.eye(tamanho)-ganho_Kalman*self.H)*estimativa_estado_em_teste


# Definição dos parâmetros do filtro
F = numpy.matrix([1])
B = numpy.matrix([1])
H = numpy.matrix([1])
Q = numpy.matrix([1])
R = numpy.matrix([0.0001])
xhat = numpy.matrix([100])
P    = numpy.matrix([0.001])

# Instanciação do filtro
filter = Filtro_Kalman_Linear(F,B,H,xhat,P,Q,R)

# Criação do vetor para atualização dos dados filtrados
kalman = []

# Laço de repetição para atualização do filtro
for i in range(2600):
    kalman.append(filter.GetCurrentState()[0,0])
    filter.Step(numpy.matrix([0]),df.loc[i,'Media S1'])


# Definição dos nomes dos eixos do gráfico
pparam = dict(xlabel='Nº Amostras [1]', ylabel='Distância Medida [mm]')

# Código para gerar o gráfico em formato ciêntifico e para exportação dos arquivos
with plt.style.context(['science', 'grid', 'no-latex']):
    fig, ax = plt.subplots()
    ax.plot(amostra, MedidoS1,'tab:blue', label='Sem filtro')
    ax.plot(amostra, kalman, 'tab:red', label='Com filtro')
    ax.legend(title='Sinal:', fontsize='small')
    ax.autoscale(tight=True)
    ax.set(**pparam)
    fig.savefig('Filtro_S1.pdf')
    fig.savefig('Filtro_S1.jpg', dpi=300)