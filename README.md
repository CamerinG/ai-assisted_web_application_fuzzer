# AI-Assisted Web Application Fuzzer

## Description
Businesses that rely on web-facing applications face the persistent problem of finding security vulnerabilities before attackers are able to exploit them. One aspect of finding vulnerabilities includes application fuzzing, which is basically testing data on input fields to find  possible vulnerabilities. Traditional web application fuzzing uses prewritten wordlists and randomly mutated inputs to test against input fields, this can be inefficient and waste computing resources and a security analyst's time. The goal of this project is to create an intelligent automated system that learns which payload characteristics are more likely to expose vulnerabilities. Undetected vulnerabilities can result in data breaches, regulatory penalties and reputational damage, this tool can help mitigate that by allowing the security team to use an efficient method of fuzzing to quickly and accurately elicit vulnerabilities before they are used by a bad actor.
Description: sql injection is a type of security vulnerability that allows attackers to gain access to database features of an application. The dataset will reflect this by containing queries to databases. The xss payloads are similar in the sense that they inject code that alters the webpage.
Example: sql queries tell the database what to do such as SELECT * FROM db WHERE -here is where it connects to an input field on the webpage, so after the ‘WHERE’ is a single quote, if you close that quote and inject something like - ‘1 OR ‘1’=1’ - you will have closed the original area where the input lives and now you can add more query information, in this case since 1=1 is true we will be able to select all database queries, this can be very dangerous for companies because it opens the door for a bad actor to manage their database. 

## Application Guide (how to run)
1. Clone the repository
2. Create and activate virtual environment:
   venv\Scripts\activate
3. Install dependencies:
   pip install -r requirements.txt
4. Run predictions (no DVWA required):
   python src/predict.py
5. To retrain the model:
   python src/train.py
6. To run the fuzzer (requires DVWA and Kali VM):
   python src/fuzzer.py

predict.py:
This is the file that runs payloads through the model and outputs what the model predicts the outcome of the payload to be (triggered (1) or not (0)) as well as a 'confidence' score of how confident the model was about the outcome. 

train.py:
This file is where the model is trained, and it has outputs such as feature importance and f1 scores to see how well the model is performing.

fuzzer.py:
This file is the actual fuzzer that is run against the web application (in this case, the Damn Vulnerable Web Application (DVWA)). It fires payloads from curated wordlists at SQLi and XSS endpoints, logs the HTTP responses, and labels each result based on whether a vulnerability was triggered. The outputs include a CSV file containing the labeled request/response dataset used for model training, as well as a safety score representing the percentage of payloads that did not trigger a vulnerability.

features.py:
This processes the fuzzing results (fuzzing_results.csv). 

