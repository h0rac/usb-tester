wget https://github.com/libusb/libusb/releases/download/v1.0.23/libusb-1.0.23.tar.bz2
tar -xvf libusb-1.0.23.tar.bz2
cd libusb-1.0.23
sed -i '85 c\#define MAX_CTRL_BUFFER_LENGTH      65536' libusb/os/linux_usbfs.h
./configure --host=arm-linux-gnueabihf --prefix=/usr/local/libusb-rpi CC=arm-linux-gnueabihf-gcc --enable-udev=false
make
sudo make install
sudo sh -c 'echo /usr/local/libusb-rpi/lib >> /etc/ld.so.conf.d/libusb.conf'
sudo rm -f /lib/arm-linux-gnueabihf/libusb-1*
sudo ldconfig
ldconfig -p | grep libusb
