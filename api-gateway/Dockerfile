FROM nginx:alpine

COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY conf/default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \ 
  CMD wget --spider -q http://localhost:80/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
