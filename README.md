# eRecoverer

This program allows you to flash any update package for your device model and region. This allows you to fix devices even with a corrupt kernel (which prevents entering recovery) and FRP lock (which prevents flashing via fastboot).

## Installation

1. Download this repo to your computer
2. Install Python3.7  or higher. Make sure to include pip if available, and install Python to the PATH on Windows
3. Open a terminal or command prompt in this directory
4. Run `pip install -r requirements.txt`
5. Run `python3.7 server.py`
6. Enter the filelist URL (see below)

## Usage

1. Obtain your filelist URL. 
    - Visit https://pro-teammt.ru/firmware-database/
    - Enter the first 11 digits of the firmware you want to install. An example would be `LLD-L31C432` for a European Honor 9 Lite. 
    - Click "Find Model"
    - Find a file marked as **FullOTA-MF** or **FullOTA-MF-PV** for the build number you wish to install. It is safest to install the one you were running most recently.
    - Click the text **"filelist"**. Then right click **"Filelist Link"** and copy the link address. Paste it in a text file as you will have to reboot the computer meaning your clipboard will be cleared.
2. Enable WiFi Hotspot
    - The hotspot must use either **WPA2** or **open** security; WPA or others **will not work**.
    - Obviously, you need a WiFi adapter for this. You also need an ethernet or other internet connection to download the files. **You cannot use the WiFi as both a hotspot and standard adapter at the same time**.
3. Prepare your hosts file
    - The instructions differ on Windows and Unix-based OSes.
    - First, find your current IP address. Disconnect all other network cards other than the one with the hotspot. In this step, you can ignore anything that says 127.0.0.1. 
    - Configure the hosts file (remember to take a backup):
    - For Linux:
        - https://linuxconfig.org/how-to-find-ip-address-on-linux
        - Run `echo "(your IP address) query.hicloud.com" >> /etc/hosts` in a root shell
    - For Windows:
        - https://www.tp-link.com/us/faq-838.html
        - Use https://gist.github.com/zenorocha/18b10a14b2deb214dc4ce43a2d2e2992 to add `(your IP address) query.hicloud.com` at the end of the hosts file.
    - Reboot
    - Check it was successful by visiting http://query.hicloud.com/sp_ard_common/v2/Check.action. If the configuration was successful, this page will not load. If it shows something like `{"status":"-1"}` you did not configure hosts correctly or didn't reboot.
4. Connect an external network connection. Turn the hotspot back on, and check that you can access the Internet with the hotspot on. 
5. Run the server with `python3.7 server.py`
    - If any error occurs, it will tell you the solution **at the start of the error**.
6. It will prompt you for the filelist URL that you obtained in step 1. Enter it, and wait for the program to display `Starting server...`. When it does, boot the phone into eRecovery and press `Download and recovery`. eRecovery will guide you through the rest of the process.
7. Profit


