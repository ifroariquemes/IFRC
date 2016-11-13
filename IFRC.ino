/**
 * IFRC.ino - Carro robo para Ensino de Fisica
 * 
 * H. S. Oliveira <heleno.oliveira@ifro.edu.br>
 * N. A. V Simoes <natanael.simoes@ifro.edu.br> http://github.com/natanaelsimoes/
 * 
 * 
 * Projeto de pesquisa do mestrado de H. S. Oliveira, tambem registrado no 
 * Instituto Federal de Rondonia - Campus Ariquemes. Este codigo controla 
 * um carro robo feito em Arduino com objetivo de promover um experimento 
 * didatico no ensino do Movimento Retilineo Uniformemente Variado (MRUV).
 * A comunicacao e feita atraves de um modulo bluetooth. O usuario 
 * seleciona a porta de comunicacao com o carro e entao utiliza as funcoes 
 * para realizar demonstracoes em sala de aula.
 *
 * Este carro usa os seguintes modulos para atingir os objetivos propostos:
 * - Bluetooth HC-05
 * - Ponte H L298N
 * - Sensor Sheild Keyes 5.0 
 * - 2x plhas de 3.7V em série
 * - 4x motores DC 12V
 * - Arduino Uno R3
 */
#include "IFRC.h"

IFRC ifrc;

void setup(){
  Serial.begin(9600);    // Inicializa comunicacao serial
  while(!Serial) { }     // e aguarda ate que seja estabelecida
  ifrc.testarMotores(); 
}

void loop() {
  ifrc.processarComandos(); // Sistema fica intermitentemente recebendo e respodendo a comandos
}
