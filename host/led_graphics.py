"""
# Raspbot Remote Control Application (Raspbot RCA, Raspbot RCA-G), v1.1, revised for v1.2
# led_graphics module (for controlling onboard LED matrix)
# Made by Taian Chen
"""

try:
    print("[LG_RFP-ENCELADUS][INFO]: Starting imports...")
    from sense_hat import SenseHat
    from time import sleep
    sense = SenseHat()
except ImportError as e:
    SenseHat = None
    sleep = None
    print("[LG_RFP-ENCELADUS][FAIL]: Imports failed! See below for details.")
    print(e)
    exit(1)
except ImportWarning as e:
    print("[LG_RFP-ENCELADUS][FAIL]: Import warnings were raised! Please proceed with caution, see below for more details.")
    print(e)
pass

class led_graphics:
    """Main module class."""
    def __init__(self):
        print("[LG_RFP-ENCELADUS][INFO]: led_graphics loaded!")
    pass
    @staticmethod
    def InvalidCommand():
        """Exception when entered command parameter for led_graphics is invalid."""
        print("[LG_RFP-ENCELADUS][EXCP]: InvalidCommand, entered command parameter for led_graphics is invalid.")
        sense.clear()
    pass
    @staticmethod
    def display(command, frames):
        """Multi-purpose function for controlling SenseHAT's LED matrix. Accepts a command and frame parameter."""
        if command == "play" and frames is not None:
            print("[LG_RFP-ENCELADUS][INFO]: led_graphics is now displaying frames (from list format).")
            while True:
                for x in frames:
                    print("[LG_RFP-ENCELADUS][INFO]: Rendering frame...")
                    sense.set_pixels(x)
                    print("[LG_RFP-ENCELADUS][INFO]: Rendered.")
                    sleep(1)
                pass
            pass
        elif command == "stop":
            print("[LG_RFP-ENCELADUS][INFO]: led_graphics is now stopping display.")
            sense.clear()
            print("[LG_RFP-ENCELADUS][INFO]: led_graphics cleared.")
        elif command == "image":
            print("[LG_RFP-ENCELADUS][INFO]: led_graphics is now displaying frames (from image format).")
            for x in frames:
                print("[LG_RFP-ENCELADUS][INFO]: Rendering frame...")
                sense.load_image(x)
                print("[LG_RFP-ENCELADUS][INFO]: Rendered.")
                sleep(1)
            pass
        else:
            raise led_graphics.InvalidCommand
        pass
    pass
pass

lg = led_graphics()
