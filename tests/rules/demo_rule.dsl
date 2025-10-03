rule:
  name: "Demo Rule"
  description: "Demo rule for Neo4j integration test"

variables:
  - name: "DEMO-VAR"
    type: "string"
    pic: "X(10)"
    description: "Demo variable"

requirements:
  demo_requirement:
    description: "Demo variable must be present"
    check: "DEMO-VAR variable must be defined"
    violation_message: "DEMO-VAR variable not defined"
    severity: "HIGH"

compliant_logic:
  demo_logic:
    - "MOVE 'DEMO' TO DEMO-VAR"