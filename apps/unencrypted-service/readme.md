### V. Unsecure BLE service
-  Unencrypted-service project implements a ble service with read, write and notification characteristic
-  Follow below steps to build and flash the app on DA14683-U
  ```sh
  - Select unencrypted-service project
  - from build options select DA14683-00-Realse-QSPI
  - after build is finished from external tools, select program_qspi_serial_win
  - script will run and in the terminal you have to give the port number for connected DA14683-U
  - press reset when prompted
  - press reset when app is flashed successfully --prod
 ```


#### Output
Realterm logs of peripheral responding  
<img src="/images/unsecure%20ble%20service/1.png"  height="500">  
Screen record of nRF Connect communicating  
<img src="/images/unsecure%20ble%20service/v1.gif"  height="600"> 