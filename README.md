# AWS Serverless Project

Serverless microservices built on AWS using Python. This repository contains Lambda functions, infrastructure as code (IaC) templates, tests, and helper scripts to build, run, and deploy a serverless application (API endpoints, event processors, background jobs) using AWS services such as Lambda, API Gateway, DynamoDB, S3, SNS/SQS, and CloudWatch.

Languages: Python (primary).  
Repository owner: Skull1zues

Table of contents
- [Project overview](#project-overview)
- [Architecture](#architecture)
- [Features](#features)
- [Repository layout](#repository-layout)
- [Prerequisites](#prerequisites)
- [Local development](#local-development)
- [Testing](#testing)
- [Packaging & dependencies](#packaging--dependencies)
- [Deployment](#deployment)
  - [AWS SAM](#aws-sam)
  - [Serverless Framework](#serverless-framework)
  - [AWS CDK (optional)](#aws-cdk-optional)
- [AWS resources used](#aws-resources-used)
- [Configuration & secrets](#configuration--secrets)
- [Observability & monitoring](#observability--monitoring)
- [CI / CD recommendations](#ci--cd-recommendations)
- [Security considerations](#security-considerations)
- [Contributing](#contributing)
- [License & contact](#license--contact)

Project overview
This repo is a reference implementation of an AWS serverless application in Python. It demonstrates best practices for:
- Organizing Lambda handlers and shared libraries
- Local development and testing with SAM/LocalStack
- Packaging dependencies and using Lambda layers
- Deploying via IaC (SAM, Serverless Framework, or CDK)
- Observability with CloudWatch logs and metrics

Architecture
Typical components:
- HTTP API (API Gateway) that routes requests to Lambda handlers
- Lambda functions for business logic, scheduled tasks, or event processing
- DynamoDB for primary storage (or RDS for relational use-cases)
- S3 for file storage / static assets
- SNS / SQS for event-driven workflows
- IAM roles scoped to least privilege
- Optional Lambda Layers for shared dependencies

Features
- Python-based Lambda handlers organized by domain
- IaC templates for reproducible deployments
- Local invocation and API emulation (SAM / LocalStack)
- Unit and integration tests (pytest, moto)
- Example CI configuration and deployment instructions
- Examples for packaging compiled dependencies with Docker

Repository layout (example)
- src/
  - service_a/
    - handler.py
    - requirements.txt
    - models.py
    - service_a_logic.py
  - common/
    - utils.py
    - validators.py
- templates/
  - template.yaml           # AWS SAM or CloudFormation
  - serverless.yml          # Serverless Framework config (optional)
- layers/
  - common_layer/           # example Lambda layer
- tests/
  - unit/
  - integration/
- scripts/
  - build_layer.sh
  - package.sh
- docker/                   # docker-compose for LocalStack or test env
- README.md
- requirements.txt

Prerequisites
- Python 3.8+ (3.10/3.11 recommended)
- pip
- AWS CLI configured (aws configure) with deploy credentials
- Docker (required for SAM build with dependencies and for LocalStack)
- AWS SAM CLI (if using SAM)
- Serverless Framework CLI (optional)
- Node.js & npm (required for Serverless Framework, optional)
- (Optional) AWS CDK (if using CDK)

Local development

1. Create a virtual environment and install dev dependencies:
```bash
python -m venv .venv
source .venv/bin/activate    # macOS / Linux
.venv\Scripts\activate       # Windows PowerShell

pip install -r requirements-dev.txt
```

2. Run unit tests:
```bash
pytest tests/unit
```

3. Run a single Lambda locally with SAM:
```bash
# from repo root
sam build
sam local invoke FunctionLogicalID --event events/sample_event.json
# or run the API locally
sam local start-api
```

4. Use LocalStack for integration tests that interact with AWS resources locally:
```bash
# using docker-compose/localstack config
docker-compose up -d localstack
# run tests with endpoint overrides (or using moto)
pytest tests/integration --aws-endpoint-url=http://localhost:4566
```

Testing
- Unit tests: pytest, with moto for mocking AWS services
- Integration tests: use LocalStack or test AWS account with isolated resources (prefer test account)
- Fixtures: keep test data small and deterministic
- Example test command:
```bash
pytest -q --maxfail=1
```

Example pytest and moto usage:
```python
from moto import mock_dynamodb2
import boto3

@mock_dynamodb2
def test_write_item():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    # create table and run assertions...
```

Packaging & dependencies
- Keep per-function requirements.txt for smaller deployment packages.
- Use Lambda Layers for shared dependencies (common libraries, compiled wheels).
- Build compiled dependencies using Docker (manylinux) to ensure compatibility:
```bash
# example build for layer
./scripts/build_layer.sh src/common/requirements.txt layers/common_layer
```
- For large packages, consider storing wheels or using ECR for container-based Lambdas.

Deployment

AWS SAM
1. Build:
```bash
sam build
```
2. Deploy (guided the first time):
```bash
sam deploy --guided
```
3. Re-deploy:
```bash
sam deploy --stack-name my-serverless-app --capabilities CAPABILITY_IAM
```

Serverless Framework (optional)
1. Install:
```bash
npm install -g serverless
```
2. Deploy:
```bash
sls deploy --stage dev
```

AWS CDK (optional)
- If using CDK, synth and deploy:
```bash
cdk synth
cdk deploy
```

Notes:
- Use separate AWS accounts / stages for dev, staging, prod.
- Use parameterized stacks and CI secrets for non-interactive deploys.

AWS resources used (examples)
- AWS Lambda (Python runtime)
- Amazon API Gateway (HTTP API or REST API)
- Amazon DynamoDB (NoSQL)
- Amazon S3 (object storage)
- Amazon SNS / SQS (notifications and queues)
- Amazon EventBridge (scheduler or event bus)
- CloudWatch Logs / Metrics / Alarms
- AWS Systems Manager Parameter Store or Secrets Manager for secrets
- IAM Roles with least privilege for each function

Configuration & secrets
- Do not hardcode secrets in code or checked-in files.
- Recommended approaches:
  - Use AWS Systems Manager Parameter Store or Secrets Manager
  - Use environment variables injected by the deployment template
  - For local dev, use a .env file loaded by tools like python-dotenv (do NOT commit .env)

Example environment variables (set in template or CI):
- TABLE_NAME
- BUCKET_NAME
- JWT_SECRET
- STAGE (dev|staging|prod)
- AWS_REGION

Observability & monitoring
- CloudWatch Logs: ensure structured logs (JSON) for easy parsing
- CloudWatch Metrics & Alarms: error rate, throttles, duration
- X-Ray: enable tracing for distributed tracing across services
- Log retention: configure appropriate retention policies for logs

Security considerations
- Principle of least privilege in IAM policies
- Avoid embedding secrets in code or Git
- Use AWS KMS to encrypt sensitive data at rest if required
- Validate and sanitize inputs in Lambda handlers
- Rate-limit and protect public API endpoints with API Gateway usage plans or WAF

CI / CD recommendations
- Use GitHub Actions / AWS CodePipeline / GitLab CI
- Pipeline steps:
  - Lint and unit tests
  - Build artifacts (sam build / pip wheel / layer packaging)
  - Run integration tests in an isolated account (or LocalStack in CI)
  - Deploy to dev/staging via non-interactive sam deploy / serverless deploy
  - Manual approval step before production deploy
- Securely store AWS credentials in secrets manager (GitHub Secrets, AWS Secrets Manager)

Linting & formatting
- Black for formatting:
```bash
black .
```
- Flake8 for linting:
```bash
flake8 src tests
```
- isort for imports:
```bash
isort .
```

Troubleshooting
- Cold starts: reduce package size, use provisioned concurrency for critical functions
- Missing native libs: build wheels on Amazon Linux (use Docker manylinux images)
- Permission denied errors: check IAM role resource ARNs and correct policy scoping
- Environment mismatches: confirm runtime and dependency versions match Lambda runtime

Contributing
1. Fork the repo
2. Create a feature branch: git checkout -b feat/your-feature
3. Run tests and linters locally
4. Push branch and open a Pull Request with a clear description and test coverage
5. Maintain small, focused PRs and document design decisions

License & contact
- Add a LICENSE file to the repository (MIT / Apache-2.0 recommended).
- Maintainer: Skull1zues
- Repo: https://github.com/Skull1zues/AWS_Serverless_Project

If you want a tailored README with exact commands that match this repository's structure (e.g., exact function names, template.yaml entries, or CI pipeline files), tell me whether you use SAM, Serverless Framework, or CDK and confirm the layout (for example, which top-level directories contain handlers). I can then update the README to include specific deploy commands, CloudFormation outputs, and example invocation snippets.
