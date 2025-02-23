from setuptools import setup, find_packages

setup(
    name="tradwar4py",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'PyQt5',
    ],
    entry_points={
        'console_scripts': [
            'tradwar=tradwar4py.run:main',
        ],
    },
)
