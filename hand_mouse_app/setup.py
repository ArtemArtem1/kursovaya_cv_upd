from setuptools import find_packages, setup

setup(
    name="virtual-hand-mouse",
    version="1.0.0",
    description="Virtual mouse controlled by hand gestures",
    author="Student",
    packages=find_packages(),
    py_modules=["main"],
    python_requires=">=3.10,<3.11",
    install_requires=[
        "PySide6",
        "pyautogui",
        "mediapipe==0.10.14",
        "numpy==1.26.4",
        "opencv-contrib-python==4.10.0.84",
    ],
)