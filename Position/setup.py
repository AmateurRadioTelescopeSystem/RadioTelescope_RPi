from distutils.core import setup, Extension

quaternion_module = Extension('quaternion',
                              sources=['Quaternion/quaternionModule.cpp', 'Quaternion/quaternionFilters.cpp'],
                              extra_compile_args=['-std=c++11'])
mpu_module = Extension('mpu9250', sources=['MPU9250/MPU9250module.cpp', 'MPU9250/MPU9250.cpp', 'Quaternion/quaternionFilters.cpp'],
                       extra_compile_args=['-std=c++11'])

setup(name='Quaternion',
      version='1.0',
      description='A package for the quaternion module',
      ext_modules=[quaternion_module])

setup(name='MPU9250',
      version='1.0',
      description='A package for the MPU9250 interface',
      ext_modules=[mpu_module])
