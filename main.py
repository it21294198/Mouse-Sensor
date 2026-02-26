import time
import board
import digitalio
import usb_hid
from adafruit_hid.mouse import Mouse

# ---------------- USB Mouse ----------------
mouse = Mouse(usb_hid.devices)

# -------- Sensor Registers --------
PROD_ID1 = 0x00
MOTION_STATUS = 0x02
DEL_X = 0x03
DEL_Y = 0x04
OP_MODE = 0x05
noSleep = 0xA0

# -------- Pins --------
SCLK_PIN = board.GP2
SDIO_PIN = board.GP3

sclk = digitalio.DigitalInOut(SCLK_PIN)
sclk.direction = digitalio.Direction.OUTPUT

sdio = digitalio.DigitalInOut(SDIO_PIN)
sdio.direction = digitalio.Direction.OUTPUT

# ---------------- Sensor Functions ----------------
def mouse_init():
    sclk.value = True
    sclk.value = False
    time.sleep(0.000001)
    sclk.value = True
    time.sleep(0.320)
    sclk.value = False
    write_register(OP_MODE, noSleep)

def read_register(address):
    sdio.direction = digitalio.Direction.OUTPUT

    for i in range(7, -1, -1):
        sclk.value = False
        sdio.value = (address >> i) & 1
        sclk.value = True

    sdio.direction = digitalio.Direction.INPUT
    time.sleep(0.000003)

    res = 0
    for i in range(7, -1, -1):
        sclk.value = False
        sclk.value = True
        if sdio.value:
            res |= (1 << i)

    time.sleep(0.000003)
    return res

def write_register(address, data):
    address |= 0x80
    sdio.direction = digitalio.Direction.OUTPUT

    for i in range(7, -1, -1):
        sclk.value = False
        sdio.value = (address >> i) & 1
        sclk.value = True

    for i in range(7, -1, -1):
        sclk.value = False
        sdio.value = (data >> i) & 1
        sclk.value = True

    time.sleep(0.0001)

def to_int8(v):
    return v - 256 if v > 127 else v

# ---------------- Init ----------------
time.sleep(2)  # wait for USB enumeration
mouse_init()

pid = read_register(PROD_ID1)
print("Product ID:", hex(pid))

SCALE = 1.0  # adjust sensitivity

# ---------------- Main Loop ----------------
while True:
    motion = read_register(MOTION_STATUS)
    if motion & 0x80:
        dx = to_int8(read_register(DEL_X))
        dy = to_int8(read_register(DEL_Y))

        mx = int(dx * SCALE)
        my = int(dy * SCALE)

        if mx or my:
            mouse.move(mx, my)

    time.sleep(0.005)
