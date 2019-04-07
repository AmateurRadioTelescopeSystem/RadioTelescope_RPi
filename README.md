# RadioTelescope RPi

## What is this repository for?

In this repository you will find the necessary files to get the telescope controller software up and running on your raspberry pi.  
This is still a beta version and it is relatively unstable, but usable.

## How do I get set up?

* Before proceeding, make sure that `pip` is installed on your system.
* _Installation command for pip_: `$ sudo apt-get install python3-pip`
* Also you will need to run the command `$ sudo apt-get install qt5-default python3-pyqt5`, to make sure you have the required Qt5
commands.
* In the setup process the important part is to install the required package/packages
* Run `$ sudo python3 -m pip install -r requirements` to install the necessary python packages
* After the installation of packages, you can run the main program from the `run.sh` script.
* _Running command_: `$ ./run.sh`. Make sure the run script has executable permissions.
* If executable permissions are needed for the run script type `$ chmod +x run.sh`, and the run the script as described above.

## Versioning
The versioning system that will be followed in this repo is the [SemVer](https://semver.org/).

## Documentation
This project contains an auto generated code documentation using sphinx and the page is hosted on gitlab.  
[Here](https://artsystem.gitlab.io/controller/rpi-software/) you can find the documentation page.

## Authors
* **Dimitrios Stoupis** - *Initial work* - [GitHub](https://github.com/dimst23/), [GitLab](https://gitlab.com/dimst23)  

All contributors in this project are listed [here](https://gitlab.com/ARtSystem/controller/rpi-software/graphs/master)

## License
This project is licensed under GNU GPLv3. Checkout the [LICENSE](https://gitlab.com/ARtSystem/controller/rpi-software/blob/master/LICENSE) file for details.

## Questions?

* You can contact the repo owner
