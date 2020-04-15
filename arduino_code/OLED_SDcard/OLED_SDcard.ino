// Adafruit_ImageReader test for Adafruit ST7735 TFT Breakout for Arduino.
// Demonstrates loading images from SD card or flash memory to the screen,
// to RAM, and how to query image file dimensions.
// Requires three BMP files in root directory of SD card:
// rgbwheel.bmp, miniwoof.bmp and wales.bmp.
// As written, this uses the microcontroller's SPI interface for the screen
// (not 'bitbang') and must be wired to specific pins (e.g. for Arduino Uno,
// MOSI = pin 11, MISO = 12, SCK = 13). Other pins are configurable below.

#include <Adafruit_GFX.h>         // Core graphics library
#include <Adafruit_SSD1351.h>      // Hardware-specific library
#include <SdFat.h>                // SD card & FAT filesystem library
#include <Adafruit_SPIFlash.h>    // SPI / QSPI flash library
#include <Adafruit_ImageReader.h> // Image-reading functions


#include <Wire.h>

char appData;  
String inData = "";

const int tonePin = 8;

// Comment out the next line to load from SPI/QSPI flash instead of SD card:
#define USE_SD_CARD

// Color definitions
#define BLACK           0x0000
#define BLUE            0x001F
#define RED             0xF800
#define GREEN           0x07E0
#define CYAN            0x07FF
#define MAGENTA         0xF81F
#define YELLOW          0xFFE0
#define WHITE           0xFFFF

// Screen dimensions
#define SCREEN_WIDTH  128
#define SCREEN_HEIGHT 128   // Change this to 96 for 1.27" OLED.

// TFT display and SD card share the hardware SPI interface, using
// 'select' pins for each to identify the active device on the bus.

#define SD_CS    7 // SD card select pin
#define TFT_CS   5 // TFT select pin
#define TFT_DC   4 // TFT display/command pin
#define TFT_RST  6 // Or set to -1 and connect to Arduino RESET pin

#if defined(USE_SD_CARD)
  SdFat                SD;         // SD card filesystem
  Adafruit_ImageReader reader(SD); // Image-reader object, pass in SD filesys
#else
  // SPI or QSPI flash filesystem (i.e. CIRCUITPY drive)
  #if defined(__SAMD51__) || defined(NRF52840_XXAA)
    Adafruit_FlashTransport_QSPI flashTransport(PIN_QSPI_SCK, PIN_QSPI_CS,
      PIN_QSPI_IO0, PIN_QSPI_IO1, PIN_QSPI_IO2, PIN_QSPI_IO3);
  #else
    #if (SPI_INTERFACES_COUNT == 1)
      Adafruit_FlashTransport_SPI flashTransport(SS, &SPI);
    #else
      Adafruit_FlashTransport_SPI flashTransport(SS1, &SPI1);
    #endif
  #endif
  Adafruit_SPIFlash    flash(&flashTransport);
  FatFileSystem        filesys;
  Adafruit_ImageReader reader(filesys); // Image-reader, pass in flash filesys
#endif

Adafruit_SSD1351 tft = Adafruit_SSD1351(SCREEN_WIDTH, SCREEN_HEIGHT, &SPI, TFT_CS, TFT_DC, TFT_RST);

Adafruit_Image       img;        // An image loaded into RAM
int32_t              width  = 0, // BMP image dimensions
                     height = 0;

int command;

