from setuptools import setup, find_packages
import os.path

version = '1.1.6'

setup(name='plone.app.contentrules',
      version=version,
      description="Plone integration for plone.contentrules",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Markus Fuhrer and Martin Aspeli',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://svn.plone.org/svn/plone/plone.app.contentrules',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages = ['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'plone.contentrules',
      ],
      )
