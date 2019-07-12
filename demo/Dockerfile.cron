FROM alpine

# Run every minute
RUN echo '*  *  *  *  *    wget -qO- response:8000/slack/cron_minute' > /etc/crontabs/root

# Run crond in the foreground
CMD ["crond", "-f"]