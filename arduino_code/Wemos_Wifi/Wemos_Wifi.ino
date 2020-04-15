#include "Arduino.h"
#include "Arduino.h"
#include <Wire.h>
#include <ESP8266WiFi.h>
#include <ArduinoJson.h>

const int sclPin = D3;
const int sdaPin = D4;
String temp="";
int val;
int command;

const char* ssid     = "AndroidAP";           // SSID of local network
const char* password = "matthewljk";        // Password on network
const char* ipv4_address = "192.168.43.101"; // IPv4 address obtained from cmd --> ipconfig
const char* host_name = "Host: 192.168.1.101"; // hostname for localhost

WiFiClient client;
const char* servername=ipv4_address;
String result;


void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);

  Wire.begin(sdaPin, sclPin);


  // CONNECTING TO WIFI NETWORK
  Serial.println("------------Beginning WiFi setup------------");
  Serial.println("Connecting to WiFi");
  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.println("Connecting to WiFi...");
    delay(500);
  }
  
  Serial.println("Connected to WiFi");
  delay(1000);
  Serial.println("------------Finish WiFi setup------------");

  WiFi.mode(WIFI_STA);
}


void loop() {
  // put your main code here, to run repeatedly:
  // for getting instructions for arduino
  Serial.println("Getting instructions");  
  getInstructions();  
  delay(1000);
}


// used by arduino to receive instructions from the server
void getInstructions()
{
  if (client.connect(servername, 443)) {  //starts client connection, checks for connection
    client.println("GET /getInstructions");
    client.println(host_name);
    client.println("User-Agent: Naviband");
    client.println("Connection: close");
    client.println();
  } 
  else {
    Serial.println("connection failed"); //error message if no client connect
    Serial.println();
  }

  while(client.connected() && !client.available()) delay(1); //waits for data
  while (client.connected() || client.available()) 
  { //connected or data available
    char c = client.read(); //gets byte from ethernet buffer
    result = result+c;
  } 

  client.stop(); //stop client
  result.replace('[', ' ');
  result.replace(']', ' ');
//  temp=temp+result[19];
//  temp=temp+result[20];
//  int val = temp.toInt();

  Serial.println(result);  
  char jsonArray [result.length()+1];
  result.toCharArray(jsonArray,sizeof(jsonArray));
  jsonArray[result.length() + 1] = '\0';
  StaticJsonDocument<1024> doc;
  DeserializationError error = deserializeJson(doc, jsonArray);
  if (error)
  {
    Serial.println("deserializeJson() failed with code");
    Serial.println(error.c_str());
  }
  
  String command = doc["command"];
  int val=command.toInt();
  Serial.println(val);
  
  Wire.beginTransmission(4);
  Serial.println();
  Serial.println("Began!");
  Wire.write("x is ");
  Wire.write(val);              // sends one byte  
  Wire.endTransmission();    // stop transmitting
  temp="";
  result="";  
}
