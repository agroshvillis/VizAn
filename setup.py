from io import open

from setuptools import find_packages, setup

with open('vizan/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.strip().split('=')[1].strip(' \'"')
            break
    else:
        version = '0.1.0'

with open('README.rst', 'r', encoding='utf-8') as f:
    readme = f.read()

required = [
    'pysvg-py3>=0.2.2.post2',
    'cobra>=0.14.2'
]

setup(
    name='vizan',
    version=version,
    author='Agris Pentjuss',
    author_email='agrosh@inbox.lv',
    maintainer='Rudolfs Petrovs',
    maintainer_email='rudolfs.petrovs@lu.lv',
    description='',
    long_description=readme,
    long_description_content_type="text/x-rst",
    url='https://github.com/lv-csbg/vizan',
    license='GPLv3',

    keywords=[
        '',
    ],

    classifiers=[
        'Development Status :: 3 - Alpha'
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'License :: FSF Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],

    install_requires=required,
    tests_require=['coverage', 'pytest'],

    packages=find_packages(),
)
