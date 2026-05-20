# AI-Assisted Web Application Fuzzer

## Overview
This project is an AI-assisted Web application fuzzer, fuzzing is 'a software testing technique aimed at identifying bugs, vulnerabilities, or unexpected behavior by automatically providing a program with unexpected, malformed, or semi-malformed inputs'(https://owasp.org/www-community/Fuzzing). Artificial intelligence can be used to predict payloads that have a higher probability of triggering a vulnerability in a web application. This is useful because many businesses have client facing web apps, and it's the job of a security team to ensure that bad actors can't expose company vulnerabilities and if they have a tool to help them, then they can more efficiently secure the site. 


## Motivation
This project was built to explore the intersection of machine learning and offensive security tooling, specifically how ML can improve the efficiency of web application penetration testing. It was developed as part of WGU D683 Advanced AI/ML coursework.

## Tech Stack
DVWA (Damn Vulnerable Web Application)


## Architecture

## Challenges and Solutions
Setting up the environment came with many challenges.
DVWA is running inside a kali linux virtual machine, Setting up the communication between the host machine and the vm required configuring two seperate network adapters. One adapter uses NAT mode so the vm has access to the internet (through the host machine). The second adapter uses a Host-Only network, this creates a private network between the host and the vm, this network is needed for the fuzzer running on the host Windows to send the HTTP requests directly to DVWA. Without the host-only adapter the vm was unreachable from the host.

Another early challenge was that all requests to DVWA were returning "CSRF token is incorrect" errors. DVWA embeds a unique token in a hidden HTML input field on every page, requiring that token to be included with every form submission. Unlike session cookies which are handled automatically by the requests library, CSRF tokens must be manually extracted from the page using BeautifulSoup and included as a parameter in each subsequent request. So before firing a payload, the target page had to be fetched and the response parsed for the token so it could be injected back into the request parameters. 

When working with the sql injection a payload of a number (i.e. 1) would trigger as true, meaning that the payload worked. However, this was a false positive, the payload of a number is not an sql injection, it is just the id for the data, so if you put 5 into the input section of the SQLi page it will show 'bob smith' because that is the user with the id of 5. This was fixed by ensuring that the response contained multiple indicators, so if the payload works you should get access to more of the database than one person, so the indicator 'first name:' should come up at least twice. 

When working with the cross site scripting portion a payload of 'hello' triggers a 'true' payload, this is a false-positive. This happened because I originally had the detect_xss function set up to detect if the response included the payload, because that would mean it reflected my input. But because cross site scripting endpoints reflect whatever is sent, back, it may be the case that when the next CSRF token is fetched that the previous payload is still there because its grabbing the html token before each payload. basically when you input a payload it is reflected and the next payload reads it when it attempts to fetch the CSRF token. This was fixed by checking if the payload itself contains a < character before marking it as triggered, plain text payloads like 'hello' will never contain HTML tags, so they correctly return False regardless of what's reflected in the response.
## Dataset Generation

The dataset used is SecLists (Daniel Miessler, Github, https://github.com/danielmiessler/seclists), PayloadsAllTheThings(swisskyrepo, GitHub, https://github.com/swisskyrepo/payloadsallthethings), and self-generated data through controlled fuzzing of DVWA. 

## ML Model
## Results

after training the random forest classifier the model accuracy score was 1.0 on the first try, this was a very suspicious accuracy score. I removed some features that I had originally put in, such as response_length, and response code. I then got an accuracy score of 0.99, still extremely high, but this is to be expected because the environment being tested on (DVWA) is controlled and I have the security set to low (because this is a proof of concept project for testing), in real world testing web applications would have more noise and the model would get lower scores. The final model achieved an F1 score of 0.98, precision of 0.98, and recall of 0.99 on the held-out test set, exceeding the target F1 score of 0.85 defined in the project proposal.

## Future Work