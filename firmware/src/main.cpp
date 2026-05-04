#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>

// --- CONFIGURACIÓN WIFI ---
const char* ssid = "Xiaomi_2405";
const char* password = "famqch0506";
WebServer server(80);

// --- CONFIGURACIÓN DE PINES ---
// Pines para el puente H (Control de motores)
const int IN1 = 11; const int IN2 = 12;
const int IN3 = 13; const int IN4 = 14;
const int SENSOR_IZQ = 4; const int SENSOR_DER = 5; // Pines para Encoders (Sensores de velocidad/pasos)
const int PIN_BUZZER = 15;

// Pines para Encoders (Sensores de velocidad/pasos)
volatile int pasosIzq = 0;
volatile int pasosDer = 0;
char orientacionActual = 'S';  // Estado de la brújula interna del robot

// --- FUNCIONES DE INTERRUPCIÓN ---
void IRAM_ATTR contarPasoIzq() { pasosIzq++; }
void IRAM_ATTR contarPasoDer() { pasosDer++; }

// Detiene todos los motores y aplica una pequeña pausa de estabilización
void detener() {
  digitalWrite(IN1, LOW); digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
  delay(500);
}

// --- FUNCIONES DE MOVIMIENTO CON DETECTOR DE ATASCO ---
// Mueve el robot hacia adelante una distancia específica en centímetros
void avanzar(float cm) {
  int objetivo = cm / 1.021; // Conversión de cm a pasos de encoder
  pasosIzq = 0; pasosDer = 0;
  
  unsigned long tiempoAtasco = millis();
  int tempIzq = 0; int tempDer = 0;

  digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);

  while (pasosIzq < objetivo || pasosDer < objetivo) { // Bucle de control: corre hasta alcanzar los pasos o detectar atasco
    if (pasosIzq >= objetivo) { digitalWrite(IN1, LOW); digitalWrite(IN2, LOW); }
    if (pasosDer >= objetivo) { digitalWrite(IN3, LOW); digitalWrite(IN4, LOW); }
    
    // Si algún sensor registra un paso, reiniciamos el cronómetro de atasco
    if (pasosIzq != tempIzq || pasosDer != tempDer) {
      tiempoAtasco = millis();
      tempIzq = pasosIzq; 
      tempDer = pasosDer;
    }
    
    // Si pasan 2 segundos sin dar NINGÚN paso, chocamos. Rompemos el ciclo.
    if (millis() - tiempoAtasco > 2000) {
      Serial.println("¡ATASCO DETECTADO EN AVANCE! Salvando WiFi...");
      break; 
    }
    delay(1); 
  }
  detener();
}
// Giro de 90 grados a la IZQUIERDA 
void girar90() {
  int objetivoIzq = 12; 
  pasosIzq = 0; pasosDer = 0;
  
  unsigned long tiempoAtasco = millis();
  int tempIzq = 0; int tempDer = 0;
  
  digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH);
  
  while (pasosIzq < objetivoIzq || pasosDer < objetivoIzq) { 
    if (pasosIzq >= objetivoIzq) { digitalWrite(IN1, LOW); digitalWrite(IN2, LOW); }
    if (pasosDer >= objetivoIzq) { digitalWrite(IN3, LOW); digitalWrite(IN4, LOW); }
    
    if (pasosIzq != tempIzq || pasosDer != tempDer) {
      tiempoAtasco = millis();
      tempIzq = pasosIzq; tempDer = pasosDer;
    }
    if (millis() - tiempoAtasco > 2000) {
      Serial.println("¡ATASCO EN GIRO IZQ! Salvando WiFi...");
      break;
    }
    delay(1);
  }
  detener(); 
}
// Giro de 90 grados a la DERECHA
void girar90Der() {
  int objetivoDer = 12; 
  pasosIzq = 0; pasosDer = 0;
  
  unsigned long tiempoAtasco = millis();
  int tempIzq = 0; int tempDer = 0;
  
  digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
  
  while (pasosIzq < objetivoDer || pasosDer < objetivoDer) { 
    if (pasosIzq >= objetivoDer) { digitalWrite(IN1, LOW); digitalWrite(IN2, LOW); }
    if (pasosDer >= objetivoDer) { digitalWrite(IN3, LOW); digitalWrite(IN4, LOW); }
    
    if (pasosIzq != tempIzq || pasosDer != tempDer) {
      tiempoAtasco = millis();
      tempIzq = pasosIzq; tempDer = pasosDer;
    }
    if (millis() - tiempoAtasco > 2000) {
      Serial.println("¡ATASCO EN GIRO DER! Salvando WiFi...");
      break;
    }
    delay(1); 
  }
  detener();
}

