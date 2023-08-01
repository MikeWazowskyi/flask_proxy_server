# flask_proxy_server
[![python-app workflow](https://github.com/MikeWazowskyi/flask_proxy_server/actions/workflows/python-app.yml/badge.svg)](https://github.com/MikeWazowskyi/flask_proxy_server/actions/workflows/python-app.yml)
## Description

#### Implementation of a simple HTTP proxy server that runs locally and displays the content of Hacker News pages. The proxy modifies the text on the pages as follows: after every six-letter word, there is a trademark symbol "™".

## Instructions for running

1. Clone the repository and navigate to it in the command line::

    ``` git clone https://github.com/MikeWazowskyi/flask_proxy_server```

    ``` cd flask_proxy_server```

2. Create and activate a virtual environment:

    ```python -m venv venv```

    ```source vens/Scripts/activate```

3. Install requirements:

    ``` python -m pip install --upgrade pip```

    ``` python -m pip install -r requirements.txt```

4. Run:

    ``` flask run```
