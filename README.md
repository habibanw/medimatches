# MediMatch

These are the instructions for the MediMatch for setting up and deploying the Django application for MediMatch.

## Initial Setup

1. Install Docker ([Mac](https://docs.docker.com/docker-for-mac/install/) or [Windows](https://docs.docker.com/docker-for-windows/install/))

After installation, run `docker --version` to verify that Docker is installed correctly.

2. Clone the repository from the ~~GitLab~~ GitHub repository and change into the repository's directory

```bash
git clone https://github.com/slenguyen/medimatch.git
cd medimatch
```

3. Create an `.env` file with the following environment variables:

```bash
DJANGO_SECRET_KEY=<your_secret_key>
```

4. Build the Docker image

```bash
docker build .
```

5. Run the Docker container

```bash
docker-compose up
```

Troubleshooting: if you get an error related to the database container not running properly, try removing the volume:

```bash
docker-compose down --volumes
```

Or you can try rebuilding the container:

```bash
docker compose build --no-cache
```

and then retry the `docker-compose up` command.

6. Open your web browser and navigate to `http://127.0.0.1:8000/` to view the application.

## Working with the application

### Accessing PostgreSQL

To access the PostgreSQL database, you'll need to exec into the db container within Docker. Note that the name of the database, user, and password are all `postgres`. This is configured in `docker-compose.yml`.

First, find the name of your database docker container:

```bash
docker ps # will be the one that contains "db" in the name
```

Then, exec into the container:

```bash
docker exec -it <container-name> psql -U postgres -W postgres
```

When prompted, enter `postgres` as the password.

If you need to work with Postgres via the cli, after you exec in, you'll need to select the database:

```bash
\c postgres # password is postgres (again)
```

Once you select the database, you can list tables like so:

```bash
\dt
```

More info on running raw SQL at the [command line](https://www.warp.dev/terminus/psql-run-sql-file) and [backing up/restoring databases](https://davejansen.com/how-to-dump-and-restore-a-postgresql-database-from-a-docker-container/).

### Accessing the Django Shell

You'll need to exec into the web container in order to access the Django shell. First, find the name of your web docker container:

```bash
docker ps # will be the one that contains "web" in the name
```

Then, exec into the container:

```bash
docker exec -it <container-name> python manage.py shell
```

You can also manually run the migration command this way:

```bash
docker-compose exec web python manage.py migrate
```

### Troubleshooting with migrations

If you are running into issues like "Dependency on app with no migrations". Check out if the migrations are currently are empty lists with the following command.

```bash
docker-compose exec web python manage.py showmigrations
```

If they are, then run:

```bash
docker-compose exec web python manage.py makemigrations
```

Then you can try the manual migration command from before.

If all else fails, delete the volume holding the postgres data and rebuild Docker:

```bash
docker volume rm <volume name, probably medimatch_postgres_data> # find it with docker volume ls
docker compose up --build
``` 

### Adding packages/libraries

Add any necessary packages to the `requirements.txt` file. Then, rebuild the Docker image:

```bash
docker-compose up -d --build
```

If you want to commit those packages, be sure to update requirements.txt, or else other team members and Heroku won't be able to use them.

```bash
pip freeze > requirements.txt
```

Then, commit the updated `requirements.txt` file to the repository.

### Shutting down the application

```bash
docker-compose down
```

### Working with admin

When working with admin, you need to create a superuser, so since we are working within the docker container, we need to run this:

```bash
docker-compose exec web python manage.py createsuperuser
```

This will then prompt you to enter an email and password, so you will enter it:

Ex: admin@example.com
pass: password123

It is worth noting that the superuser account allows access to the Django admin interface, and so once you create a auth for it, you
can also delete it if necessary by running this command.

```bash
docker-compose exec web python manage.py createsuperuser --delete <username>
```

## Testing

### Running unit tests

The following command runs all tests existing the tests folder, because this command will discover all files with the pattern test\*.py

```bash
docker exec -it <container-web-name> python manage.py test
```

Tests are located in pages/tests/test\*.py.

In order to run specific tests, you need to specifiy the full dot path to the test, subclass, or method. For example, to run the model tests you would do the following command, where the directory is pages/tests/and the test_models is the test file desired.

```bash
docker exec -it <container-web-name> python manage.py test pages.tests.test_models
```

Or you can specify to test one subclass like the following:

```bash
docker exec -it <container-web-name> python manage.py test pages.tests.test_models.ProviderTest
```

And further specification like the same command and just add....CustomUserModelTest.test_custom_user will further specifiy the test desired in that subclass needed to be tested, which in this case was the test_custom_user in the CustomUserModelTest test method.

### Running e2e (Cypress) tests

To run the Cypress (aka: end to end, e2e, integration) tests within Docker, you need to exec into the `test` container and run the cypress command:

```bash
docker exec -it <container-name> npx cypress run
```

The container will likely be called `medimatch-test-1` or similar.

You can also run the tests locally after running `npm install` within the project directory, and then running:

```bash
npx cypress run
```

Troubleshooting: If you get a message that Cypress can't find the installed binary due to caching configuration, you can run the tests outside Docker as described below. You can also completely rebuild the Docker environment with the following command, which is also how to fix problems with running out of disk space.

```bash
docker system prune -a
```

To open up Cypress's application when running tests outside of Docker, run:

```bash
npx cypress run --env environmentName=local
```

When tests fail, you can view screenshots of the failures in the `cypress/screenshots` directory. Note that the contents of th e screenshots directory is deleted before each test run.

### Pushing changes to the repository

Before you start your work, create a new branch and switch to it:

```bash
git checkout -b <branch-name>
```

When you're ready to push changes to the repository, you'll need to add, commit, and push your changes.

```bash
git add .
git commit -m "Your commit message here"
git push origin <branch-name>
```

Then, create a pull request in the ~~GitLab~~ [GitHub repository](https://github.com/slenguyen/medimatch) for code review. Note that GitHub will run unit tests for each PR.

## Importing provider data

We now have a set of commands to handle importing, counting and deleting providers from our dataset. 

Also note that there is a constraint on the provider_id. You cannot attempt to import when a Provider object is stored in the database that has a `provider_id` that is the same as one in the dataset. In other words: delete all of your providers first, then run the import command. 

Make sure your container name matches what is in the commands below -- you want to run them against the web container. 

### Deleting providers

```bash
docker exec -it medimatch-web-1 python manage.py delete-providers
```

### Importing providers

```bash
docker exec -it medimatch-web-1 python manage.py importer
```

By default, the command will only import the first ~28K providers. If you want to import the entire dataset, you can do so by adding the `--all` flag to the command. Be warned that the dataset is VERY large (1.2M+ records), so imports will take awhile (~10 minutes).

```bash
docker exec -it medimatch-web-1 python manage.py importer --all
```

### Counting providers

This command returns the total number of Provider objects stored in postgres. 

```bash
docker exec -it medimatch-web-1 python manage.py counter
```

## Deploying the application

The main branch of the application will be deployed to Heroku when both of these conditions are true:

1. Unit tests pass (see the `continuous-integration/heroku` of the Pull Request in GitHub)
2. A GitHub Pull Request is merged to the main branch.

After that, GitHub will deploy the application to Heroku and automatically run any migration tasks.

### Heroku setup (if you need it)

If you need access to Heroku:

You'll need to create a [Heroku account](https://signup.heroku.com/) and install the Heroku CLI.

Despite the instructions saying you shouldn't do so, I installed via npm.

```bash
npm install -g heroku # you might have to run this command on Mac with `sudo` depending on your set up.
```

Then, log in to Heroku:

```bash
heroku login
```

You'll be prompted to log in via a web browser.

After you have set up your account, ping Sarah to add you to the [medimatch project](https://dashboard.heroku.com/apps/medimatch).

### Deploying directly to Heroku

We should handle deploys through GitHub, but just in case we ever need to do one directly to Heroku:

Deployment happens on git push of the main repository branch to a new remote called Heroku. This is done by adding a new remote to the repository:

```bash
heroku git:remote -a medimatch
```

Then, push to the Heroku remote:

```bash
git push heroku main
```

It will take a while to build the application (2-4 minutes), but once it's done, you can open the application in your web browser: https://medimatch-5a4f315c8a09.herokuapp.com/

### Logs

You can access the last 1500 log entries with the Heroku CLI by running:

```bash
heroku log
```

I have also set up [Sentry](https://docs.sentry.io/platforms/python/integrations/django/) in case you need to access older logs. After you have access to the Heroku project, you can visit Sentry [here](https://sentry-objective-43077.sentry.io/issues/?project=4506802647924736).
