FROM python:3.9-slim
WORKDIR /bot
COPY . .
RUN python3 -m pip install --upgrade pip
RUN pip3 install -r requirements.txt
CMD python3 bot.py || reboot
