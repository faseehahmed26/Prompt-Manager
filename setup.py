from setuptools import setup, find_packages

setup(
    name="prompt_manager",
    version="0.1.0",
    description="A simple library for managing versioned prompts.",
    author="Faseeh Ahmed Mohammad",
    author_email="faseehahmed2606@gmail.com",
    packages=find_packages(),
    install_requires=[
        "watchdog",  
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
