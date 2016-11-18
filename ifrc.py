"""
Projeto de pesquisa do mestrado de H. S. Oliveira, tambem registrado no 
Instituto Federal de Rondonia - Campus Ariquemes. Este codigo controla 
um carro robo feito em Arduino com objetivo de promover um experimento 
didatico no ensino do Movimento Retilineo Uniformemente Variado (MRUV).
A comunicacao e feita atraves de um modulo bluetooth. O usuario 
seleciona a porta de comunicacao com o carro e entao utiliza as funcoes 
para realizar demonstracoes em sala de aula.
"""
import time
import serial
import serial.tools.list_ports
from cursesmenu import *
from cursesmenu.items import *
import unicodedata
import plotly 
from plotly.graph_objs import Scatter, Layout

class IFRCMenu:
	"""
	Esta classe realiza o controle da interface grafica 
	"""
	def __init__(self):
		self.ifrc = IFRC()
		titulo = " IFRC: Carro robo para Ensino de Fisica - Instituto Federal de Rondonia - Campus Ariquemes (v1.0.0)"
		self.menuPrincipal = CursesMenu(titulo, "H. S. Oliveira <heleno.oliveira@ifro.edu.br> e N. A. V. Simoes <natanael.simoes@ifro.edu.br>", False)
		self.menuPortas = CursesMenu(titulo, "Selecione a porta onde o carro esta conectado", False)
		self.criarItensPortas()
		self.menuPrincipal.append_item(SubmenuItem("Selecionar porta de comunicacao", self.menuPortas, self.menuPrincipal))
		self.menuPrincipal.append_item(FunctionItem("Movimento Retilineo Uniforme", self.ifrc.velocidadeMedia))
		self.menuPrincipal.append_item(FunctionItem("Movimento Retilineo Uniformemente Variada", self.ifrc.velocidadeVariada))
		self.menuPrincipal.append_item(ExitItem("Sair"))
		self.menuPrincipal.show()
	
	def criarItensPortas(self):
		itens = []
		for ser in self.ifrc.listarPortas():
			nome = "{0} - {1}".format(ser.device, strip_accents(ser.description[0:-6]))
			self.menuPortas.append_item(FunctionItem(nome, self.selecionarPorta, [ser.device]))
		self.menuPortas.append_item(ExitItem("Voltar", self.menuPortas))	
		
	def selecionarPorta(self, porta):
		print("Tentativa de comunicacao com o carro na porta {0}...".format(porta))
		try:
			self.ifrc.selecionarPorta(porta)
			print("Carro conectado! Pressione ENTER para continuar...")
			input()
		except:
			print("O carro nao esta conectado nesta porta, pressione ENTER para continuar...")
			input()
		if self.ifrc.conectado:
				self.menuPrincipal.selected_item.text = "Selecionar porta de comunicacao (Conectado em {0})".format(porta)
				self.menuPortas.exit()
		else:
			self.menuPrincipal.selected_item.text = "Selecionar porta de comunicacao"
		
class IFRC:
	"""
	Esta classe realiza o controle da porta serial para comunicar com o carro
	"""
	velocidadeMinima = 17
	velocidadeMaxima = 71
	tempoMaximo = 99
	
	def __init__(self):
		self.porta = ''
		self.dispositivo = None
		self.velocidadeSerial = 9600
		self.conectado = False
		self.velocidadeSerialMedia = 0
		self.variacaoTempo = []
		self.variacaoDistancia = []
		self.variacaoVelocidade = []
		self.aceleracao = 0
		
	def listarPortas(self):
		return serial.tools.list_ports.comports()		
		
	def selecionarPorta(self, porta):
		self.conectado = False
		self.dispositivo = serial.Serial(porta, self.velocidadeSerial, timeout=1, write_timeout=1)
		self.dispositivo.write(str.encode("T"))
		resposta = ""
		while(resposta == ""):
			resposta = str(self.dispositivo.readline())[2:-5]
		self.conectado = True
		return True
		
	def velocidadeMedia(self):
		if self.conectado:
			cmdV = input("Velocidade em cm/s [{0} - {1}, 0 para cancelar]: ".format(self.velocidadeMinima, self.velocidadeMaxima))
			if cmdV != '0':
				cmdT = input("Tempo em segundos [1 - {0}]: ".format(self.tempoMaximo));
				if self.validarVelocidade(cmdV, cmdT):
					self.enviarComandoVM(cmdV, cmdT)
					self.escutarRespostaVM(int(cmdT))
				input("\nPressione ENTER para continuar...")
		else:
			print("Conexao com o carro nao foi inicializada, selecione uma porta de comunicacao.")
			input("\nPressione ENTER para continuar...")
	
	def velocidadeVariada(self):
		if self.conectado:
			cmdV = input("Velocidade em cm/s [{0} - {1}, 0 para cancelar]: ".format(self.velocidadeMinima, self.velocidadeMaxima))
			if cmdV != '0':
				cmdA = input("Aceleração em cm/s²: ")
				cmdT = input("Tempo em segundos [1 - {0}]: ".format(self.tempoMaximo));
				if self.validarAceleracao(cmdV, cmdT, cmdA):
					self.enviarComandoVV(cmdV, cmdA, cmdT)
					self.escutarRespostaVV(int(cmdT), int(cmdA), int(cmdV))
				input("\nPressione ENTER para continuar...")
		else:
			print("Conexao com o carro nao foi inicializada, selecione uma porta de comunicacao.")
			input("\nPressione ENTER para continuar...")
			
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
		self.dispositivo.write(str.encode("A{0},{1},{2}".format(t.zfill(2),v,a.zfill(2))))
		time.sleep(0.5) # tempo para aguardar processamento
	
	def escutarRespostaVV(self, cmdT, cmdA, cmdV):
		i = 0; t = 0; deltaD = 0; v = 0;
		self.variacaoDistancia.clear()
		self.variacaoTempo.clear()
		self.variacaoVelocidade.clear()
		while i <= cmdT: 
			dadosRecebidos = str(self.dispositivo.readline())[2:-5]
			if (dadosRecebidos != ""):
				dadosProcessados = dadosRecebidos.split(",")
				v = float(dadosProcessados[0])
				t = float(dadosProcessados[1])
				deltaD = (cmdV * t) + (cmdA * pow(t, 2) / 2)
				print("Velocidade: ", str(v), " cm/s, Tempo: ", str(t), "s, Distancia percorrida: ", str(deltaD), "cm")
				self.variacaoTempo.append(t)
				self.variacaoDistancia.append(deltaD)
				self.variacaoVelocidade.append(v)
				i += 1
			time.sleep(1) # aguardando chegar mais respostas
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
		self.dispositivo.write(str.encode("V{0},{1}".format(t.zfill(2),v)))
		time.sleep(0.5) # tempo para aguardar processamento
		
	def escutarRespostaVM(self, cmdT):
		i = 0; t = 0; deltaD = 0; v = 0;
		self.variacaoDistancia.clear()
		self.variacaoTempo.clear()
		self.variacaoVelocidade.clear()
		while i <= cmdT: 
			dadosRecebidos = str(self.dispositivo.readline())[2:-5]
			if (dadosRecebidos != ""):
				dadosProcessados = dadosRecebidos.split(",")
				v = float(dadosProcessados[0])
				t = float(dadosProcessados[1])
				if t != 0:
					deltaD += v
				print("Velocidade: ", str(v), " cm/s, Tempo: ", str(t), "s, Distancia percorrida: ", str(deltaD), "cm")
				self.variacaoTempo.append(t)
				self.variacaoDistancia.append(deltaD)
				self.variacaoVelocidade.append(v)
				i += 1
			time.sleep(1) # aguardando chegar mais respostas
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
