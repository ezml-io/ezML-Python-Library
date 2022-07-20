from setuptools import setup


setup(
    name='ezml',
    version='0.1.0',    
    description='Ezml client library',
    author='Dennis Zax',
    packages=['ezml'],
    install_requires=['numpy', 'pillow' , 'filetype', 'opencv-python', 'requests'],
)