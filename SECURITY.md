# 🔐 Security Guidelines

## Credential Management

### Local Development

1. **Never commit `.env` to git**
   ```bash
   # ✅ GOOD - .env is in .gitignore
   echo ".env" >> .gitignore
   git add .gitignore
   
   # ❌ NEVER do this
   git add .env
   git commit -m "Add credentials"
   ```

2. **Use `.env.example` as template**
   ```bash
   cp .env.example .env
   # Edit .env with YOUR credentials
   ```

3. **Verify before committing**
   ```bash
   # Check for accidentally staged credentials
   git diff --cached | grep -i "password\|api_key\|token"
   
   # Safe to commit if no output above
   ```

### Production Deployment

#### Option 1: Azure Key Vault (Recommended)
```bash
# Store secrets in Azure Key Vault
az keyvault secret set --vault-name MyKeyVault \
  --name snowflake-password --value "your_password"

# Reference in Azure Function
os.environ['SNOWFLAKE_PASSWORD'] = client.get_secret('snowflake-password').value
```

#### Option 2: Snowflake Key-Pair Authentication (Recommended for Snowflake)
```python
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Generate keypair (do this once, store private key securely)
# openssl genrsa 3072 > private_key.pem
# openssl req -new -x509 -key private_key.pem -out public_key.pem -days 365

with open('/secure/location/private_key.pem', 'rb') as f:
    private_key = serialization.load_pem_private_key(
        f.read(),
        password=None,
        backend=default_backend()
    )

connector = snowflake.connector.connect(
    account='your_account',
    user='your_user',
    private_key=private_key
)
```

#### Option 3: Environment Variables (CI/CD)
```yaml
# GitHub Actions example
- name: Run Snowflake Analysis
  env:
    SNOWFLAKE_PASSWORD: ${{ secrets.SNOWFLAKE_PASSWORD }}
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  run: python main.py analyze
```

## API Key Security

### Anthropic API Key
- Store in `.env` locally (not committed)
- Use environment variables in production
- Rotate keys periodically
- Never log or print API keys

```python
# ✅ GOOD
api_key = os.getenv('ANTHROPIC_API_KEY')

# ❌ NEVER do this
print(f"API Key: {api_key}")
logger.info(f"Using key: {api_key}")
```

## Database Permissions

### Snowflake Account Setup
```sql
-- Create service account with minimal permissions
CREATE USER optimizer_svc PASSWORD = 'secure_password';

-- Grant only required roles
GRANT ROLE ANALYZER TO USER optimizer_svc;

-- Or create custom role with limited access
CREATE ROLE ANALYZER;
GRANT SELECT ON DATABASE governance TO ROLE ANALYZER;
GRANT USAGE ON WAREHOUSE compute_wh TO ROLE ANALYZER;
GRANT ROLE ANALYZER TO USER optimizer_svc;
```

**Note:** QUERY_HISTORY access requires ACCOUNTADMIN role

## Incident Response

### If Credentials Are Exposed

1. **Immediately revoke access**
   ```sql
   -- Snowflake
   ALTER USER wondi DISABLE;
   
   -- Anthropic
   -- Delete the exposed key in Anthropic console
   ```

2. **Generate new credentials**
   ```bash
   # Update in .env
   SNOWFLAKE_PASSWORD=new_secure_password
   ANTHROPIC_API_KEY=sk-ant-...new_key
   ```

3. **Audit logs**
   ```sql
   -- Check query history
   SELECT * FROM snowflake.account_usage.query_history
   WHERE user_name = 'wondi'
   ORDER BY start_time DESC
   LIMIT 100;
   ```

4. **Update everywhere**
   - Local `.env`
   - CI/CD secrets
   - Azure Key Vault
   - Any other systems

## Security Checklist

- [ ] Never commit `.env` file
- [ ] Use `.env.example` for templates
- [ ] No credentials in code comments
- [ ] No credentials in git history
- [ ] No credentials in logs (DEBUG mode)
- [ ] Use strong passwords (20+ chars, mixed case, numbers, symbols)
- [ ] Rotate keys every 90 days
- [ ] Use key-pair auth for production Snowflake
- [ ] Store secrets in Key Vault for Azure deployment
- [ ] Audit access logs regularly
- [ ] Use separate users per environment

## Testing Security

```bash
# Check for exposed credentials in git
git log --all -S "password" --oneline
git log --all -S "api_key" --oneline

# Check for hardcoded secrets
grep -r "password\|api_key\|secret" --include="*.py" . | grep -v ".env"

# Scan dependencies for vulnerabilities
pip install safety
safety check
```

## Resources

- [Snowflake Security Best Practices](https://docs.snowflake.com/en/user-guide/security.html)
- [Anthropic API Security](https://docs.anthropic.com/docs/basics/api-security)
- [OWASP Credential Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [Azure Key Vault Integration](https://learn.microsoft.com/en-us/azure/key-vault/)

---

**Last Updated:** 2026-11-27  
**Maintained by:** Security Team
