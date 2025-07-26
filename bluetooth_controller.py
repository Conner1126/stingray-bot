import pygame
import serial
import time

def setup_serial():
    # Use '/dev/ttyUSB0' or '/dev/ttyACM0' for Raspberry Pi Linux
    try:
        ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
        print("Serial port opened successfully.")
        return ser
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        exit()

def axis_to_rpm(axis_val, MIN_RPM = 0, MAX_RPM = 60):
    # Map -1.0 to 1.0 to MIN_RPM to MAX_RPM
    return axis_val * (MAX_RPM - MIN_RPM) + MIN_RPM

def setup_joystick():

    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("No joystick detected!")
        exit()

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    return joystick

def game_loop(ser, joystick, test_mode=False):
    try:
        while True:
            pygame.event.pump()

            # left stick vertical axis (axis 1)
            axis_val = joystick.get_axis(1)
            rpm = axis_to_rpm(-axis_val)  # invert if needed

            # Read all axes
            axes = [joystick.get_axis(i) for i in range(joystick.get_numaxes())]

            # Read all buttons
            buttons = [joystick.get_button(i) for i in range(joystick.get_numbuttons())]

            # Read all hats (D-pad)
            hats = [joystick.get_hat(i) for i in range(joystick.get_numhats())]

            print("Axes:", ["{:.3f}".format(a) for a in axes])
            print("Buttons:", buttons)
            print("Hats:", hats)
            print("-" * 40)

            # debug_msg = f"Left: {axis_val:.2f}, Right: {rigt_axis_val:.2f}, Left Trigger: {left_axis_val:.2f}, Right Trigger: {rigt_axis_val:.2f}"
            # msg = f"STEP R{right_rpm:.2f} L{left_rpm:.2f}\n"
            if test_mode:
                # print(debug_msg)
                continue
            else:
                # Send RPM over serial (as string, e.g., "RPM:1234\n")
                ser.write(msg.encode())

            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        ser.close()
        pygame.quit()

if __name__ == "__main__":
    # ser = setup_serial()
    ser = None
    joystick = setup_joystick()
    game_loop(ser, joystick, test_mode=True)