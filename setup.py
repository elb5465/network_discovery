#Taken from https://www.youtube.com/watch?v=nlRZdysaAiI @6:55
from setuptools import setup

#name is arbitrary: can be anything - just whatever you want to type to call the function from cmd line.
setup(
    name='network_discovery',
    version='0.0.7',
    url='http://github.com/elb5465/network_discovery',
    license='MIT',
    author='Eric Baker',
    author_email='elb5465@gmail.com',
    description='Scan the user\'s network to retrieve all connected devices IP/MAC addresses, FQDNs, and vendor names. This information is then sorted and exported to a JSON file in the directory that this is run in.',
    py_modules=['network_discovery', 'cli'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'docopt >= 0.6.0',
        'mac-vendor-lookup >= 0.1.11'],
    entry_points="""
        [console_scripts]
        network_discovery = cli:main
        """
)
