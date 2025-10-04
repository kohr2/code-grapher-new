rule:
  name: "Global Fraud Management Compliance Rule"
  description: "Global fraud management standards and regulatory compliance requirements"
  domain: "fraud_management"
  version: "1.0"
  effective_date: "2025-01-01"

variables:
  - name: "FRAUD-DETECTION-SYSTEM"
    description: "Fraud detection system identifier"
    type: "alphanumeric"
    pic: "X(20)"
    required: true
    validation: "must be properly configured and operational"
    
  - name: "FRAUD-LOG-RECORD"
    description: "Fraud decision log record"
    type: "record"
    pic: "400 CHARACTERS"
    required: true
    validation: "must contain complete audit trail"
    
  - name: "FRAUD-TIMESTAMP"
    description: "Timestamp of fraud decision"
    type: "timestamp"
    pic: "X(20)"
    required: true
    validation: "must be current system timestamp"
    
  - name: "FRAUD-REASON-CODE"
    description: "Reason code for fraud decision"
    type: "alphanumeric"
    pic: "X(10)"
    required: true
    validation: "must be valid fraud reason code"
    
  - name: "FRAUD-ACTION-TAKEN"
    description: "Action taken based on fraud decision"
    type: "alphanumeric"
    pic: "X(20)"
    required: true
    validation: "must be valid fraud action code"
    
  - name: "FRAUD-RESOLUTION"
    description: "Resolution status of fraud case"
    type: "alphanumeric"
    pic: "X(100)"
    required: true
    validation: "must be valid resolution status"

requirements:
  - name: "fraud_system_availability"
    description: "Fraud detection system must be available and operational"
    priority: "critical"
    check: "FRAUD-DETECTION-SYSTEM must be operational 24/7"
    
  - name: "fraud_logging_standards"
    description: "All fraud decisions must be logged with standard format"
    priority: "critical"
    check: "FRAUD-LOG-RECORD must contain all required fields"
    
  - name: "audit_trail_integrity"
    description: "Audit trail must be complete and tamper-evident"
    priority: "critical"
    check: "FRAUD-TIMESTAMP must be system-generated and immutable"
    
  - name: "fraud_reason_coding"
    description: "Fraud reasons must use standardized coding system"
    priority: "high"
    check: "FRAUD-REASON-CODE must follow regulatory standards"
    
  - name: "action_tracking"
    description: "All fraud actions must be tracked and documented"
    priority: "high"
    check: "FRAUD-ACTION-TAKEN must be recorded for all decisions"
    
  - name: "case_resolution_tracking"
    description: "Fraud cases must be tracked through resolution"
    priority: "high"
    check: "FRAUD-RESOLUTION must be updated throughout case lifecycle"
    
  - name: "regulatory_reporting"
    description: "Fraud data must support regulatory reporting requirements"
    priority: "critical"
    check: "All fraud data must be available for regulatory reports"
    
  - name: "data_retention_compliance"
    description: "Fraud data must be retained per regulatory requirements"
    priority: "high"
    check: "Fraud logs must be retained for minimum regulatory period"
    
  - name: "privacy_protection"
    description: "Customer privacy must be protected in fraud data"
    priority: "critical"
    check: "PII must be properly protected in fraud logs"
    
  - name: "incident_response"
    description: "Fraud incidents must trigger proper response procedures"
    priority: "critical"
    check: "High-risk fraud must trigger incident response protocols"

conditions:
  - name: "system_reliability"
    description: "Fraud detection system must maintain high reliability"
    check: "System uptime must be >= 99.9%"
    severity: "critical"
    
  - name: "response_time_requirements"
    description: "Fraud decisions must be made within required timeframes"
    check: "Fraud decisions must be made within 2 seconds"
    severity: "high"
    
  - name: "accuracy_standards"
    description: "Fraud detection must meet accuracy standards"
    check: "False positive rate must be <= 1%"
    severity: "high"
    
  - name: "regulatory_compliance"
    description: "System must comply with all applicable regulations"
    check: "Must comply with PCI-DSS, SOX, and other relevant regulations"
    severity: "critical"
    
  - name: "data_security"
    description: "Fraud data must be secured according to standards"
    check: "Data must be encrypted at rest and in transit"
    severity: "critical"

compliant_logic:
  description: "Global fraud management compliance includes system reliability, regulatory compliance, audit trails, and incident response"
  
  implementation:
    - "Maintain fraud detection system with 99.9% uptime"
    - "Log all fraud decisions with complete audit trail"
    - "Use standardized fraud reason and action codes"
    - "Track fraud cases through complete lifecycle"
    - "Support regulatory reporting requirements"
    - "Protect customer privacy and PII data"
    - "Implement incident response procedures"
    - "Ensure data retention compliance"

violation_examples:
  - type: "system_downtime"
    description: "Fraud detection system unavailable"
    code: |
      * VIOLATION: System downtime
      * Fraud detection system not operational
      * Should maintain 99.9% uptime requirement
    severity: "critical"
    
  - type: "incomplete_audit_trail"
    description: "Fraud decisions not properly logged"
    code: |
      * VIOLATION: Incomplete audit trail
      IF WS-FRAUD-DETECTED = 'Y'
        MOVE 'DECLINE' TO FRAUD-ACTION-TAKEN
        * Missing: Complete fraud log record with timestamp and reason
      END-IF
    severity: "critical"
    
  - type: "non_standard_reason_codes"
    description: "Fraud reason codes not following standards"
    code: |
      * VIOLATION: Non-standard reason codes
      MOVE 'BIG_AMOUNT' TO FRAUD-REASON-CODE
      * Should use: 'FRAUD_DETECTED' or other standard codes
    severity: "high"
    
  - type: "missing_privacy_protection"
    description: "Customer PII not properly protected in fraud logs"
    code: |
      * VIOLATION: PII exposure
      MOVE TRANS-CARD-NUMBER TO FRAUD-LOG-RECORD
      * Should mask or encrypt sensitive customer data
    severity: "critical"
    
  - type: "no_incident_response"
    description: "High-risk fraud not triggering incident response"
    code: |
      * VIOLATION: No incident response
      IF WS-TOTAL-RISK-SCORE >= 900
        MOVE 'Y' TO WS-FRAUD-DETECTED
        * Missing: Incident response procedures
      END-IF
    severity: "critical"
    
  - type: "data_retention_violation"
    description: "Fraud data not retained per regulatory requirements"
    code: |
      * VIOLATION: Data retention violation
      DELETE FRAUD-LOG-RECORD
      * Should retain for regulatory compliance period
    severity: "high"
