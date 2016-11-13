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
		self.menuPrincipal.append_item(FunctionItem("Velocidade media", self.ifrc.velocidadeMedia))
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
	def __init__(self):
		self.porta = ''
		self.dispositivo = None
		self.velocidade = 9600
		self.conectado = False
		
	def listarPortas(self):
		return serial.tools.list_ports.comports()		
		
	def selecionarPorta(self, porta):
		self.conectado = False
		self.dispositivo = serial.Serial(porta, self.velocidade, timeout=1, write_timeout=1)
		self.dispositivo.write(str.encode("T"))
		resposta = ""
		while(resposta == ""):
			resposta = str(self.dispositivo.readline())[2:-5]
		self.conectado = True
		return True
		
	def velocidadeMedia(self):
		if self.conectado:
			cmd_v = input("Velocidade em cm/s [17 - 71, 0 para cancelar]: ")
			if cmd_v != '0':
				cmd_t = input("Tempo em segundos [1 - 99]: ");
				if self.validarEntrada(cmd_v, cmd_t):
					self.enviarComandoVM(cmd_v, cmd_t)
					self.escutarRespostaVM(int(cmd_t))
				input("\nPressione ENTER para continuar...")
		else:
			print("Conexao com o carro nao foi inicializada, selecione uma porta de comunicacao.")
			input("\nPressione ENTER para continuar...")
			
	def validarEntrada(self, v, t):
		vMax = 71
		tMax = 99
		try:
			v = int(v)
			t = int(t)
			valido = v >= 17 and v <= vMax and t >= 1 and t <= tMax
			if not valido:
				print("A entrada nÃ£o obedeceu aos valores mÃ­nimos e mÃ¡ximos.")
				return False
			return True
		except:
			print("Tempo e Velocidade precisam ser nÃºmeros inteiros.")
			return False
			
	def enviarComandoVM(self, v, t):
		self.dispositivo.write(str.encode("V" + t.zfill(2) + "," + v));
		time.sleep(0.5) # tempo para aguardar processamento
		
	def escutarRespostaVM(self, tMax):
		i = 0; t = 0; deltaD = 0; v = 0; vMedia = 0
		vetorT = []; vetorDeltaD = []; vetorV = []
		while i <= tMax: 
			dadosRecebidos = str(self.dispositivo.readline())[3:-5]
			if (dadosRecebidos != ""):
				dadosProcessados = dadosRecebidos.split(",")
				v = int(dadosProcessados[0])
				t = int(dadosProcessados[1])
				if t != 0:
					deltaD += v
				print("Velocidade: ", str(v), " cm/s, Tempo: ", str(t), "s, DistÃ¢ncia percorrida: ", str(deltaD), "cm")
				vetorT.append(t)
				vetorDeltaD.append(deltaD)
				vetorV.append(v)
				i += 1
			time.sleep(1) # aguardando chegar mais respostas
		vMedia = deltaD / t
		self.gerarGraficoVM(vetorT, vetorDeltaD, vMedia)
		
	def gerarGraficoVM(self, vetorT, vetorDeltaD, vMedia):
		print("Gerando grÃ¡fico da corrida...\n")	
		plotly.offline.plot({
			"data": [
				Scatter(x=vetorT, y=vetorDeltaD, name="Vm = {:.2f}cm/s".format(vMedia))
			],
			"layout": Layout(title="IFRC", xaxis = dict(title = 'Tempo (s)'), yaxis = dict(title = 'DistÃ¢ncia (cm)'), showlegend=True)
		})
			
def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')		
				  
ifrcMenu = IFRCMenu()
