### IV. Blink
-   Blink-led project is a simple app that consecutively switch on/off  LED-1.2 (LED @ port1 and pin2)and LED-4.1 (LED @ port4 and pin1).
-   Select blink-led project
-   from build options select DA14683-00-Realse-QSPI  
      <img src="/images/4.1.png"  height="500">
-   after build is finished from external tools, select program_qspi_serial_win  
      <img src="/images/4.2.png"  height="500">
-   script will run and in the terminal you have to give the port number for connected DA14683-U  
      <img src="/images/4.3.png"  height="200">
-   to check port number: windows+X -> Device manager-> ports  
     <img src="/images/4.4.png"  height="200">
-   press reset when prompted
-   press reset when app is flashed successfully  
      <img src="/images/4.5.png"  height="400">

#### Output
Alternate blinking of both leds (red and white)
<img src="/images/DA14683-red.jpeg"  height="400">
<img src="/images/DA14683-white%20.jpeg"  height="400">
      
