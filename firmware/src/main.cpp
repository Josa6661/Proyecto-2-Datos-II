#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>

// --- CONFIGURACIÓN WIFI ---
const char* ssid = "Fam CH";
const char* password = "fchf1013";
WebServer server(80);

// --- PINES (Iguales a los anteriores) ---
const int IN1 = 11; const int IN2 = 12;
const int IN3 = 13; const int IN4 = 14;
const int SENSOR_IZQ = 4; const int SENSOR_DER = 5;

volatile int pasosIzq = 0;
volatile int pasosDer = 0;

void IRAM_ATTR contarPasoIzq() { pasosIzq++; }
void IRAM_ATTR contarPasoDer() { pasosDer++; }

void detener() {
  digitalWrite(IN1, LOW); digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
  delay(500);
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
  int objetivoGiro = 12; // El valor que ajustaste antes
  pasosIzq = 0; pasosDer = 0;
  digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
  while (pasosIzq < objetivoGiro && pasosDer < objetivoGiro) { delay(5); }
  detener();
}

// Función que ejecuta el cuadrado
void ejecutarRutina() {
  for (int i = 0; i < 4; i++) {
    avanzar(50);
    girar90();
  }
}

// Página Web
void handleRoot() {
  String html = "<html><body><h1>Control ESP32-S3</h1>";
  html += "<button onclick=\"location.href='/arrancar'\" style='width:200px;height:100px;font-size:30px;'>ARRANCAR CUADRADO</button>";
  html += "</body></html>";
  server.send(200, "text/html", html);
}

void setup() {
  Serial.begin(115200);
  delay(2000); // Esperar a que el monitor serial esté listo
  Serial.println("\n\n=== ESP32-S3 INICIANDO ===");
  pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);
  pinMode(SENSOR_IZQ, INPUT); pinMode(SENSOR_DER, INPUT);
  Serial.println("✓ Pines configurados");
  attachInterrupt(digitalPinToInterrupt(SENSOR_IZQ), contarPasoIzq, RISING);
  attachInterrupt(digitalPinToInterrupt(SENSOR_DER), contarPasoDer, RISING);
  Serial.println("✓ Interrupciones adjuntas");

  // Conectar a WiFi con timeout
  Serial.print("Conectando a WiFi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  int intentos = 0;
  int maxIntentos = 20;  // 10 segundos máximo (20 * 500ms)

  while (WiFi.status() != WL_CONNECTED && intentos < maxIntentos) {
    delay(500);
    Serial.print(".");
    intentos++;
  }

  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("✓ Conectado a WiFi!");
    Serial.print("IP del carro: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("✗ NO se conectó a WiFi (continuando de todas formas)");
  }

  // Configurar rutas del servidor
  server.on("/", handleRoot);
  server.on("/arrancar", []() {
    server.send(200, "text/plain", "Arrancando cuadrado...");
    ejecutarRutina();
  });

  server.begin();
  Serial.println("✓ Servidor web iniciado en puerto 80");
  Serial.println("=== LISTO ===\n");
}

void loop() {
  server.handleClient(); // Mantener el servidor escuchando
}