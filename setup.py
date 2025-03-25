from setuptools import setup, find_packages

setup(
    name="telegram-quotation-bot",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "python-telegram-bot>=20.6",
        "python-dotenv>=1.0.0",
        "jinja2>=3.1.2",
        "weasyprint>=60.1;platform_system!='Windows'",
        "pdfkit>=1.0.0",
        "pywin32>=306;platform_system=='Windows'",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A Telegram bot for generating professional quotations",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/telegram-quotation-bot",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
) 