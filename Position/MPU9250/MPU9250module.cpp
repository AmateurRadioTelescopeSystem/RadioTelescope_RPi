#include <python3.5m/Python.h>
#include "MPU9250.h"

static PyObject *mpuError; // Define an exception object for the module, it is a good idea to do it in every module
MPU9250 mpu; // Create the mpu object to use in functions

static void initMPU9250(PyObject* self)
{
	mpu.initMPU9250();
}

static PyObject* initAK8963(PyObject* self)
{
	PyObject* fact_values = PyList_New((Py_ssize_t)3);
	mpu.initAK8963(mpu.factoryMagCalibration);

	for(int i = 0; i < 3; i++)
		PyList_Append(fact_values, Py_BuildValue("d", mpu.factoryMagCalibration[i]));

	return fact_values;
}

static PyObject* calibrateMPU9250(PyObject* self)
{
	PyObject* gyroBias = PyList_New((Py_ssize_t)3);
	PyObject* accelBias = PyList_New((Py_ssize_t)3);
	PyObject* biasList = PyList_New((Py_ssize_t)6);
	mpu.calibrateMPU9250(mpu.gyroBias, mpu.accelBias);

	for(int i = 0; i < 3; i++)
	{
		PyList_Append(gyroBias, Py_BuildValue("d", mpu.gyroBias[i]));
		PyList_Append(accelBias, Py_BuildValue("d", mpu.accelBias[i]));
	}
	PyList_Append(biasList, gyroBias);
	PyList_Append(biasList, accelBias);

	return biasList;
}

static PyObject* magCalMPU9250(PyObject* self)
{
	PyObject* magBias = PyList_New((Py_ssize_t)3);
	PyObject* magScale = PyList_New((Py_ssize_t)3);
	PyObject* biasList = PyList_New((Py_ssize_t)6);
	mpu.magCalMPU9250(mpu.magBias, mpu.magScale);

	for(int i = 0; i < 3; i++)
	{
		PyList_Append(magBias, Py_BuildValue("d", mpu.magBias[i]));
		PyList_Append(magScale, Py_BuildValue("d", mpu.magScale[i]));
	}
	PyList_Append(biasList, magBias);
	PyList_Append(biasList, magScale);

	return biasList;
}

static PyObject* MPU9250SelfTest(PyObject* self)
{
	PyObject* test_results = PyList_New((Py_ssize_t)3);
	mpu.initAK8963(mpu.selfTest);

	for(int i = 0; i < 3; i++)
		PyList_Append(test_results, Py_BuildValue("d", mpu.selfTest[i]));

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
		PyList_Append(raw_data, Py_BuildValue("d", mpu.accelCount[i]));

	return raw_data;
}

static PyObject* readAccelData(PyObject* self)
{
	mpu.readAccelData(mpu.accelCount);

	mpu.ax = (float)mpu.accelCount[0] * mpu.aRes;
	mpu.ay = (float)mpu.accelCount[1] * mpu.aRes;
	mpu.az = (float)mpu.accelCount[2] * mpu.aRes;

	return Py_BuildValue("ddd", mpu.accelCount[0], mpu.accelCount[1], mpu.accelCount[2]);
}

static PyObject* readGyroDataRaw(PyObject* self)
{
	PyObject* raw_data = PyList_New((Py_ssize_t)3);
	mpu.readGyroData(mpu.gyroCount);

	for(int i = 0; i < 3; i++)
		PyList_Append(raw_data, Py_BuildValue("d", mpu.gyroCount[i]));

	return raw_data;
}

static PyObject* readGyroData(PyObject* self)
{
	mpu.readGyroData(mpu.gyroCount);

	mpu.ax = (float)mpu.gyroCount[0] * mpu.gRes;
	mpu.ay = (float)mpu.gyroCount[1] * mpu.gRes;
	mpu.az = (float)mpu.gyroCount[2] * mpu.gRes;

	return Py_BuildValue("ddd", mpu.gyroCount[0], mpu.gyroCount[1], mpu.gyroCount[2]);
}

static PyObject* readMagDataRaw(PyObject* self)
{
	PyObject* raw_data = PyList_New((Py_ssize_t)3);
	mpu.readMagData(mpu.magCount);

	for(int i = 0; i < 3; i++)
		PyList_Append(raw_data, Py_BuildValue("d", mpu.magCount[i]));

	return raw_data;
}

static PyObject* readMagData(PyObject* self)
{
	mpu.readMagData(mpu.magCount);

	mpu.ax = (float)mpu.magCount[0] * mpu.mRes;
	mpu.ay = (float)mpu.magCount[1] * mpu.mRes;
	mpu.az = (float)mpu.magCount[2] * mpu.mRes;

	return Py_BuildValue("ddd", mpu.magCount[0], mpu.magCount[1], mpu.magCount[2]);
}

static PyObject* readTempDataRaw(PyObject* self)
{
	int16_t temperature = mpu.readTempData();

	return Py_BuildValue("h", temperature);
}

static PyMethodDef mpu_methods[] =
{
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
PyMODINIT_FUNC PyInit_mpu(void)
{
    return PyModule_Create(&mpu9250Module);
}
