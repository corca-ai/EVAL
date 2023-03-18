# Usage

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

## Environment

You must need this environments.

```
OPENAI_API_KEY
```

You need this environments.

```
serpapi: SERPAPI_API_KEY
bing-search: BING_SEARCH_URL, BING_SUBSCRIPTION_KEY
```
