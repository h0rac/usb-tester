# usb-tester
Script for black box testing to discover USB messages on the BUS supported by target device

#### It works and it was tested on raspberry pi 4 and Linux. As long you can use prereq.sh script on your distro it should be fine. Please not that probably for Intel CPUs you need to either install build utils for ARM or change gcc.

#### Main goal of the script is to find USB messages supported by target device, either for fuzzing or for fault injection attacks. Using additionally devices like USB hardware triggers (Beagle 480, PhyWhisperer) together with X-Force RED Raiden And/or EMFI you can very deeply test USB stacks on target devices.  

### Examples


### 1. Default bruteforce wValue, wIndex, bmRequest, bRequest  
```
pi@raspberrypi:~/tools/usb-tester $ lsusb
Bus 001 Device 030: ID 0483:a2ca STMicroelectronics 

python3 usb_test.py -v 0x483 -p 0xa2ca
```
### 2. Bruteforce only wIndex
```
python3 usb_test.py -v 0x483 -p 0xa2ca -b Device-to-Host-Standard-Interface -bR GET_DESCRIPTOR -wV 0x2100
```
### 3. Bruteforce only wValue
```
python3 usb_test.py -v 0x483 -p 0xa2ca -b Device-to-Host-Standard-Interface -bR GET_DESCRIPTOR -wI 0x0
```
### 4. Bruteforce wValue and wIndex
```
python3 usb_test.py -v 0x483 -p 0xa2ca -b Device-to-Host-Standard-Interface
```
### 5. Bruteforce wValue and wIndex and bmRequest
```
python3 usb_test.py -v 0x483 -p 0xa2ca -bR GET_DESCRIPTOR
```
### 6. Other possibilities
```
python3 usb_test.py -h
```
