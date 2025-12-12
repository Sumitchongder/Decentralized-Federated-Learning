FROM node:20-alpine

WORKDIR /app

COPY hardhat/package.json hardhat/package-lock.json ./
RUN npm install

COPY hardhat/ .

EXPOSE 8545

CMD ["npx", "hardhat", "node"]
