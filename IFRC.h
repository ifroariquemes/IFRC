/**
 * Classe de controle de requisicoes e motores do carro
 */
#ifndef IFRC_h
#define IFRC_h

#include "Arduino.h"
#include "IFRCConsts.h"
#include "IFRCMotor.h"

class IFRC
{
  private:
    String _requisicao; // Armazena cada requisicao que chega pela porta serial
    IFRCMotor _motoresEsquerda;
    IFRCMotor _motoresDireita;
  public:
    IFRC(); // Ao instanciar objeto da classe inicializa os motores
    void testarMotores(); // Realiza teste para verificar se os motores estao funcionando (teste apenas visual)
    void velocidadeMedia(); // Experimento de velocidade media
    void processarComandos(); // Processamento de requisicoes
};

#endif

