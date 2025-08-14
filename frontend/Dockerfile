# build 階段
FROM node:20 AS build
WORKDIR /app
COPY . .
ARG REACT_APP_API_URL
ARG REACT_APP_SOCKET_URL
ARG REACT_APP_GOOGLE_CLIENT_ID

# 建立 .env 檔，讓 React 編譯能抓到
RUN echo "REACT_APP_API_URL=$REACT_APP_API_URL" > .env && \
    echo "REACT_APP_SOCKET_URL=$REACT_APP_SOCKET_URL" >> .env \
    echo "REACT_APP_GOOGLE_CLIENT_ID=$REACT_APP_GOOGLE_CLIENT_ID" >> .env

RUN npm install
RUN npm run build

# production 階段
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

RUN cat /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
