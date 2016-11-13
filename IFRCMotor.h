/**
 * Classe de controle individual dos motores
 */
#ifndef IFRCMotor_h
#define IFRCMotor_h

#include "Arduino.h"
#include "IFRCConsts.h"

class IFRCMotor 
{
  private:
    int pinoMA; // Pino de entrada
    int pinoMB; // Pino terra
    int pinoMV; // Pino de controle de velocidade
    uint8_t velocidadeParaTensao(int v); // Converte a velocidade digitada pelo usuario 
                                         // para a tensao que impulsionara o carro nesta
                                         // velocidade (modelo numerico e uma regressao
                                         // polinomial de terceira ordem com base em
                                         // experimentos controlados)
  public:
    IFRCMotor(int pinoMA, int pinoMB, int pinoMV); // Configura os pinos do Arduino para
                                                   // controlar o motor adequadamente
    uint8_t mover(int v); // Move o motor em uma direcao desejada
    void parar(); // Para a rotacao do motor completamente
};
  
#endif
