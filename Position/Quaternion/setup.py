from distutils.core import setup, Extension

module = Extension('quaternion', sources=['quaternionModule.cpp', 'quaternionFilters.cpp'])

setup(name='Quaternion',
      version='1.0',
      description='A package for the quaternion module',
      ext_modules=[module])
