from setuptools import setup, find_packages

with open("README.md", 'r') as fr:
	description = fr.read()

setup(
    name='HMDBScraping',
    version='1.0.0',
    url='https://github.com/jeffrichardchemistry/hmdbwebscraping',
    license='GNU General Public License v2.0',
    author='Jefferson Richard',
    author_email='jrichardquimica@gmail.com',
    keywords='HMDB Webscraping Chemistry NMR',
    description='Python script to scraping NMR and other information from HMDB.',
    long_description = description,
    long_description_content_type = "text/markdown",
    packages=['HMDBScraping'],
    install_requires=['pandas<=2.0.3', 'numpy<=1.24.4', 'bs4', 'selenium', 'requests'],
	classifiers = [
		'Intended Audience :: Developers',
		'Intended Audience :: End Users/Desktop',
		'Intended Audience :: Science/Research',
		'License :: OSI Approved :: BSD License',
		'Natural Language :: English',
		'Operating System :: Unix',
		'Operating System :: Microsoft :: Windows',
		'Operating System :: MacOS',
		'Topic :: Scientific/Engineering :: Artificial Intelligence',
		'Programming Language :: Python',
		'Programming Language :: Python :: 3.8']
)
