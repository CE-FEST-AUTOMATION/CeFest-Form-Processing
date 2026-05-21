import azure.functions as func
import logging
import json
import urllib.request
import pandas as pd

# Create the FunctionApp instance used by the Functions host
app = func.FunctionApp()


#endpoint for uploading 
ENDPOINT = "https://inpro-participants-submit-3avzbu5vaa-as.a.run.app"

last_read = None

def process_row(row: pd.DataFrame) -> None:
    #logging.info("Processing row: %s", row.to_dict(orient="records")[0])
    print(row)



@app.timer_trigger(schedule="0 */1 * * * *", #runs every minute
                   arg_name="myTimer", # parameter name Azure injects into function
                   run_on_startup=False,
                   use_monitor=False) 
def check_forms(myTimer: func.TimerRequest) -> None:
    global last_read
    # logging.info("Python timer trigger function executed.")
    if myTimer.past_due: # for tracking if the timer is due on time  
        logging.info("The timer is past due.")

    df = pd.read_excel("C:\\Users\\xuan2\\Downloads\\responses.xlsx")
    read = df.tail(1)
    if last_read is None or not read.equals(last_read):
        process_row(read)
        last_read = read.copy()


def upload_data(payload : dict): #function to upload data onto firebase
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        ENDPOINT,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode()
            print(f"Status: {resp.status}")
            print(f"Response: {body}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"Status: {e.code}")
        print(f"Error: {body}")
