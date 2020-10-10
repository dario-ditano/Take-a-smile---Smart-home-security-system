#include <Arduino.h>
#include "mqtt.h"
#include "moviment.h"
#include "gas.h"



void setup()
{
  SetupMoviment();
  SetupGas();
  StartMqtt();
}

void loop()
{
  DetectorGas();
  DetectorMoviment();
  RunClient();
  
}
