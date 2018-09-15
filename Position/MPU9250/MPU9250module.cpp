#include <Python.h>
#include "MPU9250.h"
#include "../Quaternion/quaternionFilters.h"

// static PyObject *mpuError; // Define an exception object for the module, it is a good idea to do it in every module
MPU9250 mpu; // Create the mpu object to use in functions

static PyObject* initMPU9250(PyObject* self)
{
	mpu.initMPU9250();
	return Py_None;
}

static PyObject* initAK8963(PyObject* self)
{
	PyObject* fact_values = PyList_New((Py_ssize_t)3);
	mpu.initAK8963(mpu.factoryMagCalibration);

	for(int i = 0; i < 3; i++)
		PyList_SetItem(fact_values, (Py_ssize_t)i, Py_BuildValue("d", mpu.factoryMagCalibration[i]));

	return fact_values;
}

static PyObject* calibrateMPU9250(PyObject* self)
{
	PyObject* gyroBias = PyList_New((Py_ssize_t)3);
	PyObject* accelBias = PyList_New((Py_ssize_t)3);
	PyObject* biasList = PyList_New((Py_ssize_t)2);
	mpu.calibrateMPU9250(mpu.gyroBias, mpu.accelBias);

	for(int i = 0; i < 3; i++)
	{
		PyList_SetItem(gyroBias, (Py_ssize_t)i, Py_BuildValue("d", mpu.gyroBias[i]));
		PyList_SetItem(accelBias, (Py_ssize_t)i, Py_BuildValue("d", mpu.accelBias[i]));
	}
	PyList_SetItem(biasList, (Py_ssize_t)0, gyroBias);
	PyList_SetItem(biasList, (Py_ssize_t)1, accelBias);

	return biasList;
}

static PyObject* magCalMPU9250(PyObject* self)
{
	PyObject* magBias = PyList_New((Py_ssize_t)3);
	PyObject* magScale = PyList_New((Py_ssize_t)3);
	PyObject* biasList = PyList_New((Py_ssize_t)2);
	mpu.magCalMPU9250(mpu.magBias, mpu.magScale);

	for(int i = 0; i < 3; i++)
	{
		PyList_SetItem(magBias, (Py_ssize_t)i, Py_BuildValue("d", mpu.magBias[i]));
		PyList_SetItem(magScale, (Py_ssize_t)i, Py_BuildValue("d", mpu.magScale[i]));
	}
	PyList_SetItem(biasList, (Py_ssize_t)0, magBias);
	PyList_SetItem(biasList, (Py_ssize_t)1, magScale);

	return biasList;
}

static PyObject* MPU9250SelfTest(PyObject* self)
{
	PyObject* test_results = PyList_New((Py_ssize_t)6);
	mpu.MPU9250SelfTest(mpu.selfTest);

	for(int i = 0; i < 6; i++)
		PyList_SetItem(test_results, (Py_ssize_t)i, Py_BuildValue("d", mpu.selfTest[i]));

	return test_results;
}

static PyObject* getAres(PyObject* self)
{
	mpu.getAres();

	return Py_BuildValue("d", mpu.aRes);
}

static PyObject* getGres(PyObject* self)
{
	mpu.getGres();

	return Py_BuildValue("d", mpu.gRes);
}

static PyObject* getMres(PyObject* self)
{
	mpu.getMres();

	return Py_BuildValue("d", mpu.mRes);
}


/*
 * Value read section
 */
static PyObject* readAccelDataRaw(PyObject* self)
{
	PyObject* raw_data = PyList_New((Py_ssize_t)3);
	mpu.readAccelData(mpu.accelCount);

	for(int i = 0; i < 3; i++)
		PyList_SetItem(raw_data, (Py_ssize_t)i, Py_BuildValue("d", mpu.accelCount[i]));

	return raw_data;
}

static PyObject* readAccelData(PyObject* self)
{
	mpu.readAccelData(mpu.accelCount);

	mpu.ax = (double)mpu.accelCount[0] * mpu.aRes;
	mpu.ay = (double)mpu.accelCount[1] * mpu.aRes;
	mpu.az = (double)mpu.accelCount[2] * mpu.aRes;

	return Py_BuildValue("ddd", mpu.ax, mpu.ay, mpu.az);
}

static PyObject* readGyroDataRaw(PyObject* self)
{
	PyObject* raw_data = PyList_New((Py_ssize_t)3);
	mpu.readGyroData(mpu.gyroCount);

	for(int i = 0; i < 3; i++)
		PyList_SetItem(raw_data, (Py_ssize_t)i, Py_BuildValue("d", mpu.gyroCount[i]));

	return raw_data;
}

static PyObject* readGyroData(PyObject* self)
{
	mpu.readGyroData(mpu.gyroCount);

	mpu.gx = (double)mpu.gyroCount[0] * mpu.gRes;
	mpu.gy = (double)mpu.gyroCount[1] * mpu.gRes;
	mpu.gz = (double)mpu.gyroCount[2] * mpu.gRes;

	return Py_BuildValue("ddd", mpu.gx, mpu.gy, mpu.gz);
}

static PyObject* readMagDataRaw(PyObject* self)
{
	PyObject* raw_data = PyList_New((Py_ssize_t)3);
	mpu.readMagData(mpu.magCount);

	for(int i = 0; i < 3; i++)
		PyList_SetItem(raw_data, (Py_ssize_t)i, Py_BuildValue("d", mpu.magCount[i]));

	return raw_data;
}

