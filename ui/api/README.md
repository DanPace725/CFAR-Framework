# CFAR Framework API

FastAPI-based REST API for the CFAR Framework, providing programmatic access to simulation control and data analysis.

## Features
- **Simulation Management**: Create, run, and monitor simulation jobs
- **Configuration Validation**: Validate simulation parameters before execution
- **Results Analysis**: Access and compare simulation results
- **Background Processing**: Non-blocking simulation execution
- **Interactive Documentation**: Auto-generated API docs with Swagger UI

## Quick Start
```bash
# From project root
python run_api.py
```

Then visit:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Core Endpoints
- `GET /` - API health check
- `GET /health` - Detailed health status
- `POST /simulations/` - Create new simulation job
- `GET /simulations/{job_id}` - Get job status
- `GET /simulations/{job_id}/result` - Get simulation results
- `GET /simulations/` - List all jobs
- `DELETE /simulations/{job_id}` - Delete job and results

### Configuration
- `GET /configs/default` - Get default configuration
- `POST /configs/validate` - Validate configuration

### Analysis
- `POST /analysis/compare` - Compare multiple simulation results

## Usage Examples

### Create Simulation
```bash
curl -X POST "http://localhost:8000/simulations/" \
  -H "Content-Type: application/json" \
  -d @config.json
```

### Check Job Status
```bash
curl "http://localhost:8000/simulations/{job_id}"
```

### Get Results
```bash
curl "http://localhost:8000/simulations/{job_id}/result"
```

## Integration
The API is designed for integration with:
- External monitoring systems
- Automated simulation pipelines
- Third-party analytics tools
- Custom web applications

## Development
```bash
# Run with auto-reload
uvicorn ui.api.main:app --reload --host 0.0.0.0 --port 8000
```
