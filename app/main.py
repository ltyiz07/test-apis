from fastapi import FastAPI, Response, Request
from fastapi.responses import ORJSONResponse, HTMLResponse
from pydantic import BaseModel

app = FastAPI()


@app.get("/test/page/", response_class=HTMLResponse)
def get_legacy_data():
    return page

page = \
"""
<!DOCTYPE html>
<html>
<head>
</head>
<body>
    this is test page.

    <script>
        console.log("start");

        const invocation = new XMLHttpRequest();
        const url = 'http://10.10.10.180:3031/save/cookie/';

        function callOtherDomain() {
          if (invocation) {
            invocation.open('GET', url, true);
            invocation.withCredentials = true;
            invocation.onload = function() {
                console.log("data responsed");
                console.log("loaded: ", invocation.getResponseHeader("Set-Cookie"));
                <!-- window.localStorage.setItem( -->
                <!-- ... -->
            };
            invocation.send();
          }
        }
        callOtherDomain();
    </script>
</body>
</html>
"""


@app.get("/test/")
def api_test(req: Request):
    return {"request_header": req.headers}

@app.get("/test/role/sub/")
def sub_role_test(req: Request):
    test_response = {"test_response": {"access": "granted", "status": 200, "user_role": "role"} }
    print(req.headers)

    user_id = req.headers["x-authorization-id"]
    current_service = req.headers["x-authorization-service"]
    user_role = req.headers["x-authorization-role"]
    if ("sub" not in user_role) and ("main" not in user_role):
        return "Unauthorized user."

    test_response["test_response"]["user_id"] = user_id
    test_response["test_response"]["current_service"] = current_service
    test_response["test_response"]["user_role"] = user_role

    return test_response

@app.get("/test/role/main/")
def sub_role_test(req: Request):
    test_response = {"test_response": {"access": "granted", "status": 200, "user_role": "role"} }

    user_id = req.headers["x-authorization-id"]
    current_service = req.headers["x-authorization-service"]
    user_role = req.headers["x-authorization-role"]
    if "main" not in user_role:
        return "Unauthorized user."

    test_response["test_response"]["user_id"] = user_id
    test_response["test_response"]["current_service"] = current_service
    test_response["test_response"]["user_role"] = user_role

    return test_response


@app.get("/test/save/cookie/")
def save_cookie_default(response: Response):
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3031"
    response.set_cookie(key="fakesession", value="fake_cookie-session-value")
    return {"message": "Come to dark side, we have cookie"}


@app.post("/test/save/cookie/{cookie_value}/")
def save_cookie_post(response: Response, cookie_value: str):
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3031"
    response.set_cookie(key="test_token", value=f"Bearer {cookie_value}", httponly=True)
    return {"message": "set test cookie"}


@app.get("/test/save/cookie/{cookie_value}/")
def save_cookie(response: Response, cookie_value: str):
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3031"
    response.set_cookie(key="test_token", value=f"Bearer {cookie_value}", httponly=True)
    return {"message": "set test cookie"}


@app.get("/test/json/", status_code=200)
def test_api():

    return {"data": "test_value_1", "data_2": "test_value_2"}

@app.get("/test/text/", status_code=200)
def test_api():

    return "this is test text"

class Auth(BaseModel):
    loginId: str
    loginPw: str
    services: list[str]

@app.post("/test/text/", status_code=200)
def test_api_with_param(auth: Auth):
    print(auth)
    auth.loginId += " returned"
    return auth
    
