#include "IFRC.h"

IFRC::IFRC(): _motoresEsquerda(P_MA_ESQ, P_MB_ESQ, P_MV_ESQ), _motoresDireita(P_MA_DIR, P_MB_DIR, P_MV_DIR){ }

void IFRC::testarMotores() {
  Serial.println("Iniciando teste de motores, verifique se estão funcionando corretamente.");
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
        Serial.println("$Este comando ainda não está implementado!");
        break;
      default:
        Serial.println("$Comando não reconhecido.");
        break;
    }
  }
}

void IFRC::velocidadeMedia() {
  // Formato da requisicao = "Vtt,vv" onde 
  // t = tempo em segundos, v = velocidade em centimetros por segundo
  uint8_t i = 0, r = 0;
  int t = this->_requisicao.substring(1,3).toInt();
  int v = this->_requisicao.substring(4).toInt();
  r = this->_motoresEsquerda.mover(v);
  if (r > 0) {
    this->_motoresDireita.mover(v);
    Serial.print(v);
    Serial.print(",");
    Serial.println(i);
    while(i < t) {
      i++;
      delay(1000);  
      Serial.print(v);
      Serial.print(",");
      Serial.println(i);
    }
  }
  this->_motoresEsquerda.parar();
  this->_motoresDireita.parar();
}
