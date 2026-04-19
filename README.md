# Hardware_Hackathon
RIEEE x RUHart Hardware Hackathon Spring 2026


##Start Wifi:
nmcli device wifi list
sudo nmcli device wifi connect "YOUR_SSID" password "YOUR_PASSWORD"

##Start ssh:
sudo systemctl enable ssh
sudo systemctl start ssh

##Enter Project:
cd ~/Documents/Hardware_Hackathon/

##Raspberry Pi Stream Initialization:
Start Stream: ./stream.sh

##tts start:
cd ~/Documents/Hardware_Hackathon/pi_node/
python3 tts_reciever.py
