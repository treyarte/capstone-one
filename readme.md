# <b>My Drop List</b>

https://mydroplist.herokuapp.com/

A web application that can help facilitate better communication between stockers and forklift drivers and provide record-keeping for users. See your forklift drivers' performance by creating graphs of the droplists they have completed, accepted, and declined.

### Background Information

"It wasn't on the list" is a common phrase I hear at my warehouse. Every day a droplist (a collection of items and their locations that will be stocked) is created on paper by a stocker and handed off to a forklift driver. Because the droplist is on paper, many problems occur, which causes conflict and misunderstandings.

Losing the droplist, retrieving the wrong items, and not knowing the status of the droplist are some of the problems that occur. My Droplist was built to elevate these problems while providing statistical information about employees' performance.

### Features

- The status of each droplist updates based on what action the receiving forklift driver takes.

- Graphs of completed, accepted, and declined droplist.

- Users can swap roles.

### User Flow

Users can sign up as either stocker or forklift driver. A stocker can create a droplist and send it to a forklift driver, and forklift drivers can accept, decline, and complete a droplist.

### API

##### [QuickChart](https://quickchart.io/)

### Tools

- Python
- Flask
- WTForms
- SQLAlchemy
- Jinja2
- JavaScript
- Axios
- Bootstrap 4
- HTML/CSS

### Requirements

- PostgreSQL 12.2
- Python 3.8.2 or Later

### Installation

#### Setup

Create and activate a virtual environment.

```sh
python -m venv venv
```

```sh
source venv/Scripts/activate
```

##### Upgrade pip

```sh
(venv) $ pip install --upgrade pip
```

##### Installing dependencies

```sh
(venv) $ pip install -r requirements.txt
```

#### Create the Databases

You will need to create two databases in PostgreSQL. One for the application and another for testing.

##### App Database

```sh
(venv) $ createdb mydroplist
(venv) $ python seed.py
```

##### Test Database

```sh
(venv) $ createdb mydroplist-test
```

#### Run Application

```sh
flask run
```

localhost:5000 or http://127.0.0.1:5000/ is the default location the application will run on.

#### Running Tests

```sh
FLASK_ENV=production python -m unittest <name-of-python-file>
```
