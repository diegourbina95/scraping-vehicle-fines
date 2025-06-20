import requests
import json
import urllib3
from datetime import datetime
import time

default_headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

session = requests.Session()
session.headers.update(default_headers)


class antiNetworking:

    client_key = ""
    website_url = ""
    website_key = ""
    website_stoken = ""
    proxy_type = "http"
    proxy_address = ""
    proxy_port = 0
    proxy_login = ""
    proxy_password = ""
    user_agent = ""
    cookies = ""

    is_verbose = 0
    err_string = ""
    task_id = 0
    error_code = ""

    def get_balance(self):
        result = self.make_request("getBalance", {"clientKey": self.client_key})
        if result != 0:
            return result["balance"]
        else:
            return -1

    def create_task(self, post_data):
        new_task = self.make_request("createTask", post_data)
        if new_task == 0:
            return 0
        else:
            if new_task["errorId"] == 0:
                self.task_id = new_task["taskId"]
                return 1
            else:
                self.error_code = new_task["errorCode"]
                self.err_string = "API error "+new_task["errorCode"] + ": "+new_task["errorDescription"]
                return 0

    def wait_for_result(self, max_seconds=300, current_second=0):

        if current_second >= max_seconds:
            self.err_string = "task solution expired"
            return 0

        time.sleep(1)
        task_check = self.make_request("getTaskResult", {
            "clientKey": self.client_key,
            "taskId": self.task_id
        })
        if task_check == 0:
            return 0
        else:
            if task_check["errorId"] == 0:
                if task_check["status"] == "processing":
                    self.log("task is still processing")
                    return self.wait_for_result(max_seconds, current_second+1)
                if task_check["status"] == "ready":
                    self.log("task solved")
                    return task_check
            else:
                self.error_code = task_check["errorCode"]
                self.err_string = "API error "+task_check["errorCode"] + ": "+task_check["errorDescription"]
                self.log(self.err_string)
                return 0

    # def wait_for_result(self):

    def make_request(self, method, data):
        self.log("making request to "+method)

        try:
            response = session.post("https://api.anti-captcha.com/"+method, data=json.dumps(data))
        except requests.exceptions.HTTPError as err:
            self.log("HTTPError", err.errno, err.strerror, err.args, err.filename)
            self.err_string = "http_error"
            for errArg in err.args:
                if "Network is unreachable" in str(errArg):
                    self.err_string = "Network is unreachable"
                if "Connection refused" in str(errArg):
                    self.err_string = "Connection refused"
            return 0
        except requests.exceptions.ConnectTimeout:
            self.err_string = "Connection timeout"
            return 0
        except urllib3.exceptions.ConnectTimeoutError:
            self.err_string = "Connection timeout"
            return 0
        except requests.exceptions.ReadTimeout:
            self.err_string = "Read timeout"
            return 0
        except urllib3.exceptions.MaxRetryError as err:
            self.err_string = "Connection retry error: "+err.reason
            return 0
        except requests.exceptions.ConnectionError:
            self.err_string = "Connection refused"
            return 0
        return response.json()

    def set_key(self, value):
        self.client_key = value

    def set_website_url(self, value):
        self.website_url = value

    def set_website_key(self, value):
        self.website_key = value

    def set_website_stoken(self, value):
        self.website_stoken = value

    def set_proxy_type(self, value):
        self.proxy_type = value

    def set_proxy_address(self, value):
        self.proxy_address = value

    def set_proxy_port(self, value):
        self.proxy_port = value

    def set_proxy_login(self, value):
        self.proxy_login = value

    def set_proxy_password(self, value):
        self.proxy_password = value

    def set_user_agent(self, value):
        self.user_agent = value

    def set_cookies(self, value):
        self.cookies = value

    def set_verbose(self, value):
        self.is_verbose = value

    def log(self, msg):
        if self.is_verbose:
            print (msg)

    def get_time_stamp(self):
        return int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds())

