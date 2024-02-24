import logging
import time
import uuid
from typing import Any
from botocore.config import Config
from botocore.response import StreamingBody
import boto3
import pandas as pd
import streamlit as st

from src.ai.predict import get_datasource, get_query

keywords = ['hi', 'hello', 'hey', 'howdy', 'ok', 'fine', 'greetings', 'good morning', 'good afternoon', 'good evening',
            'bye']


def process_response(result_df: pd.DataFrame) -> pd.DataFrame | str:
    if result_df.empty:
        return "No data found"
    else:
        return result_df


def process_user_query(input_string: str) -> pd.DataFrame | str:
    if input_string.lower() in keywords:
        st.session_state["messages"].pop(-1)
        raise Exception()

    data_sources = get_datasource(query=input_string)
    kb = {
        "payments": ["payment_id", "report_date", "amount", "payment_type", "account_id", "tenant"],
        "accounts": ["account_id", "tenant", 'city', 'state'],
        "transactions": ["amount", "account_id", "tenant", "report_date", "type"],
    }
    data_store = [
        {"database": f"{db.strip()}_db", "table": db.strip(), "columns": kb[db.strip()]}
        for db in data_sources.split(",")
    ]

    query_string = get_query(datastore=data_store, question=input_string)
    # st.write(query_string)

    df = execute_query_on_athena(
        query_string=query_string,
        database_name="payments_db",
    )

    return process_response(df)


def stream_content(
        *, s3_client: "botocore.client.S3", bucket: str, key: str
) -> StreamingBody:
    return s3_client.get_object(Bucket=bucket, Key=key)["Body"]


def download_report(file_path: str, s3_key: str, s3_bucket: str) -> pd.DataFrame:
    # s3 object
    s3_client: "botocore.client.s3" = boto3.client("s3")

    # download report from s3
    logging.log(
        logging.INFO, f"Downloading report from s3: {s3_key} {s3_bucket} {file_path}"
    )

    # Download and write content
    with open(file_path, "wb") as fh:
        for chunk in stream_content(s3_client=s3_client, bucket=s3_bucket, key=s3_key):
            fh.write(chunk)

    return pd.read_csv(file_path)


def execute_query_on_athena(query_string: str, database_name: str) -> pd.DataFrame:
    # execute query on aws athena
    report_id = str(uuid.uuid4())
    s3_path: str = f"s3://test-query-ouput-athena/query_result/{report_id}"

    athena_client = boto3.client(
        "athena",
        config=Config(
            retries={
                "max_attempts": 10,
                "mode": "adaptive",
            }
        ),
    )

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
            s3_bucket="test-query-ouput-athena",
        )
    except Exception as e:
        st.session_state["messages"].append({"bot": "Sorry, can you please try again ?"})
    return df


# main code starts here

st.set_page_config(page_title="DataCraft", layout="wide")
st.title("DataCraft")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{}]

with st.chat_message("bot"):
    st.write("I am DataCraft bot.")

user_input = st.chat_input(placeholder='How can I help you?')

if user_input:
    st.session_state['messages'].append({'user': user_input})
    st.session_state['messages'].append({'bot': "thinking..."})

    for message in st.session_state.messages:
        match message:
            case {'bot': _}:
                msg = message.get("bot")
                with st.chat_message("bot"):
                    if isinstance(msg, dict):
                        st.write(pd.DataFrame().from_dict(msg))
                    else:
                        st.write(msg)
            case {'user': _}:
                with st.chat_message("user"):
                    st.write(message.get("user"))

    st.session_state["messages"].pop(-1)

    # processing user_input
    try:
        bot_response = process_user_query(input_string=user_input)
        if isinstance(bot_response, pd.DataFrame):
            st.session_state['messages'].append({'bot': bot_response.to_dict()})
        else:
            st.session_state['messages'].append({'bot': bot_response})
    except Exception as e:
        bot_response = "Apologies, I didn't get you question. Can you please ask me question in different manner ?"
        st.session_state["messages"].append({"bot": bot_response})
    with st.chat_message("bot"):
        st.write(bot_response)
