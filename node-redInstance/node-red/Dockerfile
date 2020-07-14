FROM nodered/node-red:latest

# install pip
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py
ENV PATH $PATH:/usr/src/node-red/.local/bin
# install python package
# RUN pip3 install ~

ENV DATA_FOLDER=node-red

# Copy package.json to the WORKDIR so npm builds all
# of your added modules for Node-RED
COPY /$DATA_FOLDER/package.json .
RUN npm install --only=production

# Copy _your_ Node-RED project files into place
COPY /$DATA_FOLDER/settings.js /data/settings.js
COPY /$DATA_FOLDER/flows_cred.json /data/flows_cred.json
COPY /$DATA_FOLDER/flows.json /data/flows.json

# Start the container normally
CMD ["npm", "start"]

