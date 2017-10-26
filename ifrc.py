#!/usr/bin/env python
"""
Projeto de pesquisa do mestrado de H. S. Oliveira, tambem registrado no 
Instituto Federal de Rondonia - Campus Ariquemes. Este codigo controla 
um carro robo feito em Arduino com objetivo de promover um experimento 
didatico no ensino do Movimento Retilineo Uniformemente Variado (MRUV).
A comunicacao e feita atraves de um modulo WiFi. O usuario 
seleciona a porta de comunicacao com o carro e entao utiliza as funcoes 
para realizar demonstracoes em sala de aula.

Python 2.7
"""
import socket
import time
from cursesmenu import *
from cursesmenu.items import *
import unicodedata
import plotly 
from plotly.graph_objs import Scatter, Layout

TCP_IP = '192.168.4.1'
TCP_PORT = 9000
BUFFER_SIZE = 1024

class IFRCMenu:
	"""
	Esta classe realiza o controle da interface grafica 
	"""
	def __init__(self):
		self.ifrc = IFRC()
		titulo = " IFRC: Carro robo para Ensino de Fisica - Instituto Federal de Rondonia - Campus Ariquemes (v1.0.0)"
		self.menuPrincipal = CursesMenu(titulo, "H. S. Oliveira <heleno.oliveira@ifro.edu.br> e N. A. V. Simoes <natanael.simoes@ifro.edu.br>", False)
		self.menuPrincipal.append_item(FunctionItem("Movimento Retilineo Uniforme", self.ifrc.velocidadeMedia))
		self.menuPrincipal.append_item(FunctionItem("Movimento Retilineo Uniformemente Variada", self.ifrc.velocidadeVariada))
		self.menuPrincipal.append_item(ExitItem("Sair"))
		self.menuPrincipal.show()
		
