# Docker Setup for Snowflake Query Optimizer

## Quick Start

### 1. Install Docker Desktop
- Go to: https://www.docker.com/products/docker-desktop/
- Download and install
- Start Docker Desktop

### 2. Run the Application

#### Option A: Using docker-compose (Easiest)
```bash
# Set your credentials in .env file first
# Then run:
docker-compose up

# In another terminal, run commands:
docker-compose exec snowflake-optimizer python main.py analyze
docker-compose exec snowflake-optimizer python main.py chat
```

#### Option B: Using Docker directly
```bash
# Build image
docker build -t snowflake-optimizer .

# Run health check
docker run --env-file .env snowflake-optimizer python main.py health-check

# Run analysis
docker run --env-file .env snowflake-optimizer python main.py analyze

# Interactive chat
docker run -it --env-file .env snowflake-optimizer python main.py chat
```

### 3. Environment Variables
Create `.env` file with your credentials (already done):
```
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
ANTHROPIC_API_KEY=your_api_key
```

## Common Commands

```bash
# Health check
docker-compose run snowflake-optimizer python main.py health-check

# Full analysis
docker-compose run snowflake-optimizer python main.py analyze

# Cost report
docker-compose run snowflake-optimizer python main.py cost-report

# Query insights
docker-compose run snowflake-optimizer python main.py query-insights

# Schema check
docker-compose run snowflake-optimizer python main.py schema-check

# Workload analysis
docker-compose run snowflake-optimizer python main.py workload-analysis

# Interactive chat (use -it flags for input)
docker-compose run -it snowflake-optimizer python main.py chat
```

## Troubleshooting

### "Docker command not found"
- Install Docker Desktop
- Restart terminal after installation

### "Cannot connect to Docker daemon"
- Start Docker Desktop application

### "Port already in use"
- Another container is running
- Run: `docker-compose down`

### "Permission denied"
- On Linux: `sudo usermod -aG docker $USER`
- Then logout and login again

## Advantages of Docker

✅ No Python version issues
✅ No AppStore restrictions
✅ Isolated environment
✅ Works on Windows, Mac, Linux
✅ Easy to deploy to cloud
✅ No local dependencies

## Behind the Scenes

The Dockerfile:
1. Uses official Python 3.11 image (no AppStore restrictions)
2. Installs all dependencies from requirements.txt
3. Copies your code
4. Ready to run

## Next Steps

1. Install Docker Desktop from https://www.docker.com/products/docker-desktop/
2. Start Docker Desktop
3. Open PowerShell in your project directory
4. Run: `docker-compose up`
5. In another terminal: `docker-compose exec snowflake-optimizer python main.py health-check`

Done! 🎉
