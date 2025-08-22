@echo off
echo Starting ChainPilot Trading Assistant API on http://localhost:8082
cd /d %~dp0
python -m uvicorn api_gateway_agent:fastapi_app --host 0.0.0.0 --port 8082 --reload
