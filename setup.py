from setuptools import setup, find_packages

setup(
    name="decentralized-federated-learning",
    version="0.1.0",
    description="Advanced decentralized federated learning framework",
    author="Sumit Chongder",
    packages=find_packages(),
    install_requires=[
        "torch>=2.0",
        "torchvision>=0.15",
        "fastapi",
        "uvicorn",
        "pydantic>=2.0",
        "requests",
        "web3>=6.0",
        "ipfshttpclient>=0.8",
        "cryptography",
        "numpy",
        "pandas",
        "protobuf",
        "scikit-learn",
        "matplotlib",
        "libp2p==0.1.7",
    ],
    python_requires=">=3.10",
)
