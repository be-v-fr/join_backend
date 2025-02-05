*Are you looking for the Join frontend repo? Look no further:* https://github.com/be-v-fr/join_frontend

Join backend is a Django backend providing a Kanban board for all users in the database. All tasks are
seen by everyone. Moreover, users can assign tasks to each other and view each other as contacts,
while their email adresses remain hidden.

(c) 2025 Bengt Früchtenicht

General Functionality:
======================

Users can register as business users or customers.
Business users can create offers and update the offer state.
Customers can create offer orders and customer reviews for the related business.

Local setup:
============

- Install the Python dependencies listed in `requirements.txt`.
- Run `python manage.py makemigrations` in the shell
- Run `python manage.py migrate`

Local hosting:
==============

To use your own device as server:
- Run `python manage.py runserver`

You can use both `http://localhost:8000/` and `http://127.0.0.1:8000/` as base URLs.

The `admin/` sub-URL features the default Django database interface. To login, you need
to create an admin account:
- Run `python manage.py createsuperuser`

The `api/` sub-URL features the API URLs as listed in the `./join_backend/urls.py` file.

Documentation:
==============

To access the documentation, locally host `./docs/_build/html/index.html`.

Data structure:
===============

The data structure for each API endpoint can vary depending on the request method.

To get a first impression regarding GET requests, you can use the Django REST Framework interface
mentioned above.

To gain an insight into the data structure required for writing, study
- The tests for the respective POST and PATCH requests towards the endpoint in interest.
- The serializers in the respective `serializers.py` file or `serializers` folder.
- The documentation.