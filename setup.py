import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name='purepyodbc',
    version='1.0.0',  # TODO: Versioning? How?
    packages=['purepyodbc'],
    description='A pure Python ODBC package',
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/chrisimcevoy/purepyodbc',
    license='MIT',
    author='Chris McEvoy',
    author_email='chris@chrismcevoy.net',
)
