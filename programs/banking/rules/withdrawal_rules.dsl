rule:
  name: "Withdrawal-Specific Rules"
  description: "Local rules specific to withdrawal processing"

variables:
  - name: "DAILY-LIMIT"
    type: "NUMERIC"
    pic: "9(8)V99"
    description: "Daily withdrawal limit"
    value: "5000.00"
  - name: "DAILY-TOTAL"
    type: "NUMERIC"
    pic: "9(8)V99"
    description: "Daily withdrawal total"
    value: "0.00"

conditions:
  daily_limit_check:
    check: "DAILY-TOTAL + TRANSACTION-AMOUNT <= DAILY-LIMIT"
    description: "Check daily withdrawal limit"

requirements:
  daily_limit_validation:
    description: "Daily withdrawal limit must not be exceeded"
    check: "DAILY-TOTAL + TRANSACTION-AMOUNT <= DAILY-LIMIT"
    violation_message: "Daily withdrawal limit exceeded"
    severity: "HIGH"
  
  large_transaction_approval:
    description: "Large transactions require additional approval"
    check: "TRANSACTION-AMOUNT > 1000 IMPLIES APPROVAL-PRESENT"
    violation_message: "Large transaction requires approval"
    severity: "MEDIUM"

compliant_logic:
  - "Check daily withdrawal limits"
  - "Validate large transaction approvals"
  - "Update daily totals"
  - "Log all withdrawal attempts"

violation_examples:
  daily_limit_exceeded:
    description: "Daily limit check missing"
    code: |
      SUBTRACT TRANSACTION-AMOUNT FROM ACCOUNT-BALANCE
      * Missing daily limit check
    violation_type: "Daily limit validation missing"
    severity: "HIGH"
  
  large_transaction_no_approval:
    description: "Large transaction without approval"
    code: |
      IF TRANSACTION-AMOUNT > 1000
          * Process large transaction without approval check
      END-IF
    violation_type: "Large transaction approval missing"
    severity: "MEDIUM"
