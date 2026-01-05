# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in this GitHub Action, please report it by:

1. **Do NOT open a public issue**
2. Send details to the repository owner via GitHub Security Advisories
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## Security Best Practices

When using this action:

1. **Never commit database credentials** - Always use GitHub Secrets for `database-url`
2. **Use environment protection** - Enable required reviewers for production deployments
3. **Enable dry-run first** - Always preview migrations before applying
4. **Pin action versions** - Use specific tags (e.g., `@v1.0.0`) instead of `@master`
5. **Review migration SQL** - Check dry-run output for unexpected operations
6. **Limit repository access** - Only grant necessary permissions

## Action Permissions

This action requires:
- Read access to repository code
- Write access to database (via provided credentials)

The action does NOT:
- Store or transmit credentials
- Make external API calls
- Modify repository contents
- Access other secrets

## Database Security

This action connects directly to your database using provided credentials:
- Credentials are passed via environment variables
- No data is logged or stored
- Connection uses standard database drivers (psycopg2, pymysql)
- All operations run in isolated Docker containers

## Updates

Security updates will be released as patch versions. Subscribe to repository releases for notifications.
