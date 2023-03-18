# AwesomeGPT

Everything you can do with your computer is possible through AwesomeGPT. It can understand and generate data formats for text, image, dataframe, audio (TODO), video (TODO). It must be run inside a container that is only available to it, and it can build your container environment directly through Terminal Tools.

## Usage

1. environments settings
2. S3 Settings
3. Execute `docker-compose up --build -d awesomegpt`

### Environment

You must need this environments.

```
OPENAI_API_KEY
```

You need this environments.

```
serpapi: SERPAPI_API_KEY
bing-search: BING_SEARCH_URL, BING_SUBSCRIPTION_KEY
```

### S3

1. Create a bucket.
2. Turn off the "Block all public access" setting for the bucket. ![image](assets/block_public_access.png)
3. Add the following text to Bucket Policy.
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "AllowPublicRead",
         "Effect": "Allow",
         "Principal": {
           "AWS": "*"
         },
         "Action": "s3:GetObject",
         "Resource": "arn:aws:s3:::{your-bucket-name}/*"
       }
     ]
   }
   ```

## Tools

## TODO

- [ ] memory saving
- [ ] session manage
- [ ] convert to alpaca
- [ ] requests.get refactoring
- [ ] prompt upgrade
- [ ] etc.

## Reference

Thanks to the following repositories.

- https://github.com/jerryjliu/llama_index
- https://github.com/hwchase17/langchain
- https://github.com/microsoft/visual-chatgpt
