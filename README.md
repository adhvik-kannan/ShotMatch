# ShotMatch
## Introduction
This project can analyze your shooting similarity and consistency with some professional basketball players. This software is a perfect alternative when you cannot afford a coach. It also gives you historical data for you to analyze, and lets you choose the player you want to compare yourself to. It also gives you a professional player's curve to show where your shooting is when you give your score.

## Server System Requirement
MacOS version 11 or later\
Ubuntu 18.04 or later

## User System Requirement
Android 10 or later\
IOS 14 or later

## Install Instruction

1. First clone the github repository
```
git clone https://github.com/adhvik-kannan/ShotMatch.git
```
2. install the requirement file
```
pip install -r requirement.txt
```
Before proceeding to next step, we need to install NodeJS on your laptop.\
If you are not certain if NodeJS is installed on your laptop or not, run the following commands:
```
node -v
npm -v
```
If the output is not v22.14.0, follow the platform-specific steps below.

### Ubuntu
Run the commands below: 
```
# Download and install nvm:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.2/install.sh | bash

# in lieu of restarting the shell
\. "$HOME/.nvm/nvm.sh"

# Download and install Node.js:
nvm install 22.14.0
nvm use 22.14.0

# Verify the Node.js version:
node -v # Should print "v22.14.0".
nvm current # Should print "v22.14.0".

# Verify npm version:
npm -v # Should print "10.9.2".
```

### MacOS
For MacOS users, you can use homebrew to install npm\
Commands to install homebrew:
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
Commands to install NodeJS:
```
brew install node@22

# Verify versions
node -v  # Should print "v22.14.0"
npm  -v  # Should print "10.9.2"
```

3. Build the project locally
```
cd frontend/ShotMatch
npm install
```

4. Run the project locally
```
npm run
```
It will give you a URL to access the app. To access the app, you can go to your phone's appstore to install <ins>**Expo Go**</ins>\
After you finish install the Expo Go
You should see an output on the server that said:\
*Metro waiting on exp://<ip_addr>:<port_num>*\
Use connect feature on the Expo, type the 
*exp://<ip_addr>:<port_num>* above into the Expo Go then you can access our software.

## User manual
***Access the [User Manual](https://github.com/adhvik-kannan/ShotMatch/blob/integration/1.0/UserManual.md) here***

## Report Issue
Please follow the following format when report the issue
### 1. Issue Type
1. Bug Report
2. Feature Request
3. Enhancement Suggestion
4. Performance Issue
5. Other (please describe)
### 2. Description
Provide a clear and concise description of the issue or suggestion\
recommended template:\
Summary: ...\
Expected Behavior: ...\
Actual Behavior: ...
### 3. Context
Include relevant information
1. Selected professional player for comparison
2. Device used
3. Camera type (if relevant)
4. ShotMatch version
### 4. Screenshots / Video (if applicable)
Take screenshots or videos here to help explain your issue.
### 5. Steps to reproduce
Show the steps to reproduce the bug so it can save us a lot of time.
### 6. Feature Request Details (if applicable)
What's the feature you’d like to see?\
Why do you think it's useful?

***Submit the Issue/Request in our [GitHub Issue Page](https://github.com/adhvik-kannan/ShotMatch/issues)***
