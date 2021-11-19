FROM testing:node-red-build
#FROM nodered/node-red

ENV DATA_FOLDER=node-red

# Copy package.json to the WORKDIR so npm builds all
# of your added modules for Node-RED
COPY /$DATA_FOLDER/package.json .
RUN node -v
RUN npm -v
RUN npm install --unsafe-perm --no-update-notifier --no-fund --only=production

# Copy _your_ Node-RED project files into place
COPY /$DATA_FOLDER/settings.js /data/settings.js
COPY /$DATA_FOLDER/flows_cred.json /data/flows_cred.json
COPY /$DATA_FOLDER/flows.json /data/flows.json

# install pip
#ENV PATH $PATH:/usr/src/node-red/.local/bin
USER root
RUN apt-get install -y python3-pip
#RUN wget https://bootstrap.pypa.io/get-pip.py
#RUN python3 get-pip.py
# install python package
# RUN pip3 install ~
USER node-red


# Start the container normally
CMD ["npm", "start"]