## Overview
This project is an AI-assisted Web application fuzzer, fuzzing is 'a software testing technique aimed at identifying bugs, vulnerabilities, or unexpected behavior by automatically providing a program with unexpected, malformed, or semi-malformed inputs'(https://owasp.org/www-community/Fuzzing). Artificial intelligence can be used to predict payloads that have a higher probability of triggering a vulnerability in a web application. This is useful because many businesses have client facing web apps, and it's the job of a security team to ensure that bad actors can't expose company vulnerabilities and if they have a tool to help them, then they can more efficiently secure the site. 

## ML Model 
Method: Random Forest supervised binary classification
This method handles tabular data well, and works great for small to medium sized datasets. The payloads will be scored by predicted vulnerability probability.The model will predict if the payload is likely to trigger a vulnerability (1) or not (0). Feature importance will give insight to understand why the model is making its predictions and what features it's using the most to make those predictions.
Advantages:
Handles tabular, mixed-type datasets well
Many decision trees help reduce overfitting
Provides feature importance rankings which will help identify which payload characteristics influence predictions the most
Disadvantages:
Can be computation resource intense due to large number of trees
Less effective if the datasets are imbalance, so more attention and time will need to be spent on the datasets


## Motivation
This project was built to explore the intersection of machine learning and offensive security tooling, specifically how ML can improve the efficiency of web application penetration testing. It was developed as part of WGU D683 Advanced AI/ML coursework.

## Tech Stack
- DVWA (Damn Vulnerable Web Application)
- Python 3.11
- scikit-learn
- pandas, numpy
- BeautifulSoup4
- requests
- joblib
- Kali Linux (VirtualBox VM)
- VS Code

## Software/Hardware Requirements 
Software:
- Python 3.11
- VS Code
- All dependencies in requirements.txt
pip install -r requirements.txt

Hardware:
- Windows 11
- 12th Gen Intel Core i9-12900KF
- 64GB RAM

****Note: The trained model (models/random_forest_model.pkl) is included in the repository. Running predict.py does not require DVWA or a virtual machine.****

## Challenges and Solutions
Setting up the environment came with many challenges.
DVWA is running inside a kali linux virtual machine, Setting up the communication between the host machine and the vm required configuring two seperate network adapters. One adapter uses NAT mode so the vm has access to the internet (through the host machine). The second adapter uses a Host-Only network, this creates a private network between the host and the vm, this network is needed for the fuzzer running on the host Windows to send the HTTP requests directly to DVWA. Without the host-only adapter the vm was unreachable from the host.

Another early challenge was that all requests to DVWA were returning "CSRF token is incorrect" errors. DVWA embeds a unique token in a hidden HTML input field on every page, requiring that token to be included with every form submission. Unlike session cookies which are handled automatically by the requests library, CSRF tokens must be manually extracted from the page using BeautifulSoup and included as a parameter in each subsequent request. So before firing a payload, the target page had to be fetched and the response parsed for the token so it could be injected back into the request parameters. 

When working with the sql injection a payload of a number (i.e. 1) would trigger as true, meaning that the payload worked. However, this was a false positive, the payload of a number is not an sql injection, it is just the id for the data, so if you put 5 into the input section of the SQLi page it will show 'bob smith' because that is the user with the id of 5. This was fixed by ensuring that the response contained multiple indicators, so if the payload works you should get access to more of the database than one person, so the indicator 'first name:' should come up at least twice. 

When working with the cross site scripting portion a payload of 'hello' triggers a 'true' payload, this is a false-positive. This happened because I originally had the detect_xss function set up to detect if the response included the payload, because that would mean it reflected my input. But because cross site scripting endpoints reflect whatever is sent, back, it may be the case that when the next CSRF token is fetched that the previous payload is still there because its grabbing the html token before each payload. basically when you input a payload it is reflected and the next payload reads it when it attempts to fetch the CSRF token. This was fixed by checking if the payload itself contains a < character before marking it as triggered, plain text payloads like 'hello' will never contain HTML tags, so they correctly return False regardless of what's reflected in the response.

## Dataset Generation
The dataset used is SecLists (Daniel Miessler, Github, https://github.com/danielmiessler/seclists), PayloadsAllTheThings(swisskyrepo, GitHub, https://github.com/swisskyrepo/payloadsallthethings), and self-generated data through controlled fuzzing of DVWA. 


## Results
After training the random forest classifier the model accuracy score was 1.0 on the first try, this was a very suspicious accuracy score. I removed some features that I had originally put in, such as response_length, and response code. I then got an accuracy score of 0.99, still extremely high, but this is to be expected because the environment being tested on (DVWA) is controlled and I have the security set to low (because this is a proof of concept project for testing), in real world testing web applications would have more noise and the model would get lower scores. The final model achieved an F1 score of 0.98, precision of 0.98, and recall of 0.99 on the held-out test set, exceeding the target F1 score of 0.85 defined in the project proposal.

## Future Work
A planned extension is a payload mutation and feedback loop — using high-confidence predictions to seed new payload variants, iteratively refining a target-specific payload list with increasing vulnerability probability. This would move the system from passive classification toward active adaptive fuzzing. This would allow a security team to find more vulnerabilities at the endpoints and protect them, and then the team could rinse-and-repeat. 