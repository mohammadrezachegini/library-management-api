import boto3
import os
from decouple import config

AWS_REGION = config("AWS_REGION", default="us-east-1")
BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME", default="library-api-covers")
FROM_EMAIL = config("FROM_EMAIL")

session = boto3.Session(
    aws_access_key_id=config("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=config("AWS_SECRET_ACCESS_KEY"),
    region_name=AWS_REGION,
)

s3 = session.client("s3")
ses = session.client("ses")

# ── 1. Test S3 upload ─────────────
def test_s3_upload():
    print("\n📦 Testing S3 upload...")
    test_file = "test-cover.txt"
    
    with open(test_file, "w") as f:
        f.write("This is a test file for S3 upload.")
    
    try:
        s3.upload_file(test_file, BUCKET_NAME, test_file)
        url = f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{test_file}"
        print(f"✅ File uploaded successfully!")
        print(f"   URL: {url}")
        os.remove(test_file)
        s3.delete_object(Bucket=BUCKET_NAME, Key=test_file)
        print(f"✅ Test file cleaned up from S3.")
        
    except Exception as e:
        print(f"❌ S3 test error: {e}")

# ── 2. Test SES email sending ─────────────
def test_ses_email():
    print("\n📧 Testing SES email...")
    try:
        ses.send_email(
            Source=FROM_EMAIL,
            Destination={"ToAddresses": [FROM_EMAIL]},
            Message={
                "Subject": {"Data": "Library API — SES Test"},
                "Body": {
                    "Text": {
                        "Data": "This is a live test from your Library Management API. SES is working!"
                    }
                },
            },
        )
        print(f"✅ Email sent to {FROM_EMAIL} — check your inbox!")

    except Exception as e:
        print(f"❌ SES error: {e}")


if __name__ == "__main__":
    print("🧪 Running live AWS tests...")
    test_s3_upload()
    test_ses_email()
    print("\n✅ All tests done!")