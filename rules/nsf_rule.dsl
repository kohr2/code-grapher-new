rule:
  name: "NSF Banking Rule"
  description: "NSF (Non-Sufficient Funds) processing rule for banking compliance"
  domain: "banking"
  version: "1.0"

variables:
  - name: "ACCOUNT-NUMBER"
    type: "numeric"
    pic: "9(10)"
    description: "Customer account number"
    required: true
  - name: "TRANSACTION-AMOUNT"
    type: "numeric"
    pic: "9(8)V99"
    description: "Transaction amount"
    required: true
  - name: "NSF-FLAG"
    type: "alphanumeric"
    pic: "X"
    description: "NSF flag indicator"
    required: true
  - name: "NSF-FEE"
    type: "numeric"
    pic: "9(5)V99"
    description: "NSF fee amount"
    required: true
  - name: "APPROVAL-CODE"
    type: "alphanumeric"
    pic: "X(10)"
    description: "Approval code for transaction"
    required: false

conditions:
  nsf_condition:
    description: "Check if account has sufficient funds"
    check: "TRANSACTION-AMOUNT > ACCOUNT-BALANCE"
    logic: "TRANSACTION-AMOUNT > ACCOUNT-BALANCE"
    action: "SET NSF-FLAG TO 'Y' AND CHARGE NSF-FEE"

requirements:
  nsf_processing_requirement:
    description: "NSF processing must include all required variables"
    check: "All NSF processing variables must be defined"
    violation_message: "Required NSF processing variable not defined"
    severity: "HIGH"
  nsf_fee_requirement:
    description: "NSF fee must be applied when NSF flag is set"
    check: "NSF fee logic must be implemented"
    violation_message: "NSF fee logic not properly implemented"
    severity: "MEDIUM"
  approval_requirement:
    description: "Approval code must be validated"
    check: "Approval code validation must be present"
    violation_message: "Approval code validation missing"
    severity: "MEDIUM"

compliant_logic:
  nsf_processing:
    - "IF TRANSACTION-AMOUNT > ACCOUNT-BALANCE"
    - "    MOVE 'Y' TO NSF-FLAG"
    - "    MOVE 25.00 TO NSF-FEE"
    - "    PERFORM CHARGE-NSF-FEE"
    - "END-IF"
  approval_validation:
    - "PERFORM VALIDATE-APPROVAL-CODE"
    - "IF APPROVAL-CODE = 'VALID'"
    - "    PERFORM PROCESS-TRANSACTION"
    - "END-IF"

violation_examples:
  missing_nsf_flag:
    description: "Missing NSF-FLAG variable"
    code: |
      IDENTIFICATION DIVISION.
      PROGRAM-ID. BAD-NSF-PROCESSING.
      DATA DIVISION.
      01 ACCOUNT-NUMBER PIC 9(10).
      01 TRANSACTION-AMOUNT PIC 9(8)V99.
      PROCEDURE DIVISION.
      MAIN-PROCEDURE.
          DISPLAY 'Processing transaction'.
      STOP RUN.
  missing_nsf_fee_logic:
    description: "Missing NSF fee logic"
    code: |
      IDENTIFICATION DIVISION.
      PROGRAM-ID. INCOMPLETE-NSF-PROCESSING.
      DATA DIVISION.
      01 ACCOUNT-NUMBER PIC 9(10).
      01 TRANSACTION-AMOUNT PIC 9(8)V99.
      01 NSF-FLAG PIC X.
      PROCEDURE DIVISION.
      MAIN-PROCEDURE.
          IF TRANSACTION-AMOUNT > ACCOUNT-BALANCE
              MOVE 'Y' TO NSF-FLAG
          END-IF.
      STOP RUN.
