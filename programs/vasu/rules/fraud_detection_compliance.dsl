rule:
  name: "Fraud Detection Compliance Rule"
  description: "Essential fraud detection compliance requirements"

variables:
  - name: "WS-TOTAL-RISK-SCORE"
    type: "numeric"
    pic: "9(4)"
    description: "Total calculated risk score for transaction"
    
  - name: "FRAUD-LOG-RECORD"
    type: "record"
    pic: "400 CHARACTERS"
    description: "Fraud decision log record"
    
  - name: "RULE-01-TRIGGERED"
    type: "alphanumeric"
    pic: "X(1)"
    description: "High amount transaction rule trigger"

conditions:
  fraud_rule_execution_check:
    check: "All 10 fraud rules must be executed for each transaction"
    description: "Comprehensive fraud risk assessment must be performed"
    logic: "All fraud rules from 2610-RULE-HIGH-AMOUNT to 2695-RULE-CROSS-VALIDATION must be performed"

requirements:
  fraud_rule_execution:
    description: "All 10 fraud detection rules must be executed for each transaction"
    check: "All fraud rules from 2610-RULE-HIGH-AMOUNT to 2695-RULE-CROSS-VALIDATION must be performed"
    violation_message: "Fraud detection rules not fully executed"
    severity: "CRITICAL"

compliant_logic:
  fraud_detection_implementation:
    - "Execute all 10 fraud detection rules for each transaction"
    - "Calculate total risk score from all risk components"
    - "Log all fraud decisions with complete audit trail"

violation_examples:
  - description: "Transaction processed without proper risk score calculation"
    code: |
      * VIOLATION: Missing risk score calculation
      MOVE ZERO TO WS-TOTAL-RISK-SCORE
      * Should calculate: WS-TOTAL-RISK-SCORE = WS-TRANSACTION-RISK + WS-VELOCITY-RISK + WS-LOCATION-RISK + WS-MERCHANT-RISK + WS-BEHAVIORAL-RISK
      PERFORM 2800-DETERMINE-ACTION
      
  - description: "Fraud decisions not properly logged"
    code: |
      * VIOLATION: Missing fraud logging
      IF WS-TOTAL-RISK-SCORE >= HIGH-RISK-THRESHOLD
        MOVE 'Y' TO WS-FRAUD-DETECTED
        * Missing: PERFORM 3000-LOG-DECISION
      END-IF
      
  - description: "Not all fraud detection rules executed"
    code: |
      * VIOLATION: Incomplete rule execution
      PERFORM 2610-RULE-HIGH-AMOUNT
      PERFORM 2620-RULE-VELOCITY-CHECK
      * Missing: PERFORM 2630-RULE-LOCATION-VARIANCE, etc.