class IFRC:
	"""
	Esta classe realiza o controle da socket TCP para comunicar com o carro
	"""
	velocidadeMinima = 17
	velocidadeMaxima = 71
	tempoMaximo = 99
	
	def __init__(self):
		self.porta = ''
		self.dispositivo = None
		self.conectado = False
		self.velocidadeSerialMedia = 0
		self.variacaoTempo = []
		self.variacaoDistancia = []
		self.variacaoVelocidade = []
		self.aceleracao = 0
		self.criarConexao()
	
	def __del__(self):
		self.dispositivo.close()
	
	def criarConexao(self):
		try:
			self.dispositivo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.dispositivo.connect((TCP_IP, TCP_PORT))
			self.conectado = True
		except:
			print "Conexao com o carro nao foi estabelecida."
			exit()
		
	def velocidadeMedia(self):
		cmdV = raw_input("Velocidade em cm/s [{0} - {1}, 0 para cancelar]: ".format(self.velocidadeMinima, self.velocidadeMaxima))
		if cmdV != "0":	
			cmdT = raw_input("Tempo em segundos [1 - {0}]: ".format(self.tempoMaximo));
			if self.validarVelocidade(cmdV, cmdT):
				self.enviarComandoVM(cmdV, cmdT)
				self.escutarRespostaVM(int(cmdV), int(cmdT))
			raw_input("\nPressione ENTER para continuar...")	
		
	def velocidadeVariada(self):	
		cmdV = raw_input("Velocidade em cm/s [{0} - {1}, 0 para cancelar]: ".format(self.velocidadeMinima, self.velocidadeMaxima))
		if cmdV != '0':
			cmdA = raw_input("Aceleracao em cm/s2: ")
			cmdT = raw_input("Tempo em segundos [1 - {0}]: ".format(self.tempoMaximo));
			if self.validarAceleracao(cmdV, cmdT, cmdA):
				self.enviarComandoVV(cmdV, cmdA, cmdT)
				self.escutarRespostaVV(int(cmdT), int(cmdA), int(cmdV))
			raw_input("\nPressione ENTER para continuar...")
			
	def validarVelocidade(self, v, t):
		try:
			v = int(v)
			t = int(t)
			valido = v >= self.velocidadeMinima and v <= self.velocidadeMaxima and t >= 1 and t <= self.tempoMaximo
			if not valido:
				print("A entrada nao obedeceu aos valores minimos e maximos.")
				return False
			return True
		except:
			print("Tempo e Velocidade precisam ser numeros inteiros.")
			return False
			
	def validarAceleracao(self, v, t, a):
		if self.validarVelocidade(v, t):
			v = int(v)
			t = int(t)
			try:
				a = int(a)
			except:
				print("Aceleracao precisa ser um numero inteiro.")
				return False
			vtaMax = v + a * t
			if vtaMax > self.velocidadeMaxima:
				print("Esta entrada e invalida pois a velocidade final sera {0} cm/s, tente outros parametros.")
				return False
			return True
		else:
			return False
	
	def enviarComandoVV(self, v, a, t):
		self.dispositivo.send(str.encode("A{0},{1},{2}".format(str(t).zfill(2),v,str(a).zfill(2))))
	
	def escutarRespostaVV(self, cmdT, cmdA, cmdV):
		i = 0; t = 0; deltaD = 0; v = 0;
		del self.variacaoDistancia[:]
		del self.variacaoTempo[:]
		del self.variacaoVelocidade[:]
		while i <= cmdT: 
			v = float(cmdV + (cmdA * i))
			t = float(i)
			deltaD = (cmdV * t) + (cmdA * pow(t, 2) / 2)
			print 'Velocidade: {0} cm/s, Tempo: {1} s, Distancia percorrida: {2} cm'.format(str(v), str(t), str(deltaD))
			self.variacaoTempo.append(t)
			self.variacaoDistancia.append(deltaD)
			self.variacaoVelocidade.append(v)
			i += 1
			time.sleep(1)
		self.velocidadeMedia = deltaD / t
		self.aceleracao = self.variacaoVelocidade[1] - self.variacaoVelocidade[0]
		self.gerarGraficoVM()
		self.gerarGraficoVV()
		
	def gerarGraficoVV(self):
		print("Gerando grafico da variacao de velocidade...")	
		plotly.offline.plot({
			"data": [
				Scatter(x=self.variacaoTempo, y=self.variacaoVelocidade, name="A = {:.2f}cm/s".format(self.aceleracao))
			],
			"layout": Layout(title="IFRC - Variacao de Velocidade", xaxis = dict(title = 'Tempo (s)'), yaxis = dict(title = 'Velocidade (cm/s)'), showlegend=True)
		}, filename="mruv.html")
	
	def enviarComandoVM(self, v, t):
		self.dispositivo.send(str.encode("V{0},{1}".format(str(t).zfill(2),v)))
		
	def escutarRespostaVM(self, cmdV, cmdT):
		i = 0; t = 0; deltaD = 0; v = 0;
		del self.variacaoDistancia[:]
		del self.variacaoTempo[:]
		del self.variacaoVelocidade[:]
		while i <= cmdT: 
			v = float(cmdV)
			t = float(i)
			if t != 0:
				deltaD += v
			print 'Velocidade: {0} cm/s, Tempo: {1} s, Distancia percorrida: {2} cm'.format(str(v), str(t), str(deltaD))
			self.variacaoTempo.append(t)
			self.variacaoDistancia.append(deltaD)
			self.variacaoVelocidade.append(v)
			i += 1
			time.sleep(1)
		self.velocidadeMedia = deltaD / t
		self.gerarGraficoVM()
		
	def gerarGraficoVM(self):
		print("Gerando grafico da velocidade media...\n")	
		plotly.offline.plot({
			"data": [
				Scatter(x=self.variacaoTempo, y=self.variacaoDistancia, name="Vm = {:.2f}cm/s".format(self.velocidadeMedia))
			],
			"layout": Layout(title="IFRC - Velocidade Media", xaxis = dict(title = 'Tempo (s)'), yaxis = dict(title = 'Distancia (cm)'), showlegend=True)
		}, filename="mru.html")
			
def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')		
				  
ifrcMenu = IFRCMenu()