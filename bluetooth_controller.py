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

def axis_to_rpm(axis_val, MIN_RPM = 0, MAX_RPM = 100):
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
            # axis 0: left stick horizontal
            # 1: left vertical (inverted)
            # 2: right horizontal
            # 3: right vertical (inverted)
            # 4: right trigger
            # 5: left trigger

            # button 0: A
            # 1: B

            # hat 0: d pad horizontal
            # hat 1: d pad vertical (not inverted)

            # Get controller inputs
            left_stick_horiz = joystick.get_axis(0)
            right_trigger = joystick.get_axis(4)
            left_trigger = joystick.get_axis(5)
            dpad_horiz = joystick.get_hat(0)[0]
            button_b = joystick.get_button(1)
            
            # right trigger for forward speed
            right_trigger += 1.0  # make it positive
            right_trigger /= 2.0  # scale to 0.0 to 1.0
            total_for_rpm = axis_to_rpm(right_trigger)

            # left trigger for reverse speed
            left_trigger += 1.0  # make it positive
            left_trigger /= 2.0
            total_rev_rpm = axis_to_rpm(left_trigger)

            # determine direction
            if total_for_rpm > total_rev_rpm:
                direction = 1
                total_rpm = total_for_rpm
            else:
                direction = -1
                total_rpm = -total_rev_rpm                

            # if B button is pressed, boost speed
            if button_b:
                total_rpm *= 1.8

            # adjust individual wheel RPMs based on left stick
            DAMPING_COEFF = 0.9
            LEFT_STICK_DEADZONE = 0.1
            if left_stick_horiz < -LEFT_STICK_DEADZONE:
                left_rpm = total_rpm * (1.0 - abs(left_stick_horiz) * DAMPING_COEFF)
                right_rpm = total_rpm
            elif left_stick_horiz > LEFT_STICK_DEADZONE:
                right_rpm = total_rpm * (1.0 - abs(left_stick_horiz) * DAMPING_COEFF)
                left_rpm = total_rpm
            else:
                left_rpm = total_rpm
                right_rpm = total_rpm

            # override controls with crab turn
            CRAB_TURN_RPM = 40
            if dpad_horiz < 0:
                left_rpm = -CRAB_TURN_RPM
                right_rpm = CRAB_TURN_RPM
            elif dpad_horiz > 0:
                left_rpm = CRAB_TURN_RPM
                right_rpm = -CRAB_TURN_RPM

            # fix left motor direction
            left_rpm *= -1

            # debug_msg = f"Left: {axis_val:.2f}, Right: {rigt_axis_val:.2f}, Left Trigger: {left_axis_val:.2f}, Right Trigger: {rigt_axis_val:.2f}"
            msg = f"STEP R{right_rpm:.2f} L{left_rpm:.2f}\n"
            print(msg)
            if test_mode:
                # print(debug_msg)
                continue
            else:
                # Send RPM over serial (as string, e.g., "RPM:1234\n")
                ser.write(msg.encode())

            time.sleep(0.05)
    except KeyboardInterrupt:
        pass
    finally:
        ser.close()
        pygame.quit()

if __name__ == "__main__":
    ser = setup_serial()
    # ser = None
    joystick = setup_joystick()
    game_loop(ser, joystick, test_mode=False)