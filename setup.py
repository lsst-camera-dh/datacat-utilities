from setuptools import setup, find_packages

setup(
    name='lsst_camera_datacat_utils',
    version='0.1.0',
    packages=find_packages(exclude=('tests', 'docs')),
    license='SLAC license',
    description='datacat utils',
    long_description='LSST camera data catalog utilities',
    install_requires=[
        "python >= 2.7.10",
    ],
)
