import matplotlib.pyplot as plt
import numpy as np

CPU_Temperature, Fan_Speed = np.loadtxt('sample.txt', delimiter='|', unpack=True)
time = np.linspace(0, 2010, 202)

plt.plot(time, CPU_Temperature, color='red', linewidth=3, label='CPU Temperature(°C)')
plt.plot(time, Fan_Speed, color='blue', linewidth=3, label='Fan Speed')

plt.xlabel('Second(s)')
#plt.ylabel('CPU temperature/Fan speed')
plt.title('Raspberry Pi Fan Start When CPU Temperature is Above 50°C\n Not Stop Until Temperature is Below 40°C')
plt.legend()
plt.show()
