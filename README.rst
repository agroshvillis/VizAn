VizAn
=====


.. contents:: **Table of Contents**
    :backlinks: none

Installation
------------

VizAn is distributed on `PyPI <https://pypi.org>`_ as a universal
wheel and is available on Linux/macOS and Windows and supports
Python 2.7/3.5+ and PyPy.

.. code-block:: bash

    $ pip install VizAn

Old installation guide
______________________

VizAn is Python based package with additional dependencies:

To install dependencies for Your OS You need to install:
    1) Python programming language:

        a) 2.x version from : https://www.python.org/downloads/release/python-2715/

        b) 3.x version from : https://www.python.org/downloads/release/python-371/

    follow installation steps and tips from python.org links


    2) To install additional dependencies PIP or PIP3 is necessary and should be installed with Python package:



    3) To use CobraPy toolbox needs to be installed using PIP OS based version:

        https://opencobra.github.io/cobrapy/


    4) PySVG package is necessary to read and write and modify SVG file:

        a) for python 3.x :

            pip install pysvg-py3


       b) for python 2.x

            pip install pysvg

    5) to install jupyter notebook :

        http://jupyter.org/install

    6) copy VizAn directory to any project location and add it to sys.path

        import sys
        sys.path.append('path_to_VizAn')


_______________________________________________________________________________________________________________________________________________________________________________________________________________________________________

   RUN Vizan !!!


   To execute the VizAn standalone script You need to :

    import Vizan_1_0_0 as Vizan
    Vizan.Call_Vizan(model,file_source_path,sol,SolutionType,prod,subst,count)

    where

Main function to call VizAn:


 Call_Vizan(model,file_source_path,sol,SolutionType,prod,subst,count)


 A) model - metabolic model of organism

 B) file_source_path - using tkinker open window choose metabolic network layout file in SVG format developed according to the manual

 C) SolutionAnalysis - Flux Balance Analysis (FBA) or Flux Variability Analysis (FVA) optimisation results

 D) SolutionType - optional input where "FBA": FBA type visualization "FVA" : FVA type visualization

 E) prod - the analysis product name(s)

 F) subst - the analysis substrate name(s)

 H) count - arbitrary parameter for condition specific classification (any symbol or string)


Azure notebook link
___________________

https://notebooks.azure.com/agrosh/libraries/VizAn



License
-------

VizAn is distributed under the terms of `GPL v3 License <https://choosealicense.com/licenses/gpl-3.0/>`_

