# Dolpy

## This is a wrapper for using Dolby.io original developed as part of a class project within General Assembly Data Science Immersive Course.

The following wrapper is designed to take files from your AWS S3 bucket, enhance the audio via Dolby's API, and returned to the specified AWS S3 bucket.

### Required libraries:
- boto3 (https://github.com/boto/boto3)
- time (built in)
- requests (https://github.com/psf/requests)

### Examples:
```
# Default Enhancement Parameters, only any changes need to be specified 
# in user_params_dict arguemnt of the main function

params_dict = {
    'loudness_enable': True, 
    'dynamics_enable': True,
    'dynamics_amount': 'max',
    'noise_enable': True,
    'noise_amount': 'max',
    'filter_high_pass_enable': True,
    'filter_high_pass_freq': 80,
    'speech_iso_enable': True,
    'speech_iso_amount': 50,
    'speech_sibilance_enable': True,
    'speech_sibilance_amount': 'low'
}

enhance_multiple_files(
    dolby_api = '[YOUR DOLBY API KEY HERE]',
    aws_key = '[YOUR AWS KEY HERE]',
    aws_secret = '[YOUR AWS SECRET HERE]',
    bucket_name = '[NAME OF YOUR S3 BUCKET]',
    input_bucket_path = '[NAME OF FOLDER WITHIN BUCKET WITH INPUT AUDIO]',  # Leave blank if none
    output_path = '[NAME OF S3 BUCKET TO PUT ENHANCED FILES]',
    output_prefix = '[OPTIONAL STRING YOU CAN PREFIX TO ENHANCED FILES]',
    get_status_updates = 10, # seconds between status updates
    file_type = '.wav', # file type
    user_params_dict = {} # dictionary of enhancement parameters
):
```

### Original Authors:
- https://github.com/codylocks
- https://github.com/alexzadel
- https://github.com/ZachTretter
- https://github.com/lukepods
- https://github.com/jungmoon-ham
