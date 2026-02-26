from machine import Pin
import time

# Register Addresses
PROD_ID1 = 0x00
PROD_ID2 = 0x01
MOTION_STATUS = 0x02
DEL_X = 0x03
DEL_Y = 0x04
OP_MODE = 0x05

noSleep = 0xA0

# Pico pin mapping
SCLK_PIN = 2   # GP2
SDIO_PIN = 3   # GP3

sclk = Pin(SCLK_PIN, Pin.OUT)
sdio = Pin(SDIO_PIN, Pin.OUT)

# ------------------------------
def mouse_init():
    sclk.value(1)
    sclk.value(0)
    time.sleep_us(1)
    sclk.value(1)
    time.sleep_ms(320)
    sclk.value(0)
    write_register(OP_MODE, noSleep)

# ------------------------------
def read_register(address):
    global sdio
    sdio.init(Pin.OUT)

    # Send address (MSB first)
    for i in range(7, -1, -1):
        sclk.value(0)
        sdio.value((address >> i) & 1)
        sclk.value(1)

    # Switch to input
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

# ------------------------------
def write_register(address, data):
    global sdio
    address |= 0x80  # write flag
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

# ------------------------------
def to_int8(val):
    return val - 256 if val > 127 else val

# ------------------------------
print("Initializing sensor...")
mouse_init()

prod_id = read_register(PROD_ID1)
if prod_id == 0x31:
    print("Device OK")
else:
    print("Unknown device:", hex(prod_id))

# ------------------------------
while True:
    motion = read_register(MOTION_STATUS)
    print("Moved!", motion)

    dx = to_int8(read_register(DEL_X))
    dy = to_int8(read_register(DEL_Y))

    print("X:", dx, " Y:", dy)
    time.sleep(1)
