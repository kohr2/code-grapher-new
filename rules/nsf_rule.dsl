rule:
  name: "NSF Banking Rule"
  description: "NSF events must be logged and fee applied before rejection"
  
variables:
  - name: "ACCOUNT-BALANCE"
    type: "numeric"
    pic: "9(8)V99"
    description: "Current account balance"
  
  - name: "WITHDRAWAL-AMOUNT"
    type: "numeric"
    pic: "9(8)V99"
    description: "Amount to withdraw"
  
  - name: "NSF-FEE"
    type: "numeric"
    pic: "9(2)V99"
    value: "35.00"
    description: "NSF fee amount"
  
  - name: "NSF-LOG-FLAG"
    type: "flag"
    pic: "X(1)"
    default: "N"
    description: "Flag to track NSF logging"

conditions:
  insufficient_funds:
    check: "ACCOUNT-BALANCE < WITHDRAWAL-AMOUNT"
    description: "Check if account has sufficient funds"

requirements:
  nsf_logging:
    description: "NSF events must be logged"
    check: "NSF-LOG-FLAG variable must be defined"
    violation_message: "NSF-LOG-FLAG variable not defined"
    severity: "HIGH"
  
  nsf_fee_application:
    description: "NSF fee must be applied to withdrawal amount"
    check: "ADD NSF-FEE TO WITHDRAWAL-AMOUNT must be present"
    violation_message: "NSF fee not added to withdrawal amount"
    severity: "HIGH"
  
  nsf_event_logging:
    description: "NSF event must be logged to system"
    check: "NSF Event Logged message must be displayed"
    violation_message: "NSF event not logged to system"
    severity: "MEDIUM"

compliant_logic:
  when_insufficient_funds:
    - "MOVE 'Y' TO NSF-LOG-FLAG"
    - "ADD NSF-FEE TO WITHDRAWAL-AMOUNT"
    - "DISPLAY 'NSF Event Logged - Fee Applied'"
    - "PERFORM REJECT-TRANSACTION"

violation_examples:
  missing_log_flag:
    description: "NSF-LOG-FLAG variable missing"
    remove_variables: ["NSF-LOG-FLAG"]
  
  missing_fee_application:
    description: "NSF fee not applied"
    remove_logic: ["ADD NSF-FEE TO WITHDRAWAL-AMOUNT"]
  
  missing_event_logging:
    description: "NSF event not logged"
    replace_logic:
      "DISPLAY 'NSF Event Logged - Fee Applied'": "DISPLAY 'Insufficient Funds - Transaction Rejected'"