rule:
  name: "Dual Approval Rule"
  description: "Payments over $10,000 require dual approval"

variables:
  - name: "PAYMENT-AMOUNT"
    type: "numeric"
    pic: "9(8)V99"
    description: "Payment amount"
  
  - name: "APPROVER-ID"
    type: "text"
    pic: "X(10)"
    description: "First approver ID"
  
  - name: "APPROVER-2-ID"
    type: "text"
    pic: "X(10)"
    description: "Second approver ID"

conditions:
  high_value_payment:
    check: "PAYMENT-AMOUNT > 10000"
    description: "Check if payment exceeds threshold"

requirements:
  dual_approval_check:
    description: "Both approvers must be validated"
    check: "Both APPROVER-ID and APPROVER-2-ID must be checked"
    violation_message: "Second approver not validated"
    severity: "HIGH"

compliant_logic:
  when_high_value:
    - "IF APPROVER-ID NOT = SPACES"
    - "   IF APPROVER-2-ID NOT = SPACES"
    - "      PERFORM PROCESS-PAYMENT"
    - "   END-IF"
    - "END-IF"

violation_examples:
  missing_second_approver:
    description: "Second approver check missing"
    remove_logic: ["IF APPROVER-2-ID NOT = SPACES", "END-IF"]