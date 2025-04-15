# ShotMatch
This project can analyze your shooting similarity and consistency with some professional basketball players.

## System Requirement
MacOS version 11 or later\
Ubuntu 18.04 or later

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

### Ubuntu
Run the commands below: 
```
# Download and install nvm:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.2/install.sh | bash

# in lieu of restarting the shell
\. "$HOME/.nvm/nvm.sh"

# Download and install Node.js:
nvm install 22

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
brew install node
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
Use connect feature on the Expo, type the link above into the Expo Go then you can access our software