// --- LÓGICA DE RUTA ---
// Rutina de prueba: hace un cuadrado girando 4 veces a la derecha
void ejecutarRutina() {
  for (int i = 0; i < 4; i++) {
    girar90Der(); 
    delay(1000); 
  }
}
// Calcula los giros necesarios para cambiar de una orientación a otra
void apuntarHacia(char nuevaDir) {
  if (orientacionActual == nuevaDir) return; 
// Lógica para giro de 180 grados (sentidos opuestos)
  if ((orientacionActual == 'D' && nuevaDir == 'I') || (orientacionActual == 'I' && nuevaDir == 'D') ||
      (orientacionActual == 'S' && nuevaDir == 'B') || (orientacionActual == 'B' && nuevaDir == 'S')) {
    girar90(); girar90(); 
  }
  // Lógica para giro de 90 grados a la derecha
  else if ((orientacionActual == 'D' && nuevaDir == 'B') || (orientacionActual == 'B' && nuevaDir == 'I') ||
           (orientacionActual == 'I' && nuevaDir == 'S') || (orientacionActual == 'S' && nuevaDir == 'D')) {
    girar90Der();
  }
  else {
    girar90();
  }
  orientacionActual = nuevaDir;  // Actualiza la brújula interna
}
// Procesa una cadena de comando tipo "S2,D1,B3" (S=Subir, D=Derecha, B=Bajar...)
void ejecutarRutaDinamica(String ruta) {
  int indice = 0;
  while (indice < ruta.length()) {
    char direccion = ruta.charAt(indice); // Lee la letra (Dirección)
    indice++;
    
    String numStr = "";// Extrae el número de cuadros/pasos que sigue a la letra
    while (indice < ruta.length() && isDigit(ruta.charAt(indice))) {
      numStr += ruta.charAt(indice);
      indice++;
    }
    int cuadros = numStr.toInt();
    
    if (cuadros > 0) {
      Serial.print("Girando hacia: "); Serial.println(direccion);
      apuntarHacia(direccion);
      Serial.print("Avanzando cuadros: "); Serial.println(cuadros);
      for (int i = 0; i < cuadros; i++) {
        avanzar(30); // Cada "cuadro" equivale a 30cm
        delay(200);  
      }
    }
    if (indice < ruta.length() && ruta.charAt(indice) == ',') {
      indice++;
    }
  }
}

// --- SERVIDOR WEB ---
// Página principal con botón
void handleRoot() {
  String html = "<html><body><h1>Control Robot ESP32</h1>";
  html += "<button onclick=\"location.href='/arrancar'\" style='width:200px;height:100px;font-size:30px;'>ARRANCAR CUADRADO</button>";
  html += "</body></html>";
  server.send(200, "text/html", html);
}
// Recibe comandos de ruta por URL
void handleRuta() {
  if (server.hasArg("cmd")) {
    String comandos = server.arg("cmd");
    server.send(200, "text/plain", "OK"); // Libera la red antes de moverse
    ejecutarRutaDinamica(comandos);
  } else {
    server.send(400, "text/plain", "Error: Falta el parametro cmd");
  }
}

void setup() {
  Serial.begin(115200);
  delay(2000); 
  // Configuración de pines
  pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);
  pinMode(SENSOR_IZQ, INPUT); pinMode(SENSOR_DER, INPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  
  // Configuración de interrupciones para los encoders
  attachInterrupt(digitalPinToInterrupt(SENSOR_IZQ), contarPasoIzq, RISING);
  attachInterrupt(digitalPinToInterrupt(SENSOR_DER), contarPasoDer, RISING);

  // Conexión a la red WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.println("\n✓ Conectado a WiFi! IP: " + WiFi.localIP().toString());

  // Definición de rutas del servidor
  server.on("/", handleRoot);
  server.on("/arrancar", []() {
    server.send(200, "text/plain", "Arrancando...");
    ejecutarRutina();
  });
  server.on("/ruta", handleRuta);

  // Ruta para activar sonidos en el buzzer
  server.on("/beep", []() {
    server.send(200, "text/plain", "PITANDO");

    tone(PIN_BUZZER, 2000, 150);
    delay(200);
    tone(PIN_BUZZER, 2500, 200);
    delay(250);
    noTone(PIN_BUZZER); 
  });

  server.begin();
  Serial.println("=== SISTEMA LISTO ===");
}

void loop() {
  server.handleClient(); 
}