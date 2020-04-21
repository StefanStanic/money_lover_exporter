from setuptools import setup

with open("README", 'r') as f:
    long_description = f.read()

setup(
   name='money lover backup',
   version='1.0',
   description='Exports and backups all the data from budgeting app "Money Lover"',
   author='Stefan Stanić',
   author_email='vts.stefan.stanic@gmail.com',
   packages=['money lover backup'],
   install_requires=['requests'],
)