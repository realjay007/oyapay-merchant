from setuptools import find_packages, setup

setup(
	name="oyapay_merchant",
	version="0.1",
	packages=find_packages(),
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		"flask",
		"simplejson",
		"pypika",
		"flask-responses"
	]
)

