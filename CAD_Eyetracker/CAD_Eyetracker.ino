unsigned long tiempoInicio;

void setup() {
  Serial.begin(9600);
  tiempoInicio = millis(); // Guardo el tiempo actual al iniciar
}

void loop() {
  // Verifico si ha pasado un minuto desde el inicio
  if (millis() - tiempoInicio <= 80000) { // 
    // Simula datos de tiempo, posición X y posición Y
    unsigned long tiempo = millis();
    int posX = analogRead(A0) - 550;
    int posY = analogRead(A1) - 550;  
    // Envía los datos formateados a través del puerto serial
    Serial.print(posX);
    Serial.print(",");
    Serial.println(posY);
    
    delay(10); // Quiero que registre datos cada 0,1 segundos
  } else {
    // Si ha pasado un minuto, se detiene el programa
    while (true) {
      // Detiene el programa
    }
  }
}
