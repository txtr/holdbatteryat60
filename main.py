import subprocess
import asyncio
import kasa

IP_STRING = "192.168.1.XXX"
SLEEP_BETWEEN_CYCLES = 30  # in seconds


class Battery:
    def __init__(self):
        observation = subprocess.run(["pmset", "-g", "batt"], capture_output=True, text=True).stdout.strip()
        self.source = observation.split("Now drawing from '", 1)[-1].split("'")[0]
        self.batteries = []
        for battery_str in observation.split("\n -")[1:]:
            this_battery = dict()
            remainder = battery_str
            this_battery["battery_name"], remainder = remainder.split(" ", 1)
            this_battery["battery_id"], remainder = remainder.split("\t", 1)
            this_battery["battery_percentage"], remainder = remainder.split("; ", 1)
            this_battery["battery_status"], remainder = remainder.split("; ", 1)
            this_battery["battery_time_remaining"], this_battery["battery_present"] = remainder.split("present: ", 1)

            this_battery["battery_id"] = int(this_battery["battery_id"].split("(id=", 1)[-1].split(")", 1)[0])
            this_battery["battery_percentage"] = int(this_battery["battery_percentage"].split("%", 1)[0])
            this_battery["battery_present"] = True if this_battery["battery_present"] == "true" else False
            print(this_battery)
            self.batteries.append(this_battery)


async def connect(ip: str) -> kasa.SmartPlug:
    plug = kasa.SmartPlug(IP_STRING)
    await plug.update()
    return plug


async def main():
    p = await connect(IP_STRING)
    while True:
        await p.update()
        status = Battery().batteries.pop()
        if status["battery_percentage"] > 60:
            if p.is_on:
                await p.turn_off()
        if status["battery_percentage"] < 60:
            if p.is_off:
                await p.turn_on()
        await asyncio.sleep(SLEEP_BETWEEN_CYCLES)


if __name__ == "__main__":
    asyncio.run(main())
