import usb.core
import usb.util
import time
import argparse
import sys
import signal

bRequestSelected = None

bmRequestTypes = {
    "Device-to-Host-Standard-Device": 1 << 7,
    "Device-to-Host-Class-Device": (1 << 7 | 1 << 5),
    "Device-to-Host-Vendor-Device": (1 << 7 | 1 << 6),

    "Device-to-Host-Standard-Interface": 1 << 7 | 1 << 0,
    "Device-to-Host-Class-Interface": (1 << 7 | 1 << 5 | 1 << 0),
    "Device-to-Host-Vendor-Interface": (1 << 7 | 1 << 6 | 1 << 0),
    
    "Device-to-Host-Standard-Endpoint": 1 << 7 | 1 << 1,
    "Device-to-Host-Class-Endpoint": (1 << 7 | 1 << 5 | 1 << 1),
    "Device-to-Host-Vendor-Endpoint": (1 << 7 | 1 << 6 | 1 << 1),

    "Device-to-Host-Standard-Other": 1 << 7 | (1 << 1 | 1 << 0),
    "Device-to-Host-Class-Other": 1 << 7 | 1 << 5 | (1 << 1 | 1 << 0),
    "Device-to-Host-Vendor-Other": 1 << 7 | 1 << 6 | (1 << 1 | 1 << 0),
    
    "Host-to-Device-Standard-Device": 0,
    "Host-to-Device-Class-Device": 1 << 5,
    "Host-to-Device-Vendor-Device": 1 << 6,

    "Host-to-Device-Standard-Interface": 0 | 1 << 0,
    "Host-to-Device-Class-Interface": 1 << 5 | 1 << 0,
    "Host-to-Device-Vendor-Interface": 1 << 6 | 1 << 0,

    "Host-to-Device-Standard-Endpoint": 0 | 1 << 1,
    "Host-to-Device-Class-Endpoint": 1 << 5 | 1 << 1,
    "Host-to-Device-Vendor-Endpoint": 1 << 6 | 1 << 1,

    "Host-to-Device-Standard-Other": 0 | (1 << 1 | 1 << 0),
    "Host-to-Device-Class-Other": 1 << 5 | (1 << 1 | 1 << 0),
    "Host-to-Device-Vendor-Other": 1 << 6 | (1 << 1 | 1 <<0 )
}

bRequests = {
    "GET_STATUS": 0,
    "CLEAR_FEATURE": 1,
    "RESERVED_2": 2,
    "SET_FEATURE": 3,
    "RESERVED_4": 4,
    "SET_ADDRESS": 5,
    "GET_DESCRIPTOR": 6,
    "SET_DESCRIPTOR":7,
    "GET_CONFIGURATION": 8,
    "SET_CONFIGURATION": 9,
    "GET_INTERFACE": 10,
    "SET_INTERFACE":11,
    "SYNC_FRAME":12
}

bRequestsBruteKeys = ["UNDEF{}".format(x) for x in range (13,256)]
bRrequestBruteValues = [x for x in range(13,256)]
bRequestBrute = dict(zip(bRequestsBruteKeys, bRrequestBruteValues))

bRequestBrute = dict(list(bRequests.items()) + list(bRequestBrute.items()))

#resp = dev.ctrl_transfer(bmRequestType=0x81, bRequest=0x8, wValue=0x2000, wIndex=0x0000, data_or_wLength=[00 for x in range(0,4096)])
parser = argparse.ArgumentParser()
parser.add_argument('-v', '--idVendor',
                    required=False,
                    type=str,
                    dest="idVendor",
                    default=hex(1155),
                    metavar="<idVendor>",
                    help="Vendor id of USB target device")
parser.add_argument('-p', '--idProduct',
                    required=False,
                    type=str,
                    default=hex(41674),
                    dest="idProduct",
                    metavar="<idProduct>",
                    help="Product id of USB target device")                    
parser.add_argument('-bM', '--bmRequestType',
                    required=False,
                    type=str,
                    nargs='*',
                    dest="bmRequestType",
                    metavar="<bmRequestType>",
                    action="store",
                    help='Manual bmRequestType for USB request, if not provided will be bruteforce')
parser.add_argument('-bR', '--bRequest',
                    required=False,
                    type=str,
                    nargs='*',
                    dest="bRequest",
                    action="store",
                    metavar="<bRequest>",
                    help='Manual bRequest for USB request, if not provided will be bruteforce')
parser.add_argument('-wV', '--wValue',
                    required=False,
                    type=str,
                    dest="wValue",
                    metavar="<wValue>",
                    help="Manual wValue for USB request, if not provided will be bruteforce")
parser.add_argument('-wI', '--wIndex',
                    required=False,
                    type=str,
                    dest="wIndex",
                    metavar="<wIndex>",
                    help="Manual wIndex for USB request, if not provided will be bruteforce")
parser.add_argument('-wL', '--wLength',
                    required=False,
                    type=str,
                    default=hex(65000), 
                    dest="wLength",
                    metavar="<wLength>",
                    help="Manual wLength for USB request, if not provided will be default")


args = parser.parse_args()
print({x:hex(y) for (x,y) in bmRequestTypes.items()})
if (args.bmRequestType):
    args.bmRequest=int(args.bmRequestType,16)
if (args.bRequest):
    args.bRequest=int(args.bRequest,16)
if(args.idVendor):
    args.idVendor=int(args.idVendor,16)
if(args.idProduct):
    args.idProduct=int(args.idProduct,16)
