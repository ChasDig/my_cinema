FROM nginx:1.29.0

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/ /etc/nginx/conf.d/

CMD ["nginx", "-g", "daemon off;"]
