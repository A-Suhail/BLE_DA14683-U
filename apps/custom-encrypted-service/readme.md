### VII. Secure BLE service - Encrypted Characteristics/Service
-  As explained above master can only iniate the pairing process, but we can build a service inherently secure in peripheral when declaring it as "encrypted".
-  This declaration by peripheral device prompts the master device to suto moto initiate the pairing process.
-  This process is robust and if pairing process gets interrupted and fails, the service remains inaccesible to unkown devices inherently, unlike service request where peripheral has the responsibility to check for pair success.
-  > Note: Making an encrypted notify characteristics is not as straight-forward and requires its client_char_configurationto be set with write encryption flag only.
-  To flash this service proceed with the same procedures as described in earlier sections.