void setup(void) {
  pinMode( 10 , OUTPUT);  // Must be a PWM pin
  pinMode(tonePin, OUTPUT);

  ImageReturnCode stat; // Status from image-reading functions
  //Serial wires
  Wire.begin(4);                // join i2c bus with address #4
  Wire.onReceive(receiveEvent); // register event      
  Serial.begin(115200);
#if !defined(ESP32)
  while(!Serial);       // Wait for Serial Monitor before continuing
#endif

  tft.begin(); // Initialize screen

  // The Adafruit_ImageReader constructor call (above, before setup())
  // accepts an uninitialized SdFat or FatFileSystem object. This MUST
  // BE INITIALIZED before using any of the image reader functions!
  Serial.print(F("Initializing filesystem..."));
#if defined(USE_SD_CARD)
  // SD card is pretty straightforward, a single call...
  if(!SD.begin(SD_CS, SD_SCK_MHZ(10))) { // Breakouts require 10 MHz limit due to longer wires
    Serial.println(F("SD begin() failed"));
    for(;;); // Fatal error, do not continue
  }
#else
  // SPI or QSPI flash requires two steps, one to access the bare flash
  // memory itself, then the second to access the filesystem within...
  if(!flash.begin()) {
    Serial.println(F("flash begin() failed"));
    for(;;);
  }
  if(!filesys.begin(&flash)) {
    Serial.println(F("filesys begin() failed"));
    for(;;);
  }
#endif
  Serial.println(F("OK!"));

  // Fill screen blue. Not a required step, this just shows that we're
  // successfully communicating with the screen.
  tft.fillScreen(BLUE);

  // Load full-screen BMP file 'rgbwheel.bmp' at position (0,0) (top left).
  // Notice the 'reader' object performs this, with 'tft' as an argument.
    Serial.print(F("Loading Navi-Band.bmp to screen..."));
  stat = reader.drawBMP("/Start.bmp", tft, 0, 0);
  Serial.print(width);
  Serial.println(height);  
  reader.printStatus(stat);   // How'd we do?
  delay(2000);
  Serial.println("Welcome");
  reader.drawBMP("/Welcome.bmp", tft,0,0);
  delay(2000);

  analogWrite( 10 , 0 );    // 0% duty cycle (off)

    
}

void loop() {
    Serial.println(Wire.available());  
    while(Wire.available()){
        command = Wire.read();
        Serial.println(command);
         
        if(command==11){
            Serial.println("left!!!!");
            reader.drawBMP("/Left.bmp", tft,0,0);
        }
        else if(command==12){
            Serial.println("up!!!!");
            reader.drawBMP("/Straight.bmp", tft,0,0);
        }
        else if(command==13){
            Serial.println("right!!!!");
            reader.drawBMP("/Right.bmp", tft,0,0);
        }
        else if(command==14){
            Serial.println("U turn!!!!");
            reader.drawBMP("/U-Turn.bmp", tft,0,0);
            analogWrite( 10 , 153 );  // 60% duty cycle
            tone(tonePin,1000);
            delay(3000);              // play for 0.5s
            analogWrite( 10 , 0 );    // 0% duty cycle (off)
            noTone(tonePin);
            
        }
        else if(command==15){
            Serial.println("Go down");
            reader.drawBMP("/Down.bmp", tft,0,0);
        }
        else if(command==16){
            Serial.println("Go up");
            reader.drawBMP("/Up.bmp", tft,0,0);
        }
        else if(command==17){
            Serial.println("Clinics");
            reader.drawBMP("/Clinics.bmp", tft,0,0);
        }
        else if(command==18){
            Serial.println("Register");
            reader.drawBMP("/Registration.bmp", tft,0,0);
        }
        else if(command==19){
            Serial.println("Doctor Teo");
            reader.drawBMP("/Teo.bmp", tft,0,0);
        }
        else if(command==20){
            Serial.println("Doctor So");
            reader.drawBMP("/So.bmp", tft,0,0);
        }
        else if(command==21){
            Serial.println("Pharmacy");
            reader.drawBMP("/Pharmacy.bmp", tft,0,0);
        }
        else if(command==22){
            Serial.println("10 min waiting time");
            reader.drawBMP("/10.bmp", tft,0,0);
        }
        else if(command==23){
            Serial.println("5 min waiting time");
            reader.drawBMP("/5.bmp", tft,0,0);
       
        }
        else if(command==24){
            Serial.println("Your turn");
            reader.drawBMP("/Queue.bmp", tft,0,0);
            analogWrite( 10 , 255 );  // 60% duty cycle
            tone(tonePin,1000);
            delay(3000);              // play for 0.5s
            analogWrite( 10 , 0 );    // 0% duty cycle (off)
            noTone(tonePin);
        }
        else if(command==25){
            Serial.println("Hurry up!");
            reader.drawBMP("/1.bmp", tft,0,0);
            analogWrite( 10 , 255 );  // 60% duty cycle
            delay(4000);              // play for 0.5s
            analogWrite( 10 , 0 );    // 0% duty cycle (off)

        }
        else{
            Serial.println("Invalid command");
        }
    }

   delay(800); // Pause 1 sec.
}

void receiveEvent (int howMany)
{
 command = Wire.read();                   
}
