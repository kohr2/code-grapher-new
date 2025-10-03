rule:
  name: "Demo Rule"
  description: "Demo rule for Neo4j integration test"

variables:
  - name: "DEMO-VAR"
    type: "string"
    pic: "X(10)"
    description: "Demo variable"

conditions:
  demo_condition:
    check: "DEMO-VAR is defined"
    description: "Check DEMO-VAR variable"
    logic: "DEMO-VAR must be present"

requirements:
  demo_requirement:
    description: "Demo variable must be present"
    check: "DEMO-VAR variable must be defined"
    violation_message: "DEMO-VAR variable not defined"
    severity: "HIGH"

compliant_logic:
  demo_logic:
    - "MOVE 'DEMO' TO DEMO-VAR"

violation_examples:
  - description: "DEMO-VAR variable missing"
    code: |
      IDENTIFICATION DIVISION.
      PROGRAM-ID. BAD-DEMO.
      DATA DIVISION.
      PROCEDURE DIVISION.
      DISPLAY 'No DEMO-VAR defined'.
      STOP RUN.