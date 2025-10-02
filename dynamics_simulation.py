import numpy as np

def dynamics(a0, vl, vr, d):
    if vr != vl:
        v_avg = (vl + vr) / 2
        r_c = d/2 * (vl + vr) / (vl - vr)
        w = np.atan2(-1 * np.sign(r_c) * v_avg, abs(r_c))
        v_c = 0
    else:
        r_c = np.inf
        w = 0
        v_c = np.array([0, vl]) # or vr, since vl == vr in this case
        
    return v_c, w, r_c
    
def state_update(x0, a0, dt, vl, vr, d):
    # Update the state based on the wheel velocities
    v_c, w, r_c = dynamics(a0, vl, vr, d)
    # xf = x0 + v * dt
    delta_a = w * dt
    if r_c == np.inf:
        # Straight line motion
        delta_x_body = v_c * dt
    else:
        # Circular motion
        delta_x_body = -1 * r_c * np.array([np.cos(delta_a) - 1, np.sin(delta_a)])
    delta_x = np.array([[np.cos(a0), -np.sin(a0)], [np.sin(a0), np.cos(a0)]]) @ delta_x_body
    xf = x0 + delta_x
    af = a0 + delta_a
    return xf, af

import matplotlib.pyplot as plt
import time
import pygame
from bluetooth_controller import setup_joystick, joystick_to_wheel_rpms

def run_simulation(d, wheel_radius):

    x0 = np.array([0, 0]) # initial position [m]
    a0 = 0 # initial angle [rad]
    dt = 0.01 # time step [s]
    t = 0

    # Initialize the plot
    fig, ax = plt.subplots()
    ax.set_aspect('equal')  # Make the figure square
    x_data = []
    y_data = []
    line, = ax.plot(x_data, y_data)
    ax.set_xlim(-10, 10) # Set fixed x-axis limits
    ax.set_ylim(-10, 10) # Set fixed y-axis limits

    fig.show()

    joystick = setup_joystick()

    # get current system time
    start_time = time.time()

    i = 0
    try:
        while True:

            pygame.event.pump()
            rpm_l, rpm_r = joystick_to_wheel_rpms(joystick, 0, 100)
            vl = rpm_l * 2 * np.pi / 60 * wheel_radius
            vr = rpm_r * 2 * np.pi / 60 * wheel_radius 
            vr *= -1  # fix left motor direction

            xf, af = state_update(x0, a0, dt, vl, vr, d)

            # Pause for a short duration
            now_time = time.time()
            elapsed_time = now_time - start_time
            exp_time = dt * (i + 1)
            early_wake_buffer = 0.005
            plt_pause = 0.001
            exp_continue_time = exp_time - early_wake_buffer - plt_pause
            sleep_time = exp_continue_time - elapsed_time
            if sleep_time > 0:
                # print("sleep_time: ", sleep_time)
                time.sleep(sleep_time)

            # Plot the trajectory
            if abs(t % 0.1) < 1e-4 or abs((t % 0.1) - 0.1) < 1e-4:
                now_time = time.time()
                elapsed_time = now_time - start_time
                print(f"act_t: {elapsed_time}, sim_t: {t}, vl: {vl}, vr: {vr}, xf: {xf}, af: {af}")

                # Update data
                x_data.append(xf[0])
                y_data.append(xf[1])
                line.set_data(x_data, y_data)

                # Remove previous heading line if it exists
                if hasattr(ax, 'heading_line'):
                    ax.heading_line.remove()

                # Calculate the end point of the heading line
                x_l = xf[0] - d/2 * np.cos(af)
                x_r = xf[0] + d/2 * np.cos(af)
                y_l = xf[1] - d/2 * np.sin(af)
                y_r = xf[1] + d/2 * np.sin(af)

                # Draw the heading line
                ax.heading_line, = ax.plot([x_l, x_r], [y_l, y_r], 'r-', linewidth=2)

                plt.draw()
                plt.pause(plt_pause)  # Pause to allow the plot to update

            # Set current time and position for next iteration
            t += dt
            x0, a0 = xf, af

            i += 1
            if i > 6000:  # Stop after 100 iterations
                break
    except KeyboardInterrupt:
        pass
    finally:
        pygame.quit()
        plt.close(fig) # Close the figure after the loop finishes

if __name__ == "__main__":
    d = 0.508 # distance between wheels [m]
    wheel_radius = 0.1034 # radius of the wheels [m]
    run_simulation(d, wheel_radius)