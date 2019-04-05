#Kansas State University
#Electronics Design Club
#Interactive Display (Spring Open House, 2019)
#Author(s): Weston Harder

import paho.mqtt.client
from time import sleep

def main():
    #Initial setup
    tc = touch_controller()
    mqtt_pub = mqtt_publisher()
    
    #Main loop
    while(True):
        #Go through every sensor and check for touch
        tc.scan()

        #Go through each key number
        for key in tc.get_active_keys():
            mqtt_pub.publish_touch(key)

    return

class mqtt_publisher(object):
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 1883
        self.topic = "interactive_display/touch_events"
        self.mqtt_client = paho.mqtt.client.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.connect()
        self.client.loop_start()
        
        return
    
    def connect(self):
        print("Attempting to connect to \"{}:{}\"".format(self.host, self.port))
        self.client.connect_async(self.host, self.port)
        return

    def on_connect(self, client, userdata, flags, rc):
        if rc==0:
            print("Connected to MQTT server successfully.")
        else:
            print("Failed to connect to the MQTT server. rc = {}".format(rc))
            print("See http://www.steves-internet-guide.com/client-connections-python-mqtt/ or https://pypi.org/project/paho-mqtt/ for help.")
            self.connect()

        return

    def on_disconnect(self, client, userdata, rc):
        print("Disconnected from the MQTT server. rc = {}".format(rc))
        print("See http://www.steves-internet-guide.com/client-connections-python-mqtt/ or https://pypi.org/project/paho-mqtt/ for help.")
        self.connect()

        return

    def publish_touch(self, key):
        rc = self.mqtt_client.publish(self.topic, str(key))

        if rc:
            print("Failed to print message \"{}\" to \"{}\". rc = {}".format(str(key), self.topic, rc))
            print("See https://pypi.org/project/paho-mqtt/ for help.")

        return

class selection_manager(object):
    def __init__(self):
        self.max_touch_ic = 79
        self.touch_ic = self.max_touch_ic + 1

        self.reset()

        return

    def get_max(self):
        return self.max_touch_ic

    def get_number(self):
        return self.max_touch_ic + 1

    def get_selection(self):
        return self.touch_ic

    def increment(self):
        #Set CS_IN low
        #Set CLK high
        #Wait a few ms???
        #Set CLK low
        self.touch_ic += 1
        return

    def reset(self):
        #Set CS_IN low
        #Set CLK low
        #Set RESET low
        #Wait a few ms???
        #Set RESET high
        self.touch_ic = self.max_touch_ic + 1
        return

    def select(self, new_touch_ic):
        #If selection is valid
        if new_touch_ic >= 0 and new_touch_ic <= self.max_touch_ic:
            #If selection is below current selection
            if new_touch_ic < self.touch_ic:
                #Select touch IC 0
                self.reset()
                #Set CS_IN high
                #Set CLK high
                #Wait a few ms???
                #Set CLK low
                self.touch_ic = 0

            #While selection is above current selection
            while new_touch_ic > self.touch_ic:
                self.increment()

            return True

        #If selection is invalid
        else:
            self.reset()
            return False


class touch_controller(object):
    def __init__(self):
        self.sm = selection_manager()
        self.key_states = list()
        self.keys = 11

        #Initialize all keyy states to False
        for _ in range(0, self.get_touch_ic_number()):
            for _ in range(0, self.keys):
                self.key_states.append(False)

        #Setup all touch ICs
        for i in range(0, self.get_touch_ic_number()):
            self.control_setup(i)
        
        #Calibrate all touch ICs
        for i in range(0, self.get_touch_ic_number()):
            self.control_calibrate(i)

        return
    
    #def get_touch_status()

    def control_calibrate(self, touch_ic):
        if self.sm.select(touch_ic):
            #SPI: Send 0x03 to calibrate all keys
            
            #Wait at least 150 us before communications can resume
            sleep(150/1000000)

            return True

        else:
            return False

    def control_erase_eeprom_and_reset(self, touch_ic):
        if self.sm.select(touch_ic):
            #SPI: Send 0x0c to erase settings stored in EEPROM and reset touch IC (revert touch IC to default settings)
            
            #Wait at least 50 ms before communications can resume
            sleep(50/1000)

            return True

        else:
            return False

    def control_reset(self, touch_ic):
        if self.sm.select(touch_ic):
            #SPI: Send 0x04 to reset
            
            #Wait at least 160 ms before communications can resume
            sleep(160/1000)

            return True

        else:
            return False

    def control_restore_from_eeprom(self, touch_ic):
        if self.sm.select(touch_ic):
            #SPI: Send 0x0b to restore RAM contents from EEPROM (revert to checkpoint without needing to do a full reset)
            
            #Wait at least 150 ms before communications can resume
            sleep(150/1000)

            return True

        else:
            return False

    def control_setup(self, touch_ic):
        #Perform initialization on all touch ICs
            #Set the MODE bit in the Device Mode setup
            #Use a timed trigger (specified length of time or 0 for free run mode)
            #No guard channel key
            #No SYNC pin
            #Possibly use detection integrator to make sure it is touched
            #Burst length limitation??? Probably no
            #Adjacent Key Suppression??? Probably no
            #Don't use CRC checking
        
        if self.sm.select(touch_ic):
            #SPI: Send 0x01 to start setup
            #SPI: Send 42 bytes of setup data
            #If concerned about setup working properly:
                #SPI: Request a dump of setup data
                #Check to make sure setup data is correct
            
            #Wait at least 150 us before communications can resume
            sleep(150/1000000)

            return True

        else:
            return False

    def control_sleep(self, touch_ic):
        if self.sm.select(touch_ic):
            #SPI: Send 0x05 to sleep
            
            #Wait at least 150 us after a low signal is applied to the SS_bar pin before communications can resume
            sleep(150/1000000)

            return True

        else:
            return False

    def control_store_to_eeprom(self, touch_ic):
        if self.sm.select(touch_ic):
            #SPI: Send 0x0a to store RAM contents to EEPROM (basically a checkpoint that can be reached again by calling reset)
            
            #Wait at least 200 ms before communications can resume
            sleep(200/1000)

            return True

        else:
            return False

    def get_active_keys(self):
        #Return the indices of all active (touched) keys
        return [index for index, key_state in self.key_states if key_state]

    def get_key_count(self):
        return self.keys

    def get_key_state(self, key):
        return self.key_states[key]

    def get_touch_ic_key_state(self, touch_ic, key):
        return self.key_states[(touch_ic * self.get_key_count()) + key]

    def get_touch_ic_number(self):
        return self.sm.get_number()
    
    def report_all_keys(self, touch_ic):
        if self.sm.select(touch_ic):
            #SPI: Send 0xc1 to request a binary report on all 11 keys
            #SPI: Receive 2 bytes

            #           Bit 7   Bit 6   Bit 5   Bit 4   Bit 3   Bit 2   Bit 1   Bit 0
            # Byte 0                                            KEY_10  KEY_9   KEY_8
            # Byte 1    KEY_7   KEY_6   KEY_5   KEY_4   KEY_3   KEY_2   KEY_1   KEY_0
            
            #Parse data and store in self.key_states (For each key, store True if on/triggered and False if off/not triggered)

            #Wait at least 200 ms before communications can resume
            sleep(200/1000)

            return True

        else:
            return False
    
    def scan(self):
        success = True

        for i in range(0, self.get_touch_ic_number()):
            success = success and self.report_all_keys(i)

        return success

if __name__ == "__main__":
    main()