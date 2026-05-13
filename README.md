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

When working with the sql injection a payload of a number (i.e. 1) would trigger as true, meaning that the payload worked. However, this was a false positive, the payload of a number is not an sql injection, it is just the id for the data, so if you put 5 into the input section of the sqli page it will show 'bob smith' because that is the user with the id of 5. 

When working with the cross site scripting portion a payload of 'hello' triggers a 'true' payload, 
## Dataset Generation
## ML Model
## Results
## Future Work