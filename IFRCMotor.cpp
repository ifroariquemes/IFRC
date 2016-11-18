#include "IFRCMotor.h"

IFRCMotor::IFRCMotor(int pinoMA, int pinoMB, int pinoMV){
  pinMode(pinoMA, OUTPUT); 
  pinMode(pinoMB, OUTPUT);
  pinMode(pinoMV, OUTPUT);
  this->pinoMA = pinoMA;
  this->pinoMB = pinoMB;
  this->pinoMV = pinoMV;
 }

uint8_t IFRCMotor::velocidadeParaTensao(int v) {
  if(v < V_MIN || v > V_MAX) {              // Valida se a velocidade esta dentro dos
    Serial.print("$Velocidade minima = ");  // limites fisicos de movimentacao do carro
    Serial.print(V_MIN);
    Serial.print(", maxima = ");
    Serial.println(V_MAX);
    return 0;
  }
  return round(-0.00109*pow(v, 3) + 0.15562*pow(v, 2) - 3.75401*v + 126.85373);
}

uint8_t IFRCMotor::mover(int v){
  uint8_t t = velocidadeParaTensao(v);
  digitalWrite(this->pinoMA, t > 0);
  digitalWrite(this->pinoMB, t < 0);
  analogWrite(this->pinoMV, t);
  return t;
}

void IFRCMotor::parar() {
  digitalWrite(this->pinoMA, LOW);
  digitalWrite(this->pinoMB, LOW);
}
