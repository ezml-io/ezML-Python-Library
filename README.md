# Basic overview:

First run `pip install .` inside the directory to be able to use the library

## Credentials
Credentials can be explicitly created using the `EzMLCredentials` class,
```
creds = EzMLCredentials(username, password)
```
and then passed to `EzMLApp`,
```py
app = EzMLApp(app_id, credentials=creds)
```

If nothing is passed, the username & password will try to be found in the enviroment under the keys: `EZML_USER` and `EZML_PASS`

## Apps
An app can be created supplied with an app_id and credentials (done by default if in enviroment).
```py
app = EzMLApp(app_id, credentials=creds)
```
Then to be able to infer, the app needs to be deployed so `app.deploy()` must be called

For information on how inference works check the `test/` directory for examples.




