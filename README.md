# Overview

### DataBase

1. check the containers

2. run the migration script

3. check the tables
```shell
mysql> use fastapi_demo;
Database changed
mysql> show tables;
+------------------------+
| Tables_in_fastapi_demo |
+------------------------+
| classes                |
| courses                |
| stu_courses            |
| students               |
| teachers               |
| users                  |
+------------------------+
6 rows in set (0.00 sec)
```


### API Example

+ Login

```shell
$ curl -X POST \
>    -H "Content-Type: application/json" \
>    -H "Accept: application/json" \
>    -d '{"name":"tonystark","password":"12345678"}' \
>    http://127.0.0.1:8080/users/login
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100    42    0     0  100    42      0     85 --:--:-- --:--:-- --:--:--    85

```

+ Create User
```shell
$ curl -X POST \
>    -H "Content-Type: application/json" \
>    -H "Accept: application/json" \
>    --cookie "auth_token=ijqqGSmdcGnn&&SeweQ67TDtJEPCb9yFoteL" \
>    -d '{"name":"admin","password":"12345678"}' \
>    http://127.0.0.1:8080/users
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100    38    0     0  100    38      0   4638 --:--:-- --:--:-- --:--:--  5428

```

+ Create Teachers
```shell
$ curl -X POST \
>    -H "Content-Type: application/json" \
>    -H "Accept: application/json" \
>    --cookie "auth_token=ijqqGSmdcGnn&&SeweQ67TDtJEPCb9yFoteL" \
>    -d '{"name":"TeacherJames"}' \
>    http://127.0.0.1:8080/others/teachers
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100    23    0     0  100    23      0      4  0:00:05  0:00:05 --:--:--     0
```

+ Create Class

```shell
$ curl -X POST \
>    -H "Content-Type: application/json" \
>    -H "Accept: application/json" \
>    --cookie "auth_token=ijqqGSmdcGnn&&SeweQ67TDtJEPCb9yFoteL" \
>    -d '{"name":"ClassOne"}' \
>    http://127.0.0.1:8080/others/classes
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100    19    0     0  100    19      0    460 --:--:-- --:--:-- --:--:--   463

```

+ Create Students

```shell

$ curl -X POST \
> -H "Content-Type: application/json" \
> -H "Accept: application/json" \
> --cookie "auth_token=ijqqGSmdcGnn&&SeweQ67TDtJEPCb9yFoteL" \
> -d '{"name":"studentAlice","phone":"12131213121","teacher":{"id":"igBr2Z6M9pksat4fvNKSj4"},"class_":{"id":"aD88zjHAmC5tgrGEiorsk2"}}' \
> http://127.0.0.1:8080/stu/students
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   160  100    32  100   128      6     25  0:00:05  0:00:05 --:--:--     8
```
