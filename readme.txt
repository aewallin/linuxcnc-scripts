These scripts produce G-code to stdout. They can be run from within LinuxCNC/AXIS (see http://www.linuxcnc.org).

The scripts demonstrate various CAM-algorithms from truetypetracer, opencamlib, and openvoronoi.

OpenCAMLib, OpenVoronoi, and truetyeptracer can be built & installed from source (see https://github.com/aewallin)

Or, on Ubuntu, installed from a PPA:
https://launchpad.net/~anders-e-e-wallin/+archive/cam

To get the packages from the PPA:
$ sudo add-apt-repository ppa:anders-e-e-wallin/cam
$ sudo apt-get update
$ sudo apt-get install opencamlib openvoronoi truetypetracer
