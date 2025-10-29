
# Compliance & Security

## Privacy

- **No external API calls**: All processing is local
- **No data transmission**: Data never leaves your infrastructure
- **No logging of PHI**: Patient data not logged
- **Temporary file cleanup**: Automatic cleanup of temp files

## HIPAA Compliance

The system is designed for HIPAA-compliant deployment:

1. Deploy on-premises or in private cloud
2. Enable audit logging
3. Encrypt data at rest
4. Use HTTPS for API
5. Implement access controls

## Security Best Practices

1. Use API keys for authentication
2. Enable CORS restrictions
3. Set maximum upload sizes
4. Validate all inputs
5. Regular security audits

## Data Retention

Configure data retention:

```python
settings.retain_input_images = False  # Don't keep inputs
settings.audit_logging = True         # Log operations
```

## Standards Compliance

- HL7 FHIR R4
- DICOM Part 10
- SCP-ECG (EN 1064)
- WFDB/PhysioNet
- EDF+ (European Data Format)
