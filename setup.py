
from setuptools import setup

setup(
    name='Codez-Agent',  # Prova a usare un nome unico come questo
    version='0.1.1',
    description='Un assistente AI per il terminale con accesso ai comandi',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Mattia Ristori',
    url='https://github.com/tuonome/codez', # Puoi mettere un link a caso per ora
    py_modules=['codez'],
    install_requires=[
        'requests',
        'rich',
    ],
    entry_points={
        'console_scripts': [
            'codez_agent=codez:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
