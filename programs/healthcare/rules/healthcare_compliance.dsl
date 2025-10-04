rule:
  name: "Healthcare Compliance Rule"
  description: "HIPAA and healthcare-specific compliance requirements"

variables:
  - name: "PATIENT-ID"
    type: "ALPHANUMERIC"
    pic: "X(10)"
    description: "Unique patient identifier"
    value: "REQUIRED"
  - name: "PATIENT-NAME"
    type: "ALPHANUMERIC"
    pic: "X(50)"
    description: "Patient name"
    value: "REQUIRED"
  - name: "INSURANCE-ID"
    type: "ALPHANUMERIC"
    pic: "X(10)"
    description: "Insurance identifier"
    value: "REQUIRED"
  - name: "PHI-AUTHORIZED"
    type: "ALPHANUMERIC"
    pic: "X(1)"
    description: "PHI access authorization flag"
    value: "REQUIRED"

conditions:
  phi_authorization:
    check: "PHI-AUTHORIZED = 'Y'"
    description: "Check PHI authorization"

requirements:
  patient_id_validation:
    description: "Patient ID must be validated"
    check: "PATIENT-ID IS NOT EQUAL TO SPACES"
    violation_message: "Patient ID validation failed"
    severity: "HIGH"
  
  hipaa_compliance:
    description: "HIPAA authorization required for PHI access"
    check: "PHI-AUTHORIZED = 'Y'"
    violation_message: "HIPAA authorization required"
    severity: "HIGH"
  
  audit_logging:
    description: "All PHI access must be logged"
    check: "PHI-AUTHORIZED IMPLIES AUDIT-LOGGED"
    violation_message: "PHI access not properly logged"
    severity: "HIGH"

compliant_logic:
  - "Validate patient identifiers"
  - "Check HIPAA authorization"
  - "Log all PHI access"
  - "Verify insurance coverage"
  - "Maintain audit trail"

violation_examples:
  phi_access_unauthorized:
    description: "PHI accessed without authorization"
    code: |
      DISPLAY PATIENT-NAME
      * Missing HIPAA authorization check
    violation_type: "Unauthorized PHI access"
    severity: "HIGH"
  
  missing_audit_log:
    description: "PHI access not logged"
    code: |
      MOVE 'Y' TO PHI-AUTHORIZED
      * Missing audit logging
    violation_type: "Missing audit trail"
    severity: "HIGH"
