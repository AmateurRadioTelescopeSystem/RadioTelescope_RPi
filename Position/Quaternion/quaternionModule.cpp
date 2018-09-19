#include <python3.5/Python.h>
#include "quaternionFilters.h"

/* The quaternion code wa taken from an Arduino library made by SparkFun
 * The whole library can be found here: https://github.com/sparkfun/SparkFun_MPU-9250-DMP_Arduino_Library
 * Some changes where mad to the original code.
 * This code was chosen because the tests that were made, shown a good stability and accuracy of location calculation
**/

static PyObject *quatmodError; // Define an exception object for thr module, it is a good idea to do it in every module

static PyObject* quaternion_mahonyQuaternion(PyObject* self, PyObject *args) //args is represented as a tuple in python
{
    double ax, ay, az, gx, gy, gz, mx, my, mz, deltat;
    double *quaterValues;
    
    // We expect at least one string argument to this function
    if(!PyArg_ParseTuple(args, "dddddddddd", &ax, &ay, &az, &gx, &gy, &gz, &mx, &my, &mz, &deltat))
    {
        PyErr_SetString(quatmodError, "Not enough or wrong arguments provided");
        return NULL; //If nothing is found return an error
    }
    else
    {
        MahonyQuaternionUpdate(ax, ay, az, gx, gy, gz, mx, my, mz, deltat); // Do the necessary calculations
        quaterValues = getQ(); // Get the calculated values for the quaternion
    }
    
    // Build the value and them send it
    return Py_BuildValue("dddd", quaterValues[0], quaterValues[1], quaterValues[2], quaterValues[3]);
}

static PyObject* quaternion_madgwickQuaternion(PyObject* self, PyObject* args)
{
    double ax, ay, az, gx, gy, gz, mx, my, mz, deltat;
    const double *quaterValues = NULL;
    
    // We expect at least one string argument to this function
    if(!PyArg_ParseTuple(args, "dddddddddd", &ax, &ay, &az, &gx, &gy, &gz, &mx, &my, &mz, &deltat))
    {
        PyErr_SetString(quatmodError, "Not enough or wrong arguments provided");
        return NULL; //If nothing is found return an error
    }
    else
    {
        MadgwickQuaternionUpdate(ax, ay, az, gx, gy, gz, mx, my, mz, deltat);
        quaterValues = getQ();
    }
    
    // Build the value and them send it
    return Py_BuildValue("dddd", quaterValues[0], quaterValues[1], quaterValues[2], quaterValues[3]);
}

static PyMethodDef quaternion_methods[] = 
{
    // "PythonName" C-function Name, argument presentation, description
    //METH_VARARGS is always there
    {"mahonyQuaternion", quaternion_mahonyQuaternion, METH_VARARGS, "Calculate the quternion using Mahony's method"},
    {"madgwickQuaternion", quaternion_madgwickQuaternion, METH_VARARGS, "Calculate the quternion using Madgwick's method"},
    {NULL, NULL, 0, NULL} //Sentinel, tell the API that we finished defining table
};

static struct PyModuleDef quatModule =
{
    PyModuleDef_HEAD_INIT,
    "quaternion",
    "A wrapper for quaternion calculation",
    -1,
    quaternion_methods
};


// Initialization used when compiling and using this code
// A reference is created
PyMODINIT_FUNC PyInit_quaternion(void)
{
    return PyModule_Create(&quatModule);
}
