VizAn
=====
VizAn is a metabolic flux visualisation tool written in Python. It can be used
for flux balance analysis (FBA) and flux variability analysis (FVA).

.. contents:: **Table of Contents**
    :backlinks: none

Installation
------------

VizAn is distributed on `PyPI <https://pypi.org>`_ as a universal
wheel and is available on Linux/macOS and Windows and supports
Python 2.7/3.5+ and PyPy.

.. code-block:: bash

    $ pip install VizAn

Usage
-------------

.. code-block:: python

    import vizan
    model_filename = 'data/iML1515.json'
    svg_filename = 'data/E_coli_source.svg'
    output_filename = 'FBA_result.svg'
    vizan.visualise(model_filename, svg_filename, output_filename, analysis_type='FBA')

Explanation of parameters:
__________________________

visualise(model_filename, svg_filename, output_filename, analysis_type='FBA', analysis_results=None)
    :model_filename: a filename string of metabolic model of an organism saved as JSON
    :svg_filename: a filename string of SVG pathway map, which is made according to instructions in MANUAL.rst
    :output_filename: a filename string for output SVG file with the visualisation
    :analysis_type: "FBA" or "FVA" string, to specify the type of visualisation
    :analysis_results: optional FBA or FVA results to be given (otherwise they are calculated using defaults)
    :return: None

Manual for creating SVG biochemical pathway maps
------------------------------------------------

See the manual `here <docs/MANUAL.rst>`__

Development
-----------

To install the development version from Github:

.. code-block:: bash

    git clone https://github.com/lv-csbg/VizAn.git
    cd VizAn
    pip install .

License
-------

VizAn is distributed under the terms of `GPL v3 License <https://choosealicense.com/licenses/gpl-3.0/>`_

