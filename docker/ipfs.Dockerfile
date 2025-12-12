FROM ipfs/go-ipfs:latest

EXPOSE 4001 5001 8080

CMD ["ipfs", "daemon", "--init", "--migrate=true"]
