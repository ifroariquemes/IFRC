#include "IFRC.h"

IFRC::IFRC(): _motoresEsquerda(P_MA_ESQ, P_MB_ESQ, P_MV_ESQ), _motoresDireita(P_MA_DIR, P_MB_DIR, P_MV_DIR){ }

void IFRC::testarMotores() {
  Serial.println("Iniciando teste de motores, verifique se estao funcionando corretamente.");
  delay(1000);
  this->_motoresEsquerda.mover(V_MAX); // Roda os motores com o maximo de potencia
  this->_motoresDireita.mover(V_MAX);
  delay(1000);
  this->_motoresEsquerda.parar();
  this->_motoresDireita.parar();
}

void IFRC::processarComandos() {
  if(Serial.available()) {
    this->_requisicao = Serial.readString();
    switch(this->_requisicao.charAt(0)) {
      case 'T': // teste de conexao
        Serial.println("1");
        break;
      case 'V': // velocidade media
        velocidadeMedia();
        break;
      case 'A': // velocidade uniformemente variada
        velocidadeVariada();
        break;
      default:
        Serial.println("$Comando nao reconhecido.");
        break;
    }
  }
}

void IFRC::velocidadeMedia() {
  // Formato da requisicao = "Vtt,vv" onde 
  // t = tempo em segundos, v = velocidade em centimetros por segundo
  uint8_t i = 0, r = 0;
  float t = this->_requisicao.substring(1,3).toFloat();
  float v = this->_requisicao.substring(4).toFloat();
  r = this->_motoresEsquerda.mover(v);
  if (r > 0) {
    this->_motoresDireita.mover(v);
    Serial.print(v);
    Serial.print(",");
    Serial.println((float)i);
    while(i < t) {
      i++;
      delay(1000);  
      Serial.print(v);
      Serial.print(",");
      Serial.println((float)i);
    }
  }
  this->_motoresEsquerda.parar();
  this->_motoresDireita.parar();
}

void IFRC::velocidadeVariada() {
  // Formato da requisicao = Att,vv,aa onde
  // t = tempo em segundos, v = velocidade inicial em centimetros por segundo,
  // a = aceleracao em centimetros por segundo ao quadrado
  uint8_t r = 0;
  float vAtual = 0, tAtualF = 0, sensibilidade = 100;
  uint16_t tAtual = 0, t = this->_requisicao.substring(1,3).toInt() * 1000;
  uint8_t vInicial = this->_requisicao.substring(4,6).toInt();
  uint8_t a = this->_requisicao.substring(7).toInt();
  r = this->_motoresEsquerda.mover(vInicial);
  if (r > 0) {
    for(tAtual = 0; tAtual <= t; tAtual += sensibilidade) {
      tAtualF = (float)tAtual / 1000;
      vAtual = vInicial + (a * tAtualF); // V = Vo + at
      this->_motoresEsquerda.mover(vAtual);
      this->_motoresDireita.mover(vAtual);
      if(tAtual % 1000 == 0) {
        Serial.print(vAtual);
        Serial.print(",");
        Serial.println(tAtualF);
      }     
      delay(sensibilidade);
    }
  }
  this->_motoresEsquerda.parar();
  this->_motoresDireita.parar();
}
