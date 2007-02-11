from setuptools import setup, find_packages
import sys, os

version = '1.0a3'

setup(name='plone.app.contentrules',
      version=version,
      description="Plone integration for plone.contentrules",
      long_description="""\
plone.app.contentrules provides Plone-specific conditions and actions, as well
as a user interface for plone.contentrules.
""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Markus Fuhrer and Martin Aspeli',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://svn.plone.org/svn/plone/plone.app.contentrules',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'plone.contentrules>=' + version, # sync versions
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