if(args.wValue):
    args.wValue = int(args.wValue,16)
if(args.wIndex):
    args.wIndex = int(args.wIndex,16)
if(args.wLength):
    args.wLength = int(args.wLength,16)

try:
    dev = usb.core.find(idVendor=args.idVendor, idProduct=args.idProduct)
    for cfg in dev:
        for intf in cfg:
            if dev.is_kernel_driver_active(intf.bInterfaceNumber):
                try:
                    dev.detach_kernel_driver(intf.bInterfaceNumber)
                except usb.core.USBError as e:
                    sys.exit("Could not detatch kernel driver from interface({0}): {1}".format(intf.bInterfaceNumber, str(e)))
    dev.set_configuration() 
    # print(dev)
except TypeError as e:
    print("Probably USB Device is not connected {}".format(e))
    sys.exit(0)

responses = []


bRequestSelected = {k:v for k,v in bRequestBrute.items() if k in  args.bRequest}
bmRequestTypesSelected = {k:v for k,v in bmRequestTypes.items() if k in args.bmRequestType}

# for k,v in bmRequestTypes.items():
#     print("{}, {}".format(k, hex(v)))

try:
    for kRequestType,vRequestType in bmRequestTypesSelected.items():
        for kRequest, vRequest in bRequestSelected.items():
            if(args.wValue is not None and args.wValue >= 0 and args.wIndex is not None and args.wIndex >= 0):
                try:
                    print("[+] bmRequestType={}, description={}, bRequest={}, description={}, wValue={}, wIndex={}, wLength={}".format(hex(vRequestType), kRequestType, hex(vRequest), kRequest, hex(args.wValue), hex(args.wIndex), hex(args.wLength)))
                    ret = dev.ctrl_transfer(bmRequestType=args.bmRequestType, bRequest=args.bRequest, wValue=args.wValue, wIndex=args.wIndex, data_or_wLength=args.wLength)
                    if(len(ret) > 0):
                        responses.append({"bmRequestType":hex(args.bmRequestType), "bRequest":hex(args.bRequest), "wValue":hex(args.wValue), "wIndex":hex(args.wIndex), "wLength":hex(args.wLength), "resp":list(ret) })
                        print(ret)
                except:
                    pass
            elif(args.wValue is not None and args.wValue >= 0 and args.wIndex is None):
                for wIndex in range(256):
                    try:
                        print("[+] bmRequestType={}, description={}, bRequest={}, description={}, wValue={}, wIndex={}, wLength={}".format(hex(vRequestType), kRequestType, hex(vRequest), kRequest, hex(args.wValue), hex(wIndex), hex(args.wLength)))
                        ret = dev.ctrl_transfer(bmRequestType=args.bmRequestType, bRequest=args.bRequest, wValue=args.wValue, wIndex=wIndex, data_or_wLength=args.wLength)
                        if(len(ret) > 0):
                            responses.append({"bmRequestType":hex(args.bmRequestType), "bRequest":hex(args.bRequest), "wValue":hex(args.wValue), "wIndex":hex(wIndex), "wLength":hex(args.wLength), "resp":list(ret) })
                            print(ret)
                    except:
                        pass
            elif(args.wIndex is not None and args.wIndex >=0 and args.wValue is None):
                for wValue in range(65535):
                    try:
                        print("[+] bmRequestType={}, description={}, bRequest={}, description={}, wValue={}, wIndex={}, wLength={}".format(hex(vRequestType), kRequestType, hex(vRequest), kRequest, hex(wValue), hex(args.wIndex), hex(args.wLength)))
                        ret = dev.ctrl_transfer(bmRequestType=args.bmRequestType, bRequest=args.bRequest, wValue=wValue, wIndex=args.wIndex, data_or_wLength=args.wLength)
                        if(len(ret) > 0):
                            responses.append({"bmRequestType":hex(args.bmRequestType), "bRequest":hex(args.bRequest), "wValue":hex(wValue), "wIndex":hex(args.wIndex), "wLength":hex(args.wLength), "resp":list(ret) })
                            print(ret)
                    except:
                        pass
            else:
                for wValue in range(65535):
                    for wIndex in range(256):
                        try:
                            print("[+] bmRequestType={}, description={}, bRequest={}, description={}, wValue={}, wIndex={}, wLength={}".format(hex(vRequestType), kRequestType, hex(vRequest), kRequest, hex(wValue), hex(wIndex), hex(args.wLength)))
                            ret = dev.ctrl_transfer(bmRequestType=args.bmRequestType, bRequest=args.bRequest, wValue=wValue, wIndex=wIndex, data_or_wLength=args.wLength)
                            if(len(ret) > 0):
                                responses.append({"bmRequestType":hex(args.bmRequestType), "bRequest":hex(args.bRequest), "wValue":hex(wValue), "wIndex":hex(wIndex), "wLength":hex(args.wLength), "resp":list(ret) })
                                print(ret)
                        except:
                            pass
    if(len(responses) > 0):
        print("[+] Results found !!! save to responses files")
        for i in range(0, len(responses)):
            f = open("responses%d.txt" % i, "w")
            f.write("{}\n".format(responses[i]))
            f.close()
            f = open("responses%d.bin" % i, "w")
            f.write("".join([chr(elem) for elem in responses[i]["resp"]]))
            f.close()
    else:
        print("[-] Results not found :(")
except KeyboardInterrupt:
    print("Exit program")
    sys.exit(0)

