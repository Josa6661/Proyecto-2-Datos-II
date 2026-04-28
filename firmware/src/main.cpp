#include <Arduino.h>

// --- PINES ---
const int IN1 = 11; const int IN2 = 12; // Motor Derecho
const int IN3 = 13; const int IN4 = 14; // Motor Izquierdo
const int SENSOR_IZQ = 4; const int SENSOR_DER = 5;

volatile int pasosIzq = 0;
volatile int pasosDer = 0;

void IRAM_ATTR contarPasoIzq() { pasosIzq++; }
void IRAM_ATTR contarPasoDer() { pasosDer++; }

void detener() {
  digitalWrite(IN1, LOW); digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
  delay(500); // Pausa para estabilizar la inercia
}

void avanzar(float cm) {
  int objetivo = cm / 1.021;
  pasosIzq = 0; pasosDer = 0;
  digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
  while (pasosIzq < objetivo && pasosDer < objetivo) { delay(5); }
  detener();
}

void girar90() {
  // Ajusta este valor (12) si ves que le falta o le sobra giro
  int objetivoGiro = 12; 
  pasosIzq = 0; pasosDer = 0;
  // Giro sobre eje: Derecha atrás, Izquierda adelante
  digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
  while (pasosIzq < objetivoGiro && pasosDer < objetivoGiro) { delay(5); }
  detener();
}

void setup() {
  Serial.begin(115200);
  pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);
  pinMode(SENSOR_IZQ, INPUT); pinMode(SENSOR_DER, INPUT);
  attachInterrupt(digitalPinToInterrupt(SENSOR_IZQ), contarPasoIzq, RISING);
  attachInterrupt(digitalPinToInterrupt(SENSOR_DER), contarPasoDer, RISING);

  delay(3000); // Tiempo para ponerlo en el suelo

  for (int i = 0; i < 4; i++) {
    avanzar(50); // Lado del cuadrado
    girar90();   // Esquina
  }
}

void loop() {}