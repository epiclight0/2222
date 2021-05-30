FROM gcr.io/google-appengine/python
RUN apt-get update && apt-get -y install  gconf-service libasound2 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils wget

RUN virtualenv /env
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

RUN mkdir /usr/share/2222
ADD . /usr/share/2222
WORKDIR /usr/share/2222
ADD requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
EXPOSE 8080
ENTRYPOINT ["gunicorn", "-b", ":8080", "main:app"]
