# CS157C-team2
A noSQL project using MongoDB

Building Instructions:
Flask
1. Create a virtual environment
python3 -m venv .venv

2. Activate the virtual environment
. .venv/bin/activate

3. Install the required libraries
pip install -r requirements.txt

4. Go to the Google developers credentials page
https://console.developers.google.com/apis/credentials

5. Once in, you may be prompted to agree to their terms of service. Should you agree to those, press the Create credentials button on the next page. Select the option for OAuth client ID
![Alt text](https://github.com/prabhate/CS157C-team2/blob/main/docs/gauth1.png)

6. Select the 'Web application' option at the top

7. Set the 'Authorized JavaScript origins' to https://127.0.0.1:5000

8. Set the 'Authorized redirect URIs' to https://127.0.0.1:5000/login/callback

9. Hit Create and take note of the Client ID and Client secret

10. Add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET with the values from step 9 to environment variables.

11. An alternate way is to directly paste the strings and store them in these variables in app.py file.

12. cd to dev/flask

13. run `python3 app.py`
