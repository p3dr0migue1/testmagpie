# search_console
Search Console API - Data collection and warehousing

### Master status 
[![Build Status](http://194.168.11.234:9090/job/testExample/badge/icon)](http://194.168.11.234:9090/job/testExample)

## Usage

**Install Requirements**
```bash
# local environment
pip install -r requirements/dev.txt
```

```bash
# production environment
pip install -r requirements/prod.txt
```

**Set environment variables**

Set the environment variable `SC_DIR` on your `.bashrc` file with a path of your choice

**Create a credentials folder structure**

Create a new folder to store user credentials, in the same path as the environment variable `SC_DIR`.
*(Keep these folders outside Git)*

**Download client_screts json file**

Go to to the [Google Developer Console](https://console.developers.google.com/apis/credentials?project=search-console-api-access) login with queryclick.analytics@gmail.com, download (and rename the file to `client_screts.json`) the file next to Native App under **OAuth 2.0 Client IDS**. Place the `client_screts.json` file under the credentials directory. The password is available from the KeePass database.

**Running the script**

`python app.py metricsrunner`

On the first run of the script, you will be prompted to authorise. Follow the on screen instructions.

**Running the server**

`python app.py runserver`
