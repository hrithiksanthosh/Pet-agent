This is a Python flask Application.

Instruction to run the code:

*without docker container

1.Setup a Mongodb database first- replace the [username], [password] and [ip_address] with your mongodb credentials.
2.Create 2 collections in the mongodb database one for user details and other for pets.
3.Give gmail credentials - replace [email] and [password] with your credentials.
4.Make sure to download all libraries are installed mentioned in requirement.txt
5.Run app.py

*as docker container

1.Setup a Mongodb database first- replace the [username], [password] and [ip_address] with your mongodb credentials.
2.Create 2 collections in the mongodb database one for user details and other for pets.
3.Give gmail credentials - replace [email] and [password] with your credentials.
4.Install docker on your manchine
5.Build image for the application - (command - docker build --tag python-docker-cloud . )
6.run container -( command - docker run python-docker-cloud )
