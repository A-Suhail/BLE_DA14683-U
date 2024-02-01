### VI. Secure BLE service - Security Request pair
-  Developers could mistake a security request with pairing process, both are fundamentally different from one another, confusion can lead bad and insecure ble service highly vulnerable to design mistakes in app development... i have seen it.
-  A pairing request can only be initiated from master to peripheral in a ble connection
-  While we have a mechanism called service request, in which peripheral can request master device to initiate this pairing - this is basically security request - initiated by peripheral to master.
-  The working mechanism of peripheral sending a security request is shown below
        <img src="images/6.1.png"  height="400">
-  Now you may wonder why I chose strong words like vulnerable design mistakes. To implement a service with SR is different from implementing it robustly
-  When talking in the context of DA1468x, the app should follow below process
        <img src="images/6.2.jpg"  height="500">
-  One important thing which developers miss is Block/Wait Process, which leads to the service data being open to anybody even if pairing is failed or rejected.
-  For those who thought why not just directly check for BLE Pair Success? Good question and this is the point which devs miss... you also have to send ble pair reply first accepting security request, and before replying you need to wait for peripheral to process the SR - thaty why we wait - and then reply and then check for ble pair success. if we were to directly check for ble pair success we would nullify the whole process of SR basically as if SR weren't implemented in the first place.
-  Now we can move on to flash the app in DA14683-U using same procedures as decribed previous section.