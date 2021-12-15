#######################################
############## LIBRARIES ##############

import re
from   airflow.models             import DAG
from   datetime                   import datetime
from   airflow.operators.bash     import BashOperator
from   airflow.operators.python   import PythonOperator



###################################################
############## EMAIL SENDER FUNCTION ##############

def send_report_email( PROJECT_PATH, DEPLOY_NOTEBOOK_PATH ):
    """
    Send an email with dag result (successful or failed) and loggings to the manager.
    
    Args:
        PROJECT_PATH: absolute path to the root folder of insiders project.
        DEPLOY_NOTEBOOK_PATH: relative path from the PROJECT_PATH 
            untill the  deployment jupyter notebook.

    Return:
        None
    """
    
    #########################
    ####### LIBRARIES #######
    import os
    import smtplib
    import os
    from   email.message    import EmailMessage


    ################################
    ######## CHECK LOGGINGS ########
    # create a list with log file names
    log_files = os.listdir(f'{PROJECT_PATH}/logs/')

    # sort list according to date of logs
    log_files.sort()

    # get the most recent log
    last_log_file = log_files[-1]

    # open the latest log file
    with open( f'{PROJECT_PATH}/logs/{last_log_file}', 'r') as log:
        # get last log content
        last_log_content = log.read()

    # open the latest log file
    with open( f'{PROJECT_PATH}/logs/{last_log_file}', 'r') as log:
        # get number of lines in log file
        log_n_lines = len( log.readlines() )

    # open deployment notebook
    with open( f'{DEPLOY_NOTEBOOK_PATH}', 'r') as deploy_notebook:       
        # get number of logs in the deployment notebook
        num_loggings = len( re.findall("logger\.[a-z]+\(.+\)", deploy_notebook.read() ) )


    ##########################################
    ####### LOAD ENVIRONMENT VARIABLES #######
    # emails & credentials
    EMAIL_SENDER_PSWD = os.environ.get( 'EMAIL_SENDER_PSWD' )
    EMAIL_SENDER_USER = os.environ.get( 'EMAIL_SENDER_USER' ),
    EMAIL_DESTINATION = os.environ.get( 'EMAIL_DEFAULT_RECEIVER' )

    ############################
    ####### EMAIL SENDER #######
    
    # instanciate email message constructor
    msg = EmailMessage()
    # set email sender
    msg['From'] = EMAIL_SENDER_USER[0]
    # set email destination
    msg['To'] = EMAIL_DESTINATION
    # set email body -> content of last log
    msg.set_content( last_log_content )


    # check if pipelines was successful:
    # success = number of lines in logging file =
    # number of loggins in deployment notebook
    if log_n_lines == num_loggings:
        # set email subject
        msg['Subject'] = 'Insiders log: SUCCESSFUL'
    else: # in case of failure
        # set email subject
        msg['Subject'] = 'Insiders log: FAILED'


    # use context manager to send email    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        # login to email server
        smtp.login( EMAIL_SENDER_USER[0], EMAIL_SENDER_PSWD )
        # send email
        smtp.send_message(msg)

    
    return None



###########################
######## CONSTANTS ########

# project root folder
PROJECT_PATH = '/home/ubuntu/insiders-aws-deployment/insiders_project_deployment'
# get deployment notebook path
DEPLOY_NOTEBOOK_PATH = f"{PROJECT_PATH}/models/1.0-gcj-insiders-clustering-model.ipynb"



#########################################
############## AIRFLOW DAG ##############

# create a dag with context manager
with DAG(dag_id = "insiders_pipeline", 
        start_date = datetime(2021,12, 10),
        schedule_interval = "00 9 * * 1", # At 09:00 on Monday.
        catchup = False # don't wait schedule_interval after start date
        ) as dag:
        

    # task to run the data pipeline
    pipeline_operator = BashOperator(task_id = 'pipeline_operator',
        # the bash command below does the following:
        # makes papermill run the deploy notebook
        # save the output on another notebook with timestamp
        # -k parameter means what kernel papermill must use
        # -r parameter means the value of the papermmill tag variable
        bash_command = "papermill /home/ubuntu/insiders-aws-deployment/insiders_project_deployment/models/1.0-gcj-insiders-clustering-model.ipynb /home/ubuntu/insiders-aws-deployment/insiders_project_deployment/reports/1.0-gcj-deploy-$(date +'%Y-%m-%dT%H:%M:%S').ipynb -k insiders_project_deployment -r PROJECT_PATH /home/ubuntu/insiders-aws-deployment/insiders_project_deployment/"
        ) 


    # task to send a reporting email
    reporting_email =  PythonOperator(task_id = "reporting_email",
        python_callable = send_report_email, # call python function
        op_kwargs = {'PROJECT_PATH': PROJECT_PATH, 'DEPLOY_NOTEBOOK_PATH': DEPLOY_NOTEBOOK_PATH}, # callable args
        trigger_rule = "all_done" # send email regardless of upstream success/fail
        )
    

    # define workflow
    pipeline_operator >> reporting_email

