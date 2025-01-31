import pathlib
from setuptools import find_packages, setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="realnet",
    version="0.0.114",
    description="Realnet command line interface",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/virtual-space/realnet",
    author="Marko Laban",
    author_email="marko.laban@l33tsystems.com",
    license="BSD",
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    package_data={  'realnet.static.initialization': ['*'],
                    'realnet.templates': ['*'],
                    'realnet.runner.http.static': ['scripts/ace/*', 'font-awesome/css/*', 'font-awesome/fonts/*']},
    install_requires=["python-dotenv",
                      "urllib3",
                      "boto3",
                      "Flask",
                      "SQLAlchemy==2.0.29",
                      "psycopg2-binary==2.9.9",
                      "sqlalchemy-serializer",
                      "shapely",
                      "GeoAlchemy2",
                      "Werkzeug",
                      "authlib",
                      "flask-cors",
                      "bootstrap-flask",
                      "requests",
                      "pygltflib",
                      "trimesh",
                      "scipy",
                      "Pillow",
                      "pillow-heif",
                      "gunicorn"],
    entry_points={
        "console_scripts": [
            "realnet=realnet.__main__:main",
        ]
    },
)
