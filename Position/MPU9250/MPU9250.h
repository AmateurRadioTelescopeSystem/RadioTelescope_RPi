/*
 Note: The MPU9250 is an I2C sensor and uses the Arduino Wire library.
 Because the sensor is not 5V tolerant, we are using a 3.3 V 8 MHz Pro Mini or
 a 3.3 V Teensy 3.1. We have disabled the internal pull-ups used by the Wire
 library in the Wire.h/twi.c utility file. We are also using the 400 kHz fast
 I2C mode by setting the TWI_FREQ  to 400000L /twi.h utility file.
 */
#ifndef _MPU9250_H_
#define _MPU9250_H_

#include <iostream>
#include <fstream>
#include <cmath>
#include <unistd.h>
#include <chrono>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <stdint.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>
#include "MPU9250_Constants.h"


// Using the MPU-9250 breakout board, ADO is set to 0
// Seven-bit device address is 110100 for ADO = 0 and 110101 for ADO = 1
#define ADO 0

#if ADO == 1
	#define MPU9250_ADDRESS 0x69  // Device address when ADO = 1
#else
	#define MPU9250_ADDRESS 0x68  // Device address when ADO = 0
#endif // AD0

#define AK8963_ADDRESS  0x0C   // Address of magnetometer

#define READ_FLAG 0x80
#define DEG_TO_RAD 0.0174532925
#define RAD_TO_DEG 57.295779513

class MPU9250
{
private:
	uint8_t rx_buffer[15]; // Save the received bytes
	int i2c_descriptor; // I2C file descriptor is saved
	char *i2c_bus = (char*)"/dev/i2c-1"; // Choose what I2C bus you want

	int8_t i2cAddr(int address); // Start a device communication
protected:
	// Set initial input parameters
	enum Ascale
	{
	  AFS_2G = 0,
	  AFS_4G,
	  AFS_8G,
	  AFS_16G
	};

	enum Gscale {
	  GFS_250DPS = 0,
	  GFS_500DPS,
	  GFS_1000DPS,
	  GFS_2000DPS
	};

	enum Mscale {
	  MFS_14BITS = 0, // 0.6 mG per LSB
	  MFS_16BITS      // 0.15 mG per LSB
	};

	enum M_MODE {
	  M_8HZ = 0x02,  // 8 Hz update
	  M_100HZ = 0x06 // 100 Hz continuous magnetometer
	};

	// TODO: Add setter methods for this hard coded stuff
	// Specify sensor full scale
	uint8_t Gscale = GFS_250DPS;
	uint8_t Ascale = AFS_2G;
	// Choose either 14-bit or 16-bit magnetometer resolution
	uint8_t Mscale = MFS_16BITS;

	// 2 for 8 Hz, 6 for 100 Hz continuous magnetometer data read
	uint8_t Mmode = M_8HZ;

	uint8_t writeByte(uint8_t address, uint8_t registerAddress, uint8_t data);
	uint8_t readBytes(uint8_t address, uint8_t registerAddress, uint8_t count,
			uint8_t *dest = NULL);

public:
	double pitch, yaw, roll;
	double temperature;   // Stores the real internal chip temperature in Celcius
	int16_t tempCount;   // Temperature raw count output

	double deltat = 0.0;  // integration interval for both filter schemes

	int16_t gyroCount[3];   // Stores the 16-bit signed gyro sensor output
	int16_t magCount[3];    // Stores the 16-bit signed magnetometer sensor output
	// Scale resolutions per LSB for the sensors
	double aRes, gRes, mRes;
	// Variables to hold latest sensor data values
	double ax, ay, az, gx, gy, gz, mx, my, mz;
	// Factory mag calibration and mag bias
	double factoryMagCalibration[3] = {0, 0, 0}, factoryMagBias[3] = {0, 0, 0};
	// Bias corrections for gyro, accelerometer, and magnetometer
	double gyroBias[3]  = {0, 0, 0},
		  accelBias[3] = {0, 0, 0},
		  magBias[3]   = {0, 0, 0},
		  magScale[3]  = {0, 0, 0};
	double selfTest[6];
	// Stores the 16-bit signed accelerometer sensor output
	int16_t accelCount[3];

	// Public method declarations
	MPU9250();
	void getMres();
	void getGres();
	void getAres();
	void readAccelData(int16_t *);
	void readGyroData(int16_t *);
	void readMagData(int16_t *);
	int16_t readTempData();

	void updateTime();
	void initAK8963(double *);
	void initMPU9250();
	void calibrateMPU9250(double * gyroBias, double * accelBias);
	void MPU9250SelfTest(double * destination);
	void magCalMPU9250(double * dest1, double * dest2);
	uint8_t readByte(uint8_t address, uint8_t regAddress);
};  // class MPU9250

#endif // _MPU9250_H_
