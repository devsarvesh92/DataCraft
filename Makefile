install:
	pdm install --no-self

run:
	export AWS_PROFILE=aws_private
	export AWS_REGION=us-east-1
	export AWS_DEFUALT_REGION=us-east-1
	streamlit run app.py
