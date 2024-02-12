import os
import dataclasses
import typing
import json
import libximc.highlevel as ximc
from ThorlabsPM100 import ThorlabsPM100, USBTMC

def clear() -> None:
    if os.name == 'nt':
        _ = os.system("cls")
    else:
        _ = os.system("clear")

Angle = typing.NewType("Angle", int)
Step = typing.NewType("Step", int)
NoiseDB = typing.NewType("NoiseDB", float)

@dataclasses.dataclass
class NoiseMap:
    noise: NoiseDB
    step: Step

@dataclasses.dataclass
class Motor:
    full_step: Step
    port: str = None
    motor: ximc.Axis = None
    current_step: Step = None
    current_angle: Angle = None
    current_noise: NoiseDB = None
    noise_map: NoiseMap = None

@dataclasses.dataclass
class PowerMeter:
    port: str
    powermeter: ThorlabsPM100
    current_power: str = None

menu_dict = {
    "0": "Set zero point",
    "1": "Rotate motor by angle",
    "2": "Rotate motor by step",
    "3": "Return to zero",
    "9": "Calibrate noise map",
    "Q": "Quit"
}

def connect_motor() -> Motor:
    for port_num in range(0,11):
        port = '/dev/ttyACM' + str(port_num)
        motor = Motor(
            full_step = 28800,
            port = port,
            motor = ximc.Axis('xi-com:' + port),
        )
        try:
            motor.motor.open_device()
            motor.motor.get_status()
            motor.motor.close_device()
        except:
            motor = Motor(
            full_step = 28800,
            port = None,
            motor = None,
        )
        else:
            break
    return motor

def connect_power_meter() -> PowerMeter:
    for port_num in range(0,11):
        port = '/dev/usbtmc' + str(port_num)
        try:
            inst = USBTMC(device=port)
            powermeter = PowerMeter(
                port = port,
                powermeter = ThorlabsPM100(inst=inst)
            )
        except:
            powermeter = PowerMeter(
                port = None,
                powermeter = None
            )
        else:
            break
    return powermeter

def angle_to_step(angle: Angle, full_step: Step) -> Step:
    step = Step((angle / 360 * full_step))
    return step

def step_to_angle(step: Step, full_step: Step) -> Angle:
    angle = Angle((step / full_step * 360))
    return angle

def get_motor_status(motor: Motor) -> None:
    try:
        motor.motor.open_device()
        motor.current_step = motor.motor.get_status().CurPosition
        motor.current_angle = step_to_angle(step=motor.current_step, full_step=motor.full_step)
        motor.motor.close_device()
    except:
        pass

def set_zero_point(motor: Motor) -> None:
    try:
        motor.motor.open_device()
        motor.motor.command_zero()
        motor.motor.close_device()
        get_motor_status(motor=motor)
    except:
        pass

def print_motor_status(motor: Motor) -> None:
    get_motor_status(motor=motor)
    if motor.current_step == motor.full_step:
            set_zero_point(motor=motor)
    print("Standa motor connected at port:", motor.port)
    print("Current angle:", motor.current_angle)
    print("Current step:", motor.current_step, "/", motor.full_step)
    print("Estimated noise level:", motor.current_noise)

def print_power_meter_status(powermeter: PowerMeter) -> None:
    try:
        print("Power meter connected at port:", powermeter.port)
        powermeter.current_power = powermeter.powermeter.read
        print("Power:", powermeter.current_power, "W")
    except:
        pass

def step_motor(motor: Motor, step: Step) -> None:
    try:
        motor.motor.open_device()
        motor.motor.command_movr(int(step), 0)
        motor.motor.command_wait_for_stop(refresh_interval_ms=10)
        motor.motor.close_device()
    except:
        pass

def return_to_zero(motor: Motor) -> None:
    try:
        step_delta = -motor.current_step
        step_motor(motor=motor, step=step_delta)
    except:
        pass

def calibrate_noise(motor: Motor, powermeter: PowerMeter):
    return_to_zero(motor=motor)
    noise_map = {}
    step = angle_to_step(angle=1, full_step=motor.full_step)
    for i in range(0, 360):
        noise_map[i] = powermeter.powermeter.read
        step_motor(motor=motor, step=step)
    
    with open("calibration.json", "w") as file:
        json.dump(noise_map, file, indent=4)

def main() -> None:
    while True:
        clear()
        motor = connect_motor()
        print_motor_status(motor=motor)

        powermeter = connect_power_meter()
        print_power_meter_status(powermeter=powermeter)

        print("Select option:")
        for key, value in menu_dict.items():
            print(key + ")", value)
        user_input = input()
        if user_input.lower() == 'q':
            break
        try:
            option = int(user_input)
        except:
            print("Invalid input")
    
        if option == 0:
            set_zero_point(motor=motor)
            option = -1

        while option == 1 or option == 2:
            clear()
            print_motor_status(motor=motor)
            user_input = input("Selected option: " + menu_dict.get(str(option)) + "\nEnter number or q to return to previous menu: ")
            if user_input.lower() == 'q':
                option = -1
                break
            try:
                step = int(user_input)
            except:
                print("Invalid input")
            else:
                if option == 1:
                    step = angle_to_step(angle=step, full_step=motor.full_step)
                step_motor(motor=motor, step=step)

        if option == 3:
            return_to_zero(motor=motor)

        if option == 9:
            calibrate_noise(motor=motor, powermeter=powermeter)

if '__main__' == __name__:
    main()