static PyObject* readMagData(PyObject* self)
{
	mpu.readMagData(mpu.magCount);

	mpu.mx = (double)mpu.magCount[0] * mpu.mRes
			* mpu.factoryMagCalibration[0] - mpu.magBias[0];
	mpu.my = (double)mpu.magCount[1] * mpu.mRes
			* mpu.factoryMagCalibration[1] - mpu.magBias[1];
	mpu.mz = (double)mpu.magCount[2] * mpu.mRes
			* mpu.factoryMagCalibration[2] - mpu.magBias[2];

	return Py_BuildValue("ddd", mpu.mx, mpu.my, mpu.mz);
}

static PyObject* readTempDataRaw(PyObject* self)
{
	int16_t temperature = mpu.readTempData();

	return Py_BuildValue("h", temperature);
}

static PyObject* getData(PyObject* self)
{
	double* q_val = NULL;
	if(mpu.readByte(MPU9250_ADDRESS, INT_STATUS) & 0x01)
	{
		mpu.readAccelData(mpu.accelCount);

		mpu.ax = (double)mpu.accelCount[0] * mpu.aRes;
		mpu.ay = (double)mpu.accelCount[1] * mpu.aRes;
		mpu.az = (double)mpu.accelCount[2] * mpu.aRes;

		mpu.readGyroData(mpu.gyroCount);

		mpu.gx = (double)mpu.gyroCount[0] * mpu.gRes;
		mpu.gy = (double)mpu.gyroCount[1] * mpu.gRes;
		mpu.gz = (double)mpu.gyroCount[2] * mpu.gRes;

		mpu.readMagData(mpu.magCount);

		mpu.mx = (double)mpu.magCount[0] * mpu.mRes
						* mpu.factoryMagCalibration[0] - mpu.magBias[0];
		mpu.my = (double)mpu.magCount[1] * mpu.mRes
						* mpu.factoryMagCalibration[1] - mpu.magBias[1];
		mpu.mz = (double)mpu.magCount[2] * mpu.mRes
						* mpu.factoryMagCalibration[2] - mpu.magBias[2];
	}
	mpu.updateTime();
	MahonyQuaternionUpdate(mpu.ax, mpu.ay, mpu.az,
			mpu.gx * DEG_TO_RAD, mpu.gy * DEG_TO_RAD, mpu.gz * DEG_TO_RAD,
			mpu.my, mpu.mx, mpu.mz, mpu.deltat);
	q_val = getQ();


	mpu.yaw   = atan2(2.0 * (q_val[1] * q_val[2] + q_val[0] * q_val[3]),
					q_val[0] * q_val[0] + q_val[1]
						* q_val[1] - q_val[2] * q_val[2] - q_val[3] * q_val[3]) * RAD_TO_DEG;
	mpu.pitch = -asin(2.0 * (q_val[1] * q_val[3] - q_val[0] * q_val[2])) * RAD_TO_DEG;
	mpu.roll  = atan2(2.0 * (q_val[0] * q_val[1] + q_val[2] * q_val[3]),
					q_val[0] * q_val[0] - q_val[1]
						* q_val[1] - q_val[2] * q_val[2] + q_val[3] * q_val[3]) * RAD_TO_DEG;

	return Py_BuildValue("ddd", mpu.yaw, mpu.pitch, mpu.roll);
}

static PyMethodDef mpu_methods[] =
{
	// TODO: Add comments below
	// "PythonName" C-function Name, argument presentation, description
	{"initMPU9250", (PyCFunction)initMPU9250, METH_NOARGS, ""},
	{"initAK8963", (PyCFunction)initAK8963, METH_NOARGS, ""},
	{"calibrateMPU9250", (PyCFunction)calibrateMPU9250, METH_NOARGS, ""},
	{"magCalMPU9250", (PyCFunction)magCalMPU9250, METH_NOARGS, ""},
	{"MPU9250SelfTest", (PyCFunction)MPU9250SelfTest, METH_NOARGS, ""},
	{"getAres", (PyCFunction)getAres, METH_NOARGS, ""},
	{"getGres", (PyCFunction)getGres, METH_NOARGS, ""},
	{"getMres", (PyCFunction)getMres, METH_NOARGS, ""},
	{"readAccelDataRaw", (PyCFunction)readAccelDataRaw, METH_NOARGS, ""},
	{"readAccelData", (PyCFunction)readAccelData, METH_NOARGS, ""},
	{"readGyroDataRaw", (PyCFunction)readGyroDataRaw, METH_NOARGS, ""},
	{"readGyroData", (PyCFunction)readGyroData, METH_NOARGS, ""},
	{"readMagDataRaw", (PyCFunction)readMagDataRaw, METH_NOARGS, ""},
	{"readMagData", (PyCFunction)readMagData, METH_NOARGS, ""},
	{"readTempDataRaw", (PyCFunction)readTempDataRaw, METH_NOARGS, ""},
	{"getData", (PyCFunction)getData, METH_NOARGS, ""},
	{NULL, NULL, 0, NULL} //Sentinel, tell the API that we finished defining table
};

static struct PyModuleDef mpu9250Module =
{
	PyModuleDef_HEAD_INIT,
	"mpu9250",
	"A wrapper for MPU9250 9-axis sensor",
	-1,
	mpu_methods
};


// Initialization used when compiling and using this code
// A reference is created
PyMODINIT_FUNC PyInit_mpu9250(void)
{
	return PyModule_Create(&mpu9250Module);
}
