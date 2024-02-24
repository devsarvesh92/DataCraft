# DataCraft
# Openai: https://chat.openai.com/share/327cfcb9-4c3d-4e10-900d-03c68beab5fb

Hackathon Project Summary: Intelligent Data Querying Tool

Objective: Develop a tool that leverages machine learning to facilitate smart data querying, enabling users to retrieve information efficiently without prior knowledge of data sources or databases.

Background:
In the current setup, various teams frequently request specific data sets from the reporting team. These requests, such as obtaining payment data for a particular month, often involve data scattered across multiple sources. 
The requesting teams typically lack direct access to these sources and have little to no knowledge of where or how to find the required data. Consequently, this creates a significant dependency on the engineering team to retrieve and compile the necessary information, leading to inefficiencies and delays.

Goal:
To streamline data access and improve productivity by providing a user-friendly interface for querying data, thereby enabling teams to obtain the information they need promptly and autonomously.

**Approach**

1. **Data Source Identification**: Utilize BERT (Bidirectional Encoder Representations from Transformers) to analyze historical query patterns and identify relevant data sources within the data lake.
   
2. **Contextual Schema Retrieval**: Once data sources are pinpointed by BERT, fetch their corresponding schemas from AWS Glue to understand the structure and relationships of the data.

3. **Intelligent Query Construction**: Combine the user's request with the context derived from BERT and the schema information from AWS Glue. This process will be facilitated by GPT-4, which helps in formulating a comprehensive query.

4. **Query Execution**: Dispatch the constructed query to AWS Athena for execution and retrieval of the desired results.

------------

Queries for demo:

group transactions amount by year for rocket tenant
payments made by rocket tenant
group transactions by year for rocket tenant
total check payments made by reliance
group tranasctions by year
group payments made by rocket tenant by year


