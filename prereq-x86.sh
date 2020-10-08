wget https://github.com/libusb/libusb/releases/download/v1.0.23/libusb-1.0.23.tar.bz2
tar -xvf libusb-1.0.23.tar.bz2
cd libusb-1.0.23
sed -i '85 c\#define MAX_CTRL_BUFFER_LENGTH      65536' libusb/os/linux_usbfs.h
./configure --prefix=/usr/lib/x86_64-linux-gnu --enable-udev=false
make
sudo make install
sudo sh -c 'echo /usr/lib/x86_64-linux-gnu >> /etc/ld.so.conf.d/libusb.conf'
# sudo rm -f /lib/x86_64-linux-gnu/libusb-1*
sudo ldconfig
ldconfig -p | grep libusb
