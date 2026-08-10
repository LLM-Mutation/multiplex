Adding a Mutant Generation Approach
===================================

To add a mutant generation approach to *multiplex*, users should create a package for their approach in the ``multiplex/approach/`` directory.

Users can copy the ``basic`` example to get started and then build their own approach using the underlying setup.

Each approach has a ``controller.py`` file that is called by ``multiplex/__main__.py``.
Currently users must add their approach call to ``__main__.py`` following the template of the existing approaches. 


