from setuptools import setup, find_packages

setup(
    name="droneblock",
    version="1.0.0",
    author="Hemhalatha V R",
    description="A professional, event-driven drone control framework.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/droneblock", 
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        "pymavlink>=2.4.41",
    ],
)
