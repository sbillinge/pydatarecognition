.. role:: bash(code)
   :language: bash
.. role:: python(code)
   :language: python

.. raw:: html

    <link href="_static/unicodetiles.css" rel="stylesheet" type="text/css" />
    <script src="_static/unicodetiles.min.js"></script>
    <script src="_static/rg-dungeon.js"></script>
    <div style="text-align:center;">
        <div id="game"><h1>welcome to the pydatarecognition docs</h1></div>
    </div>
    <script type="text/javascript">initRgDungeon();</script>

Pydatarecognition
========
Pydatarecognition is a structure data content management system for published scientific papers.
Pydatarecognition stores data and metadata relevant for describing the
science in scientific publications and allows it to serialized into structured
databases which may then be mined for better scientific understanding

Pydatarecognition is developed in the `Billinge group <https://billingegroup.github.io/>`_


Installation
============

Pydatarecognition packages are available from conda-forge and PyPI:

**conda:**

.. code-block:: sh

    $ conda install -c conda-forge Pydatarecognition

**pip:**

.. code-block:: sh

    $ pip install Pydatarecognition

The Pydatarecognition code is migrating quickly these days.  If you prefer you can 
install from the GitHub repository mode and get the latest changes.
In that case, clone the `GitHub repository  <https://github.com/billingegroup/pydatarecognition>`_,
change directory to the top level directory in that cloned repository where the
:bash:`setup.py` file is.  From inside your virtual environment, type

.. code-block:: sh

    $ python setup.py install
    $ conda install -c conda-forge -c diffpy --file requirements/run.txt

which installs Pydatarecognition, and all its dependencies, in this environment in develop mode.  In this mode, the
version of Pydatarecognition you run will change each time you update from the repo 
leading to instability so be careful.

To check that your installation type

.. code-block:: sh

    $ pydatarecognition

or the abbreviated

.. code-block:: sh

    $ pydr

and it should run without error

Quick Start
============


Tutorials
=========
.. toctree::
    :maxdepth: 1

    broker

