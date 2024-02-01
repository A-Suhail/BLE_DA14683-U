# BLE DA15683-U
## Guide to Development of BLE services on Dialog DA15683-U

### I. Inspiration
I had briefly worked with development of BLE services on Dialog DA15683-U for a project that required developing secured services on Dialog boards. During this time, I found it very difficult to get started with anything on this board cuz lack of guide and small community with mainly organizations using Dialog boards to build IOT devices. Just for simple blink code it took me two days to get it setup on DA15683-U. 

It’s been while since I worked on this project but just want to put some simple stuff out for anyone to get started with DA15683-U (before I forget most of it xd). This repo was built in very short amount of time (3 days in total), so the stuff here can be more optimized, but this is still descent given the amount of time.

This repo will have few example codes with guide on how to use them with proper setup with DA15683-U. I currently don’t have enough time to give a guide on how to program the services, but will plan a future update if enough people require it, since its mostly fundamental BLE service development in C.

Renesas provides a sdk for BLE service development for their boards, they are basically wrappers around native BLE functions in C that aim to simply low-level handling of protocols and tasks.

## Getting Started With DA15683-U

### II. Important Reads
Before we start with the setup, I want to emphasize on self-reading about the Dialog Board DA15683-U and BLE related topics. Go through below links before proceeding with the blog:

-[Product page for DA-15683-U](https://www.renesas.com/us/en/products/wireless-connectivity/bluetooth-low-energy/da14683-00a9devkt-u-smartbond-da14683-bluetooth-low-energy-basic-development-kit)
-[Product page for DA-15683-pro](https://www.renesas.com/us/en/products/wireless-connectivity/bluetooth-low-energy/da14683-00a9devkt-p-smartbond-da14683-bluetooth-low-energy-50-development-kit-pro)
-[Development tools for Dialog boards](https://www.renesas.com/us/en/software-tool/smartbond-development-tools)
-[Official video for creating custom ble service on DA-15683-pro](https://www.youtube.com/watch?v=DGRdqP9Se8E)
-[Other important docs that i referred](https://github.com/A-Suhail/BLE_DA14683-U/tree/main/doc%20resources)

These are the fraction of docs that I went through while working on this project, it’s can be very challenging to get the right stuff at right time. For example, on the DA15683-U box itself there’s a QR code to be scanned which directs you to their product page, guess what the box (atleast in my case) lead me to DA15683-Pro page and being completely new to the board it took me several hours just to find the right resource page. Attaching few resources, including pro’s resource page since it also contains some insights.

### III. Setup
Follow these steps to get the repo and its environment locally setup on your machine.
This repo is only developed and tested on Windows environment and will continue with the guide for windows platform only.
> Note: SDK 1.1.14.1081 was used for this project since this is the “latest” and since no further plans are there to update this sdk, any application build using this is going to be reliable going forward, as it stated by dialog team itself [here](https://community.renesas.com/wireles-connectivity/f/bluetooth-low-energy/20145/da14683-roadmap-sdk-update-and-part-eol/100439#100439).

##### 1. Installing SmartSnippets Studio
- Install the IDE and its required dependencies as described in this [guide](https://s3.eu-west-2.amazonaws.com/lpccs-docs.dialog-semiconductor.com/um-b-056-da1468x_getting_started/05_Software_Development_Tools/Software_Development_Tools.html), follow steps in Section 11.2.1 only.
##### 2. Installing RealTerm - Serial/TCP Terminal
- Install Realterm for serial communication of DA15683-U to pc using usb, from [here](https://sourceforge.net/projects/realterm/).
##### 3. Download Repo on local machine
- Clone the [Repo](https://github.com/A-Suhail/BLE_DA14683-U.git) and place it your workspace folder. 
##### 4.  Setup workspace in SmartSnippets IDE
-   Open SmartSnippets Studio and locate the sdk folder inside the cloned repo (BLE_DA14683-U) in your workspace.
-   SmartSnippets Studio will open Welcome page where you need to  select the connected device as DA15683-00
-   Now select Open IDE
-   Import the scripts. These scripts were developed by Renesas to facilitate easy flashing of your Dialog board.
    -     Import Existing Project 
    -     navigate to [workspace]/BLE_DA14683-U/sdk/utilities/scripts -> finish
    
-   Import the apps folder and select all projects inside it
    -     Import Existing Project 
    -     navigate to [workspace]/BLE_DA14683-U/apps -> finish
     > Note: Ignore the missing path warnings, build is required to set project variables

### IV. Blink
-   Blink-led project is a simple app that consecutively switch on/off  LED-1.2 (LED @ port1 and pin2)and LED-4.1 (LED @ port4 and pin1).
-   Select blink-led project
-   from build options select DA15683-00-Realse-QSPI
-   after build is finished from external tools, select program_qspi_serial_win
-   script will run and in the terminal you have to give the port number for connected DA15683-U
-   to check port number: windows+X -> Device manager-> ports
-   press reset when prompted
-   press reset when app is flashed successfully
### V. Unsecure BLE service
### VI. Secure BLE service - Security Request pair
### VII. Secure BLE service - Encrypted Characteristics/Service
### VIII. Flashing DA15683-U using binary files

