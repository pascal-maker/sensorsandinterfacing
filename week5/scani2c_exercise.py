
import smbus
bus = smbus.SMBus(1)
found = []
for addr in range(0x03, 0x78):
    try:
        bus.write_quick(addr)
        found.append(hex(addr))
    except:
        pass
print(found)
bus.close()
