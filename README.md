# OpenWave-3KA

![GetImage](/image/OpenWave256x256.jpg)

This icon is copyright by Good Will Instrument Co., Ltd all rights reserved.



OpenWave-3KA is an open-source project. It's a simple python program that can get image or raw data from digital storage oscilloscope(GDS-3000A/GDS-73000A/MSO-3000/GDS-2000E/DCS-2000E/IDS-2000E/MSO-2000E/MDO-2000E/MDO-2000A/RSMSO-2000E/RSMDO-2000E/MPO-2000 series) via USB, ethernet or GPIB(GDS-3000A only) port.  

Users can execute the same source code on Windows and Linux(Ubuntu) operating system. Users can also create multiple DSO connections at the same time.


## Equipment
You have to get a new digital storage oscilloscope (as listed above) and a PC or NB with MS Windows or Linux OS .




## Environment

#### _Windows:_

Interface: USB, Ethernet and GPIB(GDS-3000A only).

OS version: Windows 7/8/10 32 or 64 bits. 

Please unzip [OpenWave-3KA V1.02.zip](/exe/OpenWave-3KA_V1.02.zip) into a folder and find OpenWave-3KA.exe in the folder. OpenWave-3KA.exe can be executed directly without installation.

OpenWave-3KA relies on NI-VISA as instrument driver. You have to download NI-VISA from NI website and install it on your Windows before executing this program. If you want to connect a GDS-2000E series DSO, you have to download and install USB driver(dso_vpo V1.08) from [www.gwinstek.com](http://www.gwinstek.com) or [here](/dso_vpo_v108.zip) when the first connection with GDS-2000E.

GDS-3000A and MPO-2000 use USBTMC as communication protocol, ther is no driver installation required.


#### _Linux:_

Interface: USB and Ethernet. Currently, GPIB seems not supported by PyVISA-py yet.

OpenWave-3KA source code can also be executed on Ubuntu Linux. We have tested it on Ubuntu 20.04 LTS(on VirtualBox) and Ubuntu 18.04 LTS(Intel Celeron 2980U @1.6GHz with 2GB DDR3)

OpenWave-3KA relies on PyVISA-Py as instrument driver. You have to install PyVISA-Py before executing this program.





#### _Tips:_

1.  *If you want to connect your DSO via ethernet. Don't forget to set up your IP address properly or set DHCP on(Utility -> I/O -> Ethernet -> DHCP/BOOTP on).  And enable the socket server on your DSO.*

2.  *If you are using Linux, please add your username to group ```dialout``` to get proper privilege level for device accessing. (for GDS-2000E series only)*
    ```
    user@Ubuntu:~/OpenWave-3KA V1.01$ sudo adduser xxxx dialout     #xxxx is your username
    ```



## Development Tools
#### _Packages:_
   If you want to modify the source code and run the program by yourself. You have to install the development tools and packages as follows:
   * Python 3.9.5
   * PyVISA 1.11.3
   * Matplotlib 3.3.3
   * Numpy 1.19.4
   * Pillow 8.0.1
   * PySide2 5.15.2
   * dateutil 2.8.1
   * pyparsing 2.4.7
   * six 1.15.0

 *OpenWave-3KA.exe is developed under Windows 7 32 bits environment, and all the packages are Windows 32bits version.*


#### _Ubuntu Linux:_
   OpenWave-3KA is also tested under Ubuntu 20.04/18.04 LTS (64 bits) with similar version of packages listed above.  And the following packages and libraries are required:
   * libxcb-xinerama0
   * PySerial 3.5
   * PyUSB 1.2.1
   * PyVISA-py 0.5.2

#### _Windows Executable File:_
   If you want to convert python program into stand-alone executables on Windows. The following packages are required:
   * PyInstaller 4.1
   * pywin32 218.4



   
## Program Execution

#### _Windows:_
You can double click on the OpenWave-3KA.exe icon to execute the program. 

You can also use a windows command line console to execute the program.
```
D:\OpenWave-3KA V1.00>OpenWave-3KA.exe
```

You have to select the connected interface from _VISA Resource_ page or _Config File_ page on the _Select Interface_ window. NI-VISA backend will automatically discover the connected USB device and the network device(with mDNS capability). In order to enable the mDNS capability, you have to enable Web Server function on your DSO first.  The GDS-2000E series does not support mDNS functionality, you have to use a config file.

You can also create a `port.config` file containing `172.16.5.94:3000`(as an example and for ethernet only) in the same folder for next time quick connection.



![](/image/Win7_Screenshot1.png)


_Ethernet connection on Win 7:_
![](/image/Win7_Screenshot2.png)


_Ethernet connection on Win 7:_
![](/image/Win7_Screenshot3.png)



#### _Ubuntu Linux:_
You can open a terminal console to execute the program.
```
user@Ubuntu:~/OpenWave-3KA V1.00$ sudo python3 OpenWave-3KA.py
```

You have to select the connected interface from _VISA Resource_ page or _Config File_ page on the _Select Interface_ window. Here PyVISA-py backend will automatically discover the connected USB device, but the network device will not be discovered by PyVISA-py. You have to create a port.config file that contains the IP address and port number matching with your DSO.



_Ubuntu Linux -- Select Interface from VISA Resource or Config File_

![](/image/Ubuntu18.04_1.png)           ![](/image/Ubuntu18.04_2.png)




_Ubuntu 20.04 LTS -- Get raw data via ethernet_
![](/image/Ubuntu20.04_1.png)


_Ubuntu 18.04 LTS -- Get screen image via USB_
![](/image/Ubuntu18.04_3.png)


_Ubuntu 20.04 LTS -- Get screen image via ethernet_
![](/image/Ubuntu20.04_2.png)


_Ubuntu 18.04 LTS -- Get screen image/raw data via USB/ethernet_
![](/image/Ubuntu18.04_4.png)


