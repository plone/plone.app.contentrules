from pathlib import Path
from setuptools import setup


version = "6.0.0a1"

long_description = (
    f"{Path('README.rst').read_text()}\n{Path('CHANGES.rst').read_text()}"
)

setup(
    name="plone.app.contentrules",
    version=version,
    description="Plone integration for plone.contentrules",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    # Get more strings from
    # https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 6.2",
        "Framework :: Plone :: Core",
        "Framework :: Zope :: 5",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="plone automatic content rules",
    author="Plone Foundation",
    author_email="plone-developers@lists.sourceforge.net",
    url="https://pypi.org/project/plone.app.contentrules",
    license="GPL version 2",
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.10",
    extras_require={
        "test": [
            "plone.app.testing",
            "plone.app.contenttypes[test]",
            "plone.dexterity",
            "plone.testing",
        ]
    },
    install_requires=[
        "lxml",
        "plone.app.contenttypes",
        "plone.app.uuid",
        "plone.app.vocabularies",
        "plone.autoform",
        "plone.base",
        "plone.contentrules",
        "plone.memoize",
        "plone.stringinterp",
        "plone.supermodel",
        "plone.uuid",
        "Products.PluggableAuthService",
        "Products.GenericSetup",
        "Products.MailHost",
        "Products.statusmessages",
        "z3c.form",
        "Zope",
    ],
)
