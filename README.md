# Django Rest Framework Recipes APP // back-end

This project was made for the TravelPerk backend onboarding assignment, feel free to contact me if you have nay questions or concerns about this.  

I've also made a web client implementation for this service, it can be found at:
https://github.com/romulino-travelperk/recipe-app-web-client

# How to run

```
docker-compose up
```

create at least one super-user by running
`./create-super-user.sh`

Point your browser to http://localhost:8000/admin/ to access the django admin panel


#Other things you might want to do

### `./lint.sh`
Runs flake8 to lint the code base

### `./test`
Runs the unit test suite

### `./create-super-user.sh`
Creates the super user that will allow you to access the django admin panel.