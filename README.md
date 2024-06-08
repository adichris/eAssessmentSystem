# Electronic Continuous Assessment System (STU Final Project)

This project is an Electronic Continuous Assessment System, designed to streamline the assessment process in educational institutions. It was developed as a final year project for the STU program.

## Features

- User Authentication and Authorization with Django Allauth
- Robust Database Management with PostgreSQL
- Dynamic Content Management using Wagtail CMS and tinymce editor
- Responsive Front-End Development with HTML, CSS, Bootstrap, Tailwind CSS, HTMX, and JavaScript frameworks
- RESTful API Integration

## Installation

To install the Electronic Continuous Assessment System, you'll need to have Python installed on your system. Then, you can install the required dependencies with the following command:

```bash
pip install -r requirements.txt
```

The `requirements.txt` file should include all the necessary packages, such as:

```
autopep8==1.4.4
Babel==2.9.1
bleach==3.1.0
...
```

## Setup

Configure your project by setting up the database and creating the necessary migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Running the Application

Launch the application using the Django built-in server:

```bash
python manage.py runserver
```

## Django Installed Apps

The project includes several Django apps which are listed in the `settings.py` file under `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    ...
    'phonenumber_field',
    'accounts',
    ...
]
```

## Contributing

Contributions are welcome. Please follow the project's guidelines for contributing.

## License
