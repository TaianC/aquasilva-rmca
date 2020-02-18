"""
# Raspbot Remote Control Application (Raspbot RCA, Raspbot RCA-G), v1.1
# nav module (for navigation)
# creates GUI
# Made by Taian Chen (perpetualCreations)
"""

try:
    print("[INFO]: Starting imports...")
    import tkinter
    from tkinter import messagebox
    from subprocess import call
    from time import gmtime
    from time import strftime
    from time import sleep
    from sense_hat import SenseHat
    import serial
    from sys import exit
except ImportError as e:
    tkinter = None
    call = None
    gmtime = None
    strftime = None
    messagebox = None
    sleep = None
    SenseHat = None
    serial = None
    print("[FAIL]: Imports failed! See below.")
    print(e)
    exit(1)
except ImportWarning as e:
    print("[FAIL]: Import warnings were raised! Please proceed with caution, see below for more details.")
    print(e)
pass

class nav:
    """Creates a GUI interface for user to start navigating."""
    def __init__(self):
        print("[INFO]: Nav loaded!")
        print("[INFO]: Starting serial connection with Arduino microcontroller...")
        try:
            self.arduino = serial.Serial("/dev/ttyACM0", timeout = 5)
        except serial.serialutil.SerialException as se:
            print("[FAIL]: Failed to create connection with Arduino microcontroller! Details below.")
            print(se)
            exit(1)
        pass
        print("[INFO]: Declaring variables...")
        self.content = ""
        self.task = ""
        self.nav_task_active = False
        self.distance_check = True
        self.distance_request = True
        self.nav_time = 0
        print("[INFO]: Creating SenseHAT interface object...")
        self.sense = SenseHat()
        print("[INFO]: Loading graphics...")
        self.root = tkinter.Tk()
        self.root.title("Raspbot RCA-G: Navigation")
        self.root.configure(bg = "#344561")
        self.root.geometry('{}x{}'.format(380, 375))
        self.root.resizable(width = False, height = False)
        graphics_title = tkinter.Label(self.root, text = "Nav Controls", fg = "white", bg = "#344561", font = ("Calibri", 16))
        graphics_title.grid(row = 0, column = 0)
        self.graphics_nav_telemetry = tkinter.Text(self.root, width = 25, height = 14)
        self.graphics_nav_telemetry.configure(state = tkinter.DISABLED)
        self.graphics_nav_telemetry.grid(row = 1, column = 0, padx = (10, 15), pady = (0, 14))
        graphics_nav_frame_buttons = tkinter.Frame(self.root, bg = "#344561")
        graphics_nav_button_forward = tkinter.Button(graphics_nav_frame_buttons, text = "F", fg = "white", bg = "#344561", font = ("Calibri", 12), command = lambda: nav.set_task(self, "F"))
        graphics_nav_button_forward.pack(side = tkinter.TOP)
        graphics_nav_button_backward = tkinter.Button(graphics_nav_frame_buttons, text = "B", fg = "white", bg = "#344561", font = ("Calibri", 12), command = lambda: nav.set_task(self, "B"))
        graphics_nav_button_backward.pack(side = tkinter.BOTTOM)
        graphics_nav_frame_buttons_left = tkinter.Frame(graphics_nav_frame_buttons, bg = "#344561")
        graphics_nav_button_left_forward = tkinter.Button(graphics_nav_frame_buttons_left, text = "LF", fg = "white", bg = "#344561", font = ("Calibri", 12), command = lambda: nav.set_task(self, "Y")) # TODO confirm correct byte command
        graphics_nav_button_left_forward.pack(side = tkinter.TOP)
        graphics_nav_button_left_backward = tkinter.Button(graphics_nav_frame_buttons_left, text = "LB", fg = "white", bg = "#344561", font = ("Calibri", 12), command = lambda: nav.set_task(self, "Z"))
        graphics_nav_button_left_backward.pack(side = tkinter.BOTTOM)
        graphics_nav_frame_buttons_left.pack(side = tkinter.LEFT)
        graphics_nav_frame_buttons_right = tkinter.Frame(graphics_nav_frame_buttons, bg = "#344561")
        graphics_nav_buttons_right_forward = tkinter.Button(graphics_nav_frame_buttons_right, text = "RF", fg = "white", bg = "#344561", font = ("Calibri", 12), command = lambda: nav.set_task(self, "W"))
        graphics_nav_buttons_right_forward.pack(side = tkinter.TOP)
        graphics_nav_buttons_right_backwards = tkinter.Button(graphics_nav_frame_buttons_right, text = "RB", fg = "white", bg = "#344561", font = ("Calibri", 12), command = lambda: nav.set_task(self, "X"))
        graphics_nav_buttons_right_backwards.pack(side = tkinter.BOTTOM)
        graphics_nav_frame_buttons_right.pack(side = tkinter.RIGHT)
        graphics_nav_frame_buttons.grid(row = 1, column = 1, padx = (0, 10))
        graphics_nav_frame_buttons_spin = tkinter.Frame(self.root, bg = "#344561")
        graphics_nav_buttons_spin_clockwise = tkinter.Button(graphics_nav_frame_buttons_spin, text = "S", fg = "white", bg = "#344561", font = ("Calibri", 12), command = lambda: nav.set_task(self, "S"))
        graphics_nav_buttons_spin_clockwise.pack(side = tkinter.LEFT)
        graphics_nav_buttons_spin_counterclockwise = tkinter.Button(graphics_nav_frame_buttons_spin, text = "C", fg = "white", bg = "#344561", font = ("Calibri", 12), command = lambda: nav.set_task(self, "C"))
        graphics_nav_buttons_spin_counterclockwise.pack(side = tkinter.RIGHT)
        graphics_nav_frame_buttons_spin.grid(row= 2, column = 1, padx = (0, 10), pady = (10, 0))
        graphics_nav_frame_entry = tkinter.Frame(self.root, bg = "#344561")
        self.graphics_nav_entry_time = tkinter.Entry(graphics_nav_frame_entry, fg = "white", bg = "#344561", font = ("Calibri", 12))
        self.graphics_nav_entry_time.pack(side = tkinter.LEFT)
        graphics_nav_button_time_submit = tkinter.Button(graphics_nav_frame_entry, text = "<", fg = "white", bg = "#344561", font = ("Calibri", 12), command = lambda: nav.time_check(self))
        graphics_nav_button_time_submit.pack(side = tkinter.RIGHT)
        graphics_nav_frame_entry.grid(row = 2, column = 0)
        graphics_nav_buttons_execute = tkinter.Button(self.root, text = "Execute Nav", fg = "white", bg = "#344561", width = 20, font = ("Calibri", 12), command = lambda: nav.process_command(self, self.task))
        graphics_nav_buttons_execute.grid(row = 3, column = 0, padx = (60, 0), pady = (10, 0))
        self.root.mainloop()
    pass
    def set_task(self, task):
        """Sets task variable, because lambda doesn't support variable assignment."""
        self.task = task
        print("[INFO]: Set task variable to " + self.task + ".")
    pass
    def time_check(self):
        """Checks if inputted time value is a number."""
        print("[INFO]: Checking submitted nav time...")
        time_input_raw = self.graphics_nav_entry_time.get()
        time_input = 0
        try:
            time_input = int(time_input_raw)
        except ValueError:
            print("[FAIL]: Submitted nav time is invalid, is not an integer!")
            messagebox.showerror("Raspbot RCA-G: Bad Nav Time", "Submitted nav time is invalid, not an integer!")
            self.graphics_nav_entry_time.delete("0", tkinter.END)
            return None
        pass
        messagebox.showinfo("Raspbot RCA-G: Valid Nav Time", "Nav time submission successful!")
        time_input_str = str(time_input)
        print("[INFO]: Submission valid, accepted value. (submitted value was " + time_input_str + ")")
        self.nav_time = time_input
    pass
    def display(self, content):
        """Accepts string input and displays it on GUI text box."""
        print("[INFO]: Displaying to text box...")
        self.graphics_nav_telemetry.configure(state=tkinter.NORMAL)
        self.graphics_nav_telemetry.delete("1.0", tkinter.END)
        self.graphics_nav_telemetry.insert("1.0", content)
        self.graphics_nav_telemetry.configure(state=tkinter.DISABLED)
        self.root.update_idletasks()
    pass
    def get_distance(self):
        """Gets distance from ToF sensor and returns as list, indexed as 0 being a string output, 1 being a integer output."""
        if self.distance_request is True:
            print("[INFO]: Collecting distance data...")
            nav.display(self, "Collecting distance data...")
            self.arduino.write(b"T")
            print("[INFO]: Decoding byte data...")
            distance = self.arduino.readline()
            distance = distance.decode(encoding="utf-8", errors="replace")
            distance = distance.rstrip('\n')
            distance = str(distance)
            if distance == "(out of range)":
                distance_int = None
            elif distance == "(fail)":
                distance_int = None
                print("[FAIL]: ToF sensor failed!")
                nav.stop(self)
                messagebox.showerror("Raspbot RCA-G: ToF Sensor Failed!", "The Time of Flight (ToF) sensor has failed! Without it Raspbot cannot perform distance checks. A dialogue will appear to disable distance checks and continue with the navigation.")
                override = messagebox.askyesno("Raspbot RCA-G: Override Distance Check?", "Disable distance checks and continue with the navigation?")
                if override is True:
                    print("[INFO]: Disabled distance check.")
                    self.distance_request = False
                else:
                    print("[INFO]: Ended navigation early due to failed ToF sensor.")
                pass
            elif distance == "":
                distance_int = None
            else:
                distance_int = int(distance)
            pass
            print("[INFO]: Collected distance data, returning...")
            nav.display(self, "Collected distance data, returning...")
            return [distance, distance_int]
        else:
            return ["n/a", None]
        pass
    pass
    def runtime(self, time):
        """Function containing runtime processes while a navigation is active."""
        if time != 0:
            distance_data = nav.get_distance(self)
            distance_str = distance_data[0]
            distance_int = distance_data[1]
            if distance_int is None:
                distance_int = 1999
            pass
            print("[INFO]: Checking distance data for incoming collisions...")
            if distance_int < 40 and self.distance_check is True:
                print("[FAIL]: Distance from object facing front of vehicle is less than 30mm! Collision warning!")
                nav.display(self, "Collision warning!" + "\n" + "Object less than 30mm away.")
                nav.stop(self)
                messagebox.showwarning("Raspbot RCA-G: Collision Warning!", "The ToF distance sensor has detected an object less than 30mm away. A dialogue will appear to resume or stop navigation.")
                str_time = str(time)
                override = messagebox.askyesno("Raspbot RCA-G: Override Distance Check?", "Override and resume navigation? Your current nav has " + str_time + " left.")
                if override is True:
                    print("[INFO]: Warning ignored, continued navigation.")
                    nav.display(self, "Continuing with navigation...")
                    self.distance_check = False
                else:
                    print("[INFO]: Ended navigation early due to collision warning.")
                    nav.display(self, "Navigation ended.")
                    return None
                pass
            else:
                print("[INFO]: Collecting orientation, compass, and acceleration data...")
                orientation_raw = self.sense.get_orientation_degrees()
                compass_raw = self.sense.compass
                accelerometer_data = self.sense.get_accelerometer_raw()
                compass = round(compass_raw, 2)
                print("[INFO]: Processing raw data...")
                orientation_roll = str(round(orientation_raw["roll"], 2))
                orientation_pitch = str(round(orientation_raw["pitch"], 2))
                orientation_yaw = str(round(orientation_raw["yaw"], 2))
                orientation = "[Orientation in Degrees]" + "\n" + "Roll: " + orientation_roll + "\n" + "Pitch: " + orientation_pitch + "\n" + "Yaw: " + orientation_yaw
                compass_str = "[Compass]" + "\n" + str(compass) + " Degrees"
                accelerometer_x = str(round(accelerometer_data["x"], 2) * 9.81)
                accelerometer_y = str(round(accelerometer_data["y"], 2) * 9.81)
                accelerometer_z = str(round(accelerometer_data["z"], 2) * 9.81)
                accelerometer = "[Acceleration in m/s]" + "\n" + "X: " + accelerometer_x + "\n" + "Y: " + accelerometer_y + "\n" + "Z: " + accelerometer_z
                distance_output = "[Distance to Collision]" + "\n" + distance_str + " mm"
                self.content = orientation + "\n" + accelerometer + "\n" + compass_str + "\n" + distance_output
                nav.display(self, self.content)
                print("[INFO]: Process cycle complete.")
                time -= 1
                sleep(1)
                nav.runtime(self, time)
                return None
            pass
        elif time == 0:
            nav.stop(self)
            print("[INFO]: Ended navigation, task complete!")
            nav.display(self, "Navigation complete.")
            return None
        else:
            raise Exception("Navigation time variable is a negative or otherwise invalid variable type!")
        pass
    pass
    def process_command(self, direction):
        """Asks user for confirmation and does pre-navigation check for existing navigation , then finally executes movement."""
        confirm = messagebox.askyesno("Raspbot RCA-G: Nav Confirm", "Are you sure you want to execute this navigation?")
        if confirm is True:
            print("[INFO]: Confirmed navigation by user.")
            if self.nav_task_active is True:
                nav.stop(self)
            pass
            direction_byte = direction.encode(encoding = "ascii", errors = "replace")
            print("[INFO]: Started navigation.")
            self.arduino.write(direction_byte)
            print("[INFO]: Starting runtime loop...")
            nav.runtime(self, self.nav_time)
        else:
            print("[INFO]: Cancelled navigation by user.")
        pass
    pass
    def stop(self):
        """Stops navigation."""
        print("[INFO]: Stopped navigation.")
        self.arduino.write(b"A")
    pass
pass

n = nav()
