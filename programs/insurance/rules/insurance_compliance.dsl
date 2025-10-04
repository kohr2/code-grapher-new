rule:
  name: "Insurance Compliance Rule"
  description: "Insurance-specific compliance requirements"

variables:
  - name: "CLAIM-NUMBER"
    type: "ALPHANUMERIC"
    pic: "X(10)"
    description: "Unique claim identifier"
    value: "REQUIRED"
  - name: "CLAIM-AMOUNT"
    type: "NUMERIC"
    pic: "9(8)V99"
    description: "Claim amount"
    value: "REQUIRED"
  - name: "POLICY-NUMBER"
    type: "ALPHANUMERIC"
    pic: "X(10)"
    description: "Policy number"
    value: "REQUIRED"
  - name: "POLICY-LIMIT"
    type: "NUMERIC"
    pic: "9(8)V99"
    description: "Policy coverage limit"
    value: "REQUIRED"

conditions:
  claim_amount_check:
    check: "CLAIM-AMOUNT <= POLICY-LIMIT"
    description: "Check claim against policy limit"

requirements:
  claim_validation:
    description: "Claim number must be validated"
    check: "CLAIM-NUMBER IS NOT EQUAL TO SPACES"
    violation_message: "Claim number validation failed"
    severity: "HIGH"
  
  policy_limit_check:
    description: "Claim amount must not exceed policy limit"
    check: "CLAIM-AMOUNT <= POLICY-LIMIT"
    violation_message: "Claim exceeds policy limit"
    severity: "HIGH"
  
  approval_required_check:
    description: "Large claims require approval"
    check: "CLAIM-AMOUNT > 5000 IMPLIES APPROVAL-REQUIRED"
    violation_message: "Large claim requires approval"
    severity: "MEDIUM"

compliant_logic:
  - "Validate claim number format"
  - "Check policy coverage limits"
  - "Verify claim amount accuracy"
  - "Require approval for large claims"
  - "Maintain audit trail"

violation_examples:
  claim_exceeds_limit:
    description: "Claim processed without limit check"
    code: |
      MOVE 'A' TO CLAIM-STATUS
      * Missing policy limit validation
    violation_type: "Policy limit check missing"
    severity: "HIGH"
  
  large_claim_no_approval:
    description: "Large claim without approval"
    code: |
      IF CLAIM-AMOUNT > 10000
          * Process large claim without approval
      END-IF
    violation_type: "Large claim approval missing"
    severity: "MEDIUM"
