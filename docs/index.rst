``azure.ml``
============

*Accelerate the machine learning lifecycle.*

Overview
--------

The ``azure.ml`` package provides user-friendly developer tools for Azure Machine Learning.

It is available via the typical installation tools for each interface, e.g. via `pip` for Python. 

Goals
-----

- consistent job and endpoint stories
- all resources are serializable in a human-readable format
- reduce to fundamental concepts
- jobs are composable

ARM Support
-----------

- improved API surface area and clean APIs for ISVs and language SDKs to be built on top of
- ARM for key uses cases (job/endpoint creation), including batch scoring endpoints
- consistent asset management experience (all assets registered via ARM, enforces consistent behavior, etc.)
- per-resource/per-asset/per-action RBAC and policy support
- x-workspace discovery, consumption, and sharing (CI/CD) of assets and resources with proper git-flow support

.. toctree::
   :hidden:
   :caption: User Guide

   overview/installation.rst
   overview/setup.rst
   quickstart/jobs.rst
   quickstart/endpoints.rst
   overview/concepts.rst

.. toctree::
  :hidden:
  :caption: Reference
  
   interfaces/cli.rst
   interfaces/python.rst
  reference/feedback.rst
  reference/qna.rst
  reference/troubleshooting.rst
