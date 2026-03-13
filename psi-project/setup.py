from setuptools import setup, find_packages

setup(
    name="psi-project",
    version="1.0.0",
    description="Private Set Intersection (PSI) Implementation",
    author="Student",
    packages=find_packages(),
    install_requires=[
        "cryptography>=41.0.7",
        "ecdsa>=0.18.0",
        "numpy>=1.26.3",
        "scipy>=1.11.4",
        "pandas>=2.1.3",
        "requests>=2.31.0",
        "pydantic>=2.5.2",
        "matplotlib>=3.8.2",
        "seaborn>=0.13.0",
        "click>=8.1.7",
        "tqdm>=4.66.1",
        "colorama>=0.4.6",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
