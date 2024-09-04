import board
import digitalio
from adafruit_debouncer import Debouncer

buttonA_pin = digitalio.DigitalInOut(board.D12)
buttonA_pin.direction = digitalio.Direction.INPUT
buttonA_pin.pull = digitalio.Pull.UP
buttonA = Debouncer(buttonA_pin)

while True:
    buttonA.update()

    if buttonA.value:
        print('not pressed')
    else:
        print('pressed')
