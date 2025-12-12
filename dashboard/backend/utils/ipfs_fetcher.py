import ipfshttpclient

client = ipfshttpclient.connect("/ip4/127.0.0.1/tcp/5001")

def fetch_json(cid: str):
    try:
        return client.cat(cid).decode("utf-8")
    except Exception as e:
        return {"error": str(e)}
