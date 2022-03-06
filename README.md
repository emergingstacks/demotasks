# demotasks

## Run Terraform Code
### Make sure you have created a bucket on aws, which stores terraform state file.
```commandline
cd terraform && terraform init && terraform plan
terraform apply
```
### Run Python code on linux box
####Note: Make sure you have docker, awscli and git installed
```commandline
export aws credentials
export AWS_ACCESS_KEYID="xxxxxxxxx"
export AWS_SECRET_ACCESS_KEY="xxxxxxxxx"

cd scripts
pip3 install -r requirements.txt
python3 upload_image.py
```