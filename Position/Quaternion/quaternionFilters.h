#ifndef _QUATERNIONFILTERS_H_
#define _QUATERNIONFILTERS_H_

#define PI 3.14159265 // Define the pi constant

#include <math.h> // Needed for the sqrt function

extern void MadgwickQuaternionUpdate(double ax, double ay, double az, double gx, double gy,
                                     double gz, double mx, double my, double mz,
                                     double deltat);
extern void MahonyQuaternionUpdate(double ax, double ay, double az, double gx, double gy,
                                   double gz, double mx, double my, double mz,
                                   double deltat);
extern double * getQ(void);

#endif // _QUATERNIONFILTERS_H_
