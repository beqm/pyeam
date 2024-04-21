from setuptools import find_packages, setup


setup(
    name="pyeam",
    version="1.0.0",
    description="A system that allows building of desktop applications using python and webview",
    package_dir={"pyeam": "pyeam"},
    packages=find_packages(),
    url="https://github.com/beqm/pyeam",
    author="beqm",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    install_requires=["psutil>=5.9.8", "requests>=2.31.0", "pywebview>=5.1"],
    python_requires=">=3.12",
)