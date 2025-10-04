rule:
  name: "Banking Compliance Rule"
  description: "Enhanced banking-specific compliance requirements"

variables:
  - name: "ACCOUNT-NUMBER"
    type: "ALPHANUMERIC"
    pic: "X(10)"
    description: "Unique account identifier"
    value: "REQUIRED"
  - name: "ACCOUNT-BALANCE"
    type: "NUMERIC"
    pic: "9(8)V99"
    description: "Current account balance"
    value: "REQUIRED"
  - name: "TRANSACTION-AMOUNT"
    type: "NUMERIC"
    pic: "9(8)V99"
    description: "Transaction amount"
    value: "REQUIRED"
  - name: "NSF-FLAG"
    type: "ALPHANUMERIC"
    pic: "X(1)"
    description: "Non-sufficient funds flag"
    value: "REQUIRED"

conditions:
  nsf_condition:
    check: "NSF-FLAG = 'Y'"
    description: "Check if NSF occurred"

requirements:
  account_validation:
    description: "Account number must be validated"
    check: "ACCOUNT-NUMBER IS NOT EQUAL TO SPACES"
    violation_message: "Account number validation failed"
    severity: "HIGH"
  
  balance_check:
    description: "Account balance must be sufficient"
    check: "ACCOUNT-BALANCE >= TRANSACTION-AMOUNT"
    violation_message: "Insufficient funds detected"
    severity: "MEDIUM"
  
  nsf_logging:
    description: "NSF events must be logged"
    check: "NSF-OCCURRED IMPLIES LOGGING-PRESENT"
    violation_message: "NSF event not properly logged"
    severity: "HIGH"

compliant_logic:
  - "Validate account number format"
  - "Check account status (active/frozen)"
  - "Verify sufficient funds before withdrawal"
  - "Log all NSF occurrences"
  - "Apply NSF fees when applicable"
  - "Maintain audit trail"

violation_examples:
  nsf_not_logged:
    description: "NSF occurred but not logged"
    code: |
      IF ACCOUNT-BALANCE < TRANSACTION-AMOUNT
          MOVE 'Y' TO NSF-FLAG
          * Missing NSF logging here
      END-IF
    violation_type: "Missing NSF logging"
    severity: "HIGH"
  
  insufficient_funds_check:
    description: "Withdrawal processed without balance check"
    code: |
      SUBTRACT TRANSACTION-AMOUNT FROM ACCOUNT-BALANCE
      * Missing balance validation
    violation_type: "Insufficient funds validation missing"
    severity: "MEDIUM"
