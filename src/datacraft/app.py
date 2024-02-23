import logging
import time
import uuid
from typing import Any
from botocore.config import Config
from botocore.response import StreamingBody
import boto3
import pandas as pd
import streamlit as st


def process_response(result_df: pd.DataFrame) -> pd.DataFrame | str:
    if result_df.empty:
        return "No data found for the given query"
    else:
        return result_df


def process_user_query(input_string: str) -> pd.DataFrame:
    logging.log(logging.INFO, f"Processing user query: {input_string}")

    result_df = identify_schema()

    return process_response(result_df=result_df)


def identify_schema() -> pd.DataFrame:
    # using model identify schema
    return build_query(text_input="")


def build_query(text_input: str) -> pd.DataFrame:
    query_string = "select * from payments_db.payments;"
    return execute_query_on_athena(query_string=query_string, database_name="payments_db")


def stream_content(
        *, s3_client: "botocore.client.S3", bucket: str, key: str
) -> StreamingBody:
    return s3_client.get_object(Bucket=bucket, Key=key)["Body"]


def download_report(file_path: str, s3_key: str, s3_bucket: str) -> pd.DataFrame:
    # s3 object
    s3_client: "botocore.client.s3" = boto3.client("s3")

    # download report from s3
    logging.log(logging.INFO, f"Downloading report from s3: {s3_key} {s3_bucket} {file_path}")

    # Download and write content
    with open(file_path, "wb") as fh:
        for chunk in stream_content(s3_client=s3_client, bucket=s3_bucket, key=s3_key):
            fh.write(chunk)

    return pd.read_csv(file_path)


def execute_query_on_athena(query_string: str, database_name: str) -> pd.DataFrame:
    # execute query on aws athena
    report_id = str(uuid.uuid4())
    s3_path: str = f"s3://test-query-ouput-athena/query_result/{report_id}"

    athena_client = boto3.client("athena", config=Config(
        retries={
            "max_attempts": 10,
            "mode": "adaptive",
        }))

    response: dict[str, Any] = athena_client.start_query_execution(
        QueryString=query_string,
        ClientRequestToken=report_id,
        QueryExecutionContext={
            "Database": database_name,
        },
        ResultConfiguration={
            "OutputLocation": s3_path,
        },
        WorkGroup="primary",
    )

    query_execution_id: str = response["QueryExecutionId"]

    # wait for query to complete
    time.sleep(1)

    df = pd.DataFrame()
    try:
        df = download_report(
            file_path=f"/tmp/{report_id}.csv",
            s3_key=f"query_result/{report_id}/{query_execution_id}.csv",
            s3_bucket="test-query-ouput-athena")
    except Exception as e:
        with st.chat_message("bot"):
            st.write("Sorry, can you please try again ?")
    return df


st.set_page_config(
    page_title="DataCraft",
    layout="wide"
)
st.title("DataCraft")

if 'user_messages' not in st.session_state:
    st.session_state['user_messages'] = []

if 'bot_messages' not in st.session_state:
    st.session_state['bot_messages'] = []

user_input = st.chat_input(placeholder='How can I help you?')

if user_input:
    st.session_state['user_messages'].append(user_input)


    st.session_state['bot_messages'].append("thinking...")

    for user_message, bot_message in zip(st.session_state.user_messages, st.session_state.bot_messages):
        with st.chat_message("user"):
            st.write(user_message)

        with st.chat_message("bot"):
            st.write(bot_message)

    bot_response = process_user_query(input_string=user_input)

    with st.chat_message("bot"):
        st.write(bot_response)
