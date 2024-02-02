# BLE DA14683-U
## Guide to Development of BLE services on Dialog DA14683-U

### I. Inspiration
I had briefly worked with development of BLE services on Dialog DA14683-U for a project that required developing secured services on Dialog boards. During this time, I found it very difficult to get started with anything on this board cuz lack of guide and small community with mainly organizations using Dialog boards to build IOT devices. Just for simple blink code it took me two days to get it setup on DA14683-U. 

It’s been while since I worked on this project but just want to put some simple stuff out for anyone to get started with DA14683-U (before I forget most of it xd). This repo was built in very short amount of time (3 days in total), so the stuff here can be more optimized, but this is still descent given the amount of time.

This repo will have few example codes with guide on how to use them with proper setup with DA14683-U. I currently don’t have enough time to give a guide on how to program the services, but will plan a future update if enough people require it, since its mostly fundamental BLE service development in C.

Renesas provides a sdk for BLE service development for their boards, they are basically wrappers around native BLE functions in C that aim to simply low-level handling of protocols and tasks.

>Note: This guide doesn't contain guide on how to develop the service as of now, but i may plan to build a programming guide on that as well in future.

## Getting Started With DA14683-U

### II. Important Reads
Before we start with the setup, I want to emphasize on self-reading about the Dialog Board DA14683-U and BLE related topics. Go through below links before proceeding with the blog:

-[Product page for DA-14683-U](https://www.renesas.com/us/en/products/wireless-connectivity/bluetooth-low-energy/da14683-00a9devkt-u-smartbond-da14683-bluetooth-low-energy-basic-development-kit)  
-[Product page for DA-14683-pro](https://www.renesas.com/us/en/products/wireless-connectivity/bluetooth-low-energy/da14683-00a9devkt-p-smartbond-da14683-bluetooth-low-energy-50-development-kit-pro)  
-[Development tools for Dialog boards](https://www.renesas.com/us/en/software-tool/smartbond-development-tools)  
-[Official video for creating custom ble service on DA-14683-pro](https://www.youtube.com/watch?v=DGRdqP9Se8E)  
-[Other important docs that i referred](https://github.com/A-Suhail/BLE_DA14683-U/tree/main/doc%20resources)  

These are the fraction of docs that I went through while working on this project, it’s can be very challenging to get the right stuff at right time. For example, on the DA14683-U box itself there’s a QR code to be scanned which directs you to their product page, guess what the box (atleast in my case) lead me to DA14683-Pro page and being completely new to the board it took me several hours just to find the right resource page. Attaching few resources, including pro’s resource page since it also contains some insights.

### III. Setup
Follow these steps to get the repo and its environment locally setup on your machine.
This repo is only developed and tested on Windows environment and will continue with the guide for windows platform only.
> Note: SDK 1.1.14.1081 was used for this project since this is the “latest” and since no further plans are there to update this sdk, any application build using this is going to be reliable going forward, as it stated by dialog team itself [here](https://community.renesas.com/wireles-connectivity/f/bluetooth-low-energy/20145/da14683-roadmap-sdk-update-and-part-eol/100439#100439).

##### 1. Installing SmartSnippets Studio
- Install the IDE and its required dependencies as described in this [guide](https://s3.eu-west-2.amazonaws.com/lpccs-docs.dialog-semiconductor.com/um-b-056-da1468x_getting_started/05_Software_Development_Tools/Software_Development_Tools.html), follow steps in Section 11.2.1 only.
##### 2. Installing RealTerm - Serial/TCP Terminal
- Install Realterm for serial communication of DA14683-U to pc using usb, from [here](https://sourceforge.net/projects/realterm/).
##### 3. Download Repo on local machine
- Clone the [Repo](https://github.com/A-Suhail/BLE_DA14683-U.git) and place it your workspace folder. 
##### 4.  Setup workspace in SmartSnippets IDE
-   Open SmartSnippets Studio and locate the sdk folder inside the cloned repo (BLE_DA14683-U) in your workspace.  
      <img src="/images/3.4.1.png"  height="500">
-   SmartSnippets Studio will open Welcome page where you need to  select the connected device as DA14683-00  
      <img src="/images/3.4.2.png"  height="500">
-   Now select Open IDE
-   Import the scripts. These scripts were developed by Renesas to facilitate easy flashing of your Dialog board.
    -     Import Existing Project  
      <img src="/images/3.4.4.png"  height="500">
    -     navigate to [workspace]/BLE_DA14683-U/sdk/utilities/scripts -> finish  
      <img src="/images/3.4.5.png"  height="500">
    
-   Import the apps folder and select all projects inside it
    -     Import Existing Project
    -     navigate to [workspace]/BLE_DA14683-U/apps -> Select all -> finish  
      <img src="/images/3.4.7.png"  height="500">

-   The Project Structure should look like this after all imports  
      <img src="/images/3.4.8.png"  height="500">
     > Note: Ignore the missing path warnings, build is required to set project variables

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
>Note: Pics of working setup shown in individual readme files present in respective app directory
### VI. Secure BLE service - Security Request pair
-  Developers could mistake a security request with pairing process, both are fundamentally different from one another, confusion can lead bad and insecure ble service highly vulnerable to design mistakes in app development... i have seen it.
-  A pairing request can only be initiated from master to peripheral in a ble connection
-  While we have a mechanism called service request, in which peripheral can request master device to initiate this pairing - this is basically security request - initiated by peripheral to master.
-  The working mechanism of peripheral sending a security request is shown below
        <img src="/images/6.1.png"  height="400">
-  Now you may wonder why I chose strong words like vulnerable design mistakes. To implement a service with SR is different from implementing it robustly
-  When talking in the context of DA1468x, the app should follow below process
        <img src="/images/6.2.jpg"  height="500">
-  One important thing which developers miss is Block/Wait Process, which leads to the service data being open to anybody even if pairing is failed or rejected.
-  For those who thought why not just directly check for BLE Pair Success? Good question and this is the point which devs miss... you also have to send ble pair reply first accepting security request, and before replying you need to wait for peripheral to process the SR - thaty why we wait - and then reply and then check for ble pair success. if we were to directly check for ble pair success we would nullify the whole process of SR basically as if SR weren't implemented in the first place.
-  Now we can move on to flash the app in DA14683-U using same procedures as decribed below:
  ```sh
  - Select security-request-pair-service project
  - from build options select DA14683-00-Realse-QSPI
  - after build is finished from external tools, select program_qspi_serial_win
  - script will run and in the terminal you have to give the port number for connected DA14683-U
  - press reset when prompted
  - press reset when app is flashed successfully --prod
 ```
>Note: Pics of working setup shown in individual readme files present in respective app directory
### VII. Secure BLE service - Encrypted Characteristics/Service
-  As explained above master can only iniate the pairing process, but we can build a service inherently secure in peripheral when declaring it as "encrypted".
-  This declaration by peripheral device prompts the master device to suto moto initiate the pairing process.
-  This process is robust and if pairing process gets interrupted and fails, the service remains inaccesible to unkown devices inherently, unlike service request where peripheral has the responsibility to check for pair success.
-  > Note: Making an encrypted notify characteristics is not as straight-forward and requires its client_char_configurationto be set with write encryption flag only.
-  To flash this service proceed with the same procedures as described below:
  ```sh
  - Select custom-encrypted-service project
  - from build options select DA14683-00-Realse-QSPI
  - after build is finished from external tools, select program_qspi_serial_win
  - script will run and in the terminal you have to give the port number for connected DA14683-U
  - press reset when prompted
  - press reset when app is flashed successfully --prod
 ```
>Note: Pics of working setup shown in individual readme files present in respective app directory
### VIII. Flashing DA14683-U using binary files
-  > Note: In this section i have no idea what i did - if it was correct way to do it or not - any risks involved or not - i didn't find anything on official channels or unofficial on how to flash DA14683-U. I had intuitively came up with this method within couple hour. Use this method on your own discretion.
-   Directly bin flashing can be optimal soln when your non-technical member wants to run apps and doens't want the whole ide setup - its cumbersome.
-   Build an app for ex: blink-led in SmartSnippets IDE on dev machine
-   Navigate to /blink-led/DA14683-00-Release_QSPI/ and find blink-led.bin file. This file can be conveniently transferred to any team member and follow below steps.
-   To flash this binary, download and install [SmartSnippets Toolbox](https://www.renesas.com/us/en/software-tool/smartbond-development-tools).
-   Open SmartSnippets Toolbox -> Select Detect Device (make sure board is connected to your machine) -> select OK after detection completes successfully
        <img src="/images/8.1.png"  height="500">
        <img src="/images/8.2.png"  height="500">
-   Select Programmer -> Flash Code -> Connect
        <img src="/images/8.3.png"  height="500">
-   make sure no errors are present upto this point in the terminal
-   import the bin file -> Burn
        <img src="/images/8.4.png"  height="500">
-   Press Reset button on DA14683-U and it should run the flashed code immediately  
> Note: After directly flashing bin file using toolbox, when using program_sqpi_serial_win script though ide may experience some issues such as even after a successfull flash previous flashed app still running in Dialog DA14683-U. For this use the erase_qspi_serial_win script through ide and retry flashing.
> <img src="/images/troubleshoot1.png"  height="500">

### IX. Troubleshoot:
-  If path errors arrises perform clean build, if error persists check the Linked resources paths as well preprocessor build paths.
-  When running script "program_qspi_serial_win", if ide complains about empty path or loc/file not found, make sure your build project is selected - just left click on it.
-  Sometimes on smartphone, connection issue arises or no services showing etc, restart your phone and in bluetooth settings remove pairing information for Dialog board , sometimes internal ble stack of phone also gets stuck.

### X. Known Issues:
-  Sometimes when trying to connect to Dialog board, Phone shows connecting but fails to do so – happens rarely and only once not consecutively
-  App like LightBlue encounters some notification reading issue but nRFConnect works fine, I recommend nRF Connect app to testing purpose, only con is service names aren't visible by default in nRF connect but can use descriptor characteristics to read the same.
-  Security request service gets hang when you try to read again from it

### XI. Concluding Words
-  This is a solid sdk build by renesas devs but the community is lacking as well as official guide to development using sdk - mind you they do have docs for this and you should go through them - but its not enough and lacking in itself.
-  I had to build my knowledge of their sdk from ground up and found it intuitive if done correctly. Yes the code were initially build upon the examples they have provided, but lacked in building a custom secured robust ble service. I developed these apps with my own understanding and were duly tested. 
-  I wish to share my understanding of their sdk by making a blog or video but as of now my time is limited.
-  This guide doesn't contain guide on how to develop the service as of now, but i may plan to build a programming guide on that as well in future.
-  I am happy to help in any open-source project building upon Dialog boards.

