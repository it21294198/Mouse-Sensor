from machine import Pin
import time
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
SCLK_PIN = 2   # GP2
SDIO_PIN = 3   # GP3

sclk = Pin(SCLK_PIN, Pin.OUT)
sdio = Pin(SDIO_PIN, Pin.OUT)

# ---------------- Sensor Functions ----------------
def mouse_init():
    sclk.value(1)
    sclk.value(0)
    time.sleep_us(1)
    sclk.value(1)
    time.sleep_ms(320)
    sclk.value(0)
    write_register(OP_MODE, noSleep)

def read_register(address):
    sdio.init(Pin.OUT)
    for i in range(7, -1, -1):
        sclk.value(0)
        sdio.value((address >> i) & 1)
        sclk.value(1)

    sdio.init(Pin.IN)
    time.sleep_us(3)

    res = 0
    for i in range(7, -1, -1):
        sclk.value(0)
        sclk.value(1)
        if sdio.value():
            res |= (1 << i)
    time.sleep_us(3)
    return res

def write_register(address, data):
    address |= 0x80
    sdio.init(Pin.OUT)
    for i in range(7, -1, -1):
        sclk.value(0)
        sdio.value((address >> i) & 1)
        sclk.value(1)
    for i in range(7, -1, -1):
        sclk.value(0)
        sdio.value((data >> i) & 1)
        sclk.value(1)
    time.sleep_us(100)

def to_int8(v):
    return v - 256 if v > 127 else v

# ---------------- Init ----------------
time.sleep(2)  # wait for USB to enumerate
mouse_init()

pid = read_register(PROD_ID1)
print("Product ID:", hex(pid))

# Sensitivity scaling
SCALE = 1.0   # increase if movement is slow

# ---------------- Main Loop ----------------
while True:
    motion = read_register(MOTION_STATUS)
    if motion & 0x80:   # motion bit set
        dx = to_int8(read_register(DEL_X))
        dy = to_int8(read_register(DEL_Y))

        mx = int(dx * SCALE)
        my = int(dy * SCALE)

        if mx or my:
            # USB HID: positive Y is down
            mouse.move(mx, my)

    time.sleep_ms(5)