import boto3
import requests
import time


def create_input_s3_presigned_url(aws_key = '', aws_secret = '', bucket_name = '', input_file = ''):
    # Instantiate Boto Client
    s3_client = boto3.client('s3',
                             aws_access_key_id = aws_key,
                             aws_secret_access_key = aws_secret)

    # Create input presigned URL
    aws_input_url = s3_client.generate_presigned_url('get_object',
                                                     Params = {'Bucket': bucket_name,
                                                               'Key': input_file})
    return aws_input_url



def create_output_s3_presigned_url(aws_key = '', aws_secret = '', bucket_name = '', output_path = '', output_file = ''):
    # Instantiate Boto Client
    s3_client = boto3.client('s3',
                             aws_access_key_id = aws_key,
                             aws_secret_access_key = aws_secret)

    # Create output presigned URL
    aws_output_url = s3_client.generate_presigned_url('put_object',
                                                  Params = {'Bucket': bucket_name,
                                                            'Key': output_path + output_file})
    return aws_output_url

def get_file_keys(aws_key = '', aws_secret = '', bucket_name = '', bucket_path = '', file_type = ''):
    # Instantiate empty list
    key_list = []

    # Instantiate Boto Client
    s3_client = boto3.client('s3', aws_access_key_id = aws_key, aws_secret_access_key = aws_secret)

    # returns objects in bucket_name
    files = s3_client.list_objects_v2(Bucket = bucket_name)

    # turn files uglyness into a list of files
    for file in files['Contents']:
        if file['Key'].startswith(bucket_path) and file['Key'].endswith(file_type):
            key_list.append(file['Key'])
    return key_list

def build_enhancement_json(user_params_dict):

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

    params_dict.update(user_params_dict)

    json = {"audio": {
        "loudness": {
            "enable": params_dict['loudness_enable']
        },
        "dynamics": {
            "range_control": {
                "enable": params_dict['dynamics_enable'],
                "amount": params_dict['dynamics_amount']
            }
        },
        "noise": {
            "reduction": {
                "enable": params_dict['noise_enable'],
                "amount": params_dict['noise_amount']
            }
        },
        "filter": {
            "high_pass": {
                "enable": params_dict['filter_high_pass_enable'],
                "frequency": params_dict['filter_high_pass_freq']
            }
        },
        "speech": {
            "isolation": {
                "enable": params_dict['speech_iso_enable'],
                "amount": params_dict['speech_iso_amount']},
            "sibilance": {
                "reduction": {
                    "enable": params_dict['speech_sibilance_enable'],
                    "amount": params_dict['speech_sibilance_amount']}
            }
        }
    }
           }
    return json

def dolby_enhance_audio(
    dolby_api = '',
    aws_key = '',
    aws_secret = '',
    bucket_name = '',
    input_file = '',
    output_path = '',
    output_file = '',
    get_status_updates = 10,
    user_params_dict = {}

):

    json_dict = {'input': create_input_s3_presigned_url(aws_key = aws_key,
                                                        aws_secret = aws_secret,
                                                        bucket_name = bucket_name,
                                                        input_file = input_file),
                 'output': create_output_s3_presigned_url(aws_key = aws_key,
                                                          aws_secret = aws_secret,
                                                          bucket_name = bucket_name,
                                                          output_path = output_path,
                                                          output_file = output_file)}

    json_dict.update(build_enhancement_json(user_params_dict))

    post_request_enhance = requests.post('https://api.dolby.com/media/enhance',
                                         headers = {'x-api-key': dolby_api},
                                         json = json_dict)

    status_url = 'https://api.dolby.com/media/enhance?job_id=' + post_request_enhance.json()['job_id']

    status = requests.get(status_url, headers = {'x-api-key': dolby_api}).json()

    while status['status'] == 'Running':
        status = requests.get(status_url, headers = {'x-api-key': dolby_api}).json()
        print(status)
#         print(f'Time elapsed: {time.time() - time_start}s')
        status = status
        time.sleep(get_status_updates)

def enhance_multiple_files(
    dolby_api = '',
    aws_key = '',
    aws_secret = '',
    bucket_name = '',
    input_bucket_path = '',
    output_path = '',
    output_prefix = '',
    get_status_updates = 10,
    file_type = '.wav',
    user_params_dict = {}
):
    """
    *** NOTE YOU NEED TO HAVE AMAZON S3 PERMISSION SET UP CORRECTLY ***
    ** For information on setting up s3 permission please see the following resources:
    ** https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp_request.html
    ** https://medium.com/@aidan.hallett/securing-aws-s3-uploads-using-presigned-urls-aa821c13ae8d

    dolby_api = REQUIRED

    aws_key = REQUIRED

    aws_secret = REQUIRED

    bucket_name = REQUIRED, Name of s3 bucket

    input_bucket_path = Used to specicfy input folder in s3 bucket

    output_path = REQUIRED, Used to specicfy input folder in s3 bucket

    output_prefix = Used to add prefix to output file

    !!WARNING!! Requesting to frequently for to long can result in errors
    get_status_updates = int -> Seconds between each get status request

    file_type = 'str' -> specify audio format ex: '.wav', '.mp3',...

    user_param_dict = {dict} -> these are for changing the default values of the dolby enhance

    The following parameters can be entered to tune the audio enhancement,
    more information can be found at
    (https://dolby.io/developers/media-processing/tutorials/improving-audio-quality)

    user_param_dict = {
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

    """

    key_list = get_file_keys(aws_key = aws_key,
                             aws_secret = aws_secret,
                             bucket_name = bucket_name,
                             bucket_path = input_bucket_path,
                             file_type= file_type)

    for key in key_list:
        dolby_enhance_audio(
            dolby_api = dolby_api,
            aws_key = aws_key,
            aws_secret = aws_secret,
            bucket_name = bucket_name,
            input_file = key,
            output_path = output_path,
            output_file = output_prefix + key[len(input_bucket_path):],
            get_status_updates = get_status_updates,
            user_params_dict = {})
