rule:
  name: "Advanced Fraud Analytics Compliance Rule"
  description: "Advanced fraud analytics including machine learning, pattern recognition, and behavioral biometrics compliance"
  domain: "fraud_analytics"
  version: "1.0"
  effective_date: "2025-01-01"

variables:
  - name: "WS-NEURAL-NETWORK-SCORE"
    description: "Neural network based fraud scoring"
    type: "numeric"
    pic: "9(4)"
    required: true
    validation: "must be calculated using advanced ML algorithms"
    
  - name: "WS-PATTERN-RECOGNITION-SCORE"
    description: "Pattern recognition based risk score"
    type: "numeric"
    pic: "9(3)"
    required: true
    validation: "must detect suspicious transaction patterns"
    
  - name: "WS-BEHAVIORAL-BIOMETRICS-SCORE"
    description: "Behavioral biometrics analysis score"
    type: "numeric"
    pic: "9(3)"
    required: true
    validation: "must analyze typing patterns and device fingerprinting"
    
  - name: "WS-CONSORTIUM-DATA-SCORE"
    description: "Cross-bank consortium data analysis score"
    type: "numeric"
    pic: "9(3)"
    required: true
    validation: "must check industry-wide fraud patterns"
    
  - name: "WS-GRADIENT-BOOSTING-SCORE"
    description: "Gradient boosting model fraud score"
    type: "numeric"
    pic: "9(3)"
    required: true
    validation: "must use ensemble learning methods"
    
  - name: "WS-RANDOM-FOREST-SCORE"
    description: "Random forest ensemble fraud score"
    type: "numeric"
    pic: "9(3)"
    required: true
    validation: "must use multiple decision trees"
    
  - name: "WS-LOGISTIC-REGRESSION-SCORE"
    description: "Logistic regression probability score"
    type: "numeric"
    pic: "9(3)"
    required: true
    validation: "must calculate fraud probability"
    
  - name: "WS-ENSEMBLE-FINAL-SCORE"
    description: "Final ensemble score combining all models"
    type: "numeric"
    pic: "9(4)"
    required: true
    validation: "must be weighted average of all model scores"

requirements:
  - name: "neural_network_scoring"
    description: "Neural network scoring must be implemented for advanced fraud detection"
    priority: "high"
    check: "WS-NEURAL-NETWORK-SCORE must be calculated with non-linear transformations"
    
  - name: "pattern_recognition"
    description: "Pattern recognition must detect round dollar amounts and test transactions"
    priority: "high"
    check: "Must detect round dollar patterns and ascending amount sequences"
    
  - name: "behavioral_biometrics"
    description: "Behavioral biometrics must analyze typing patterns and device fingerprints"
    priority: "medium"
    check: "Must analyze unusual hours, device risk, and session behavior"
    
  - name: "consortium_data_check"
    description: "Consortium data must be checked for industry-wide fraud patterns"
    priority: "high"
    check: "Must check industry blacklists and velocity consortium data"
    
  - name: "gradient_boosting_model"
    description: "Gradient boosting model must be implemented for fraud scoring"
    priority: "high"
    check: "Must use decision tree ensemble with gradient boosting"
    
  - name: "random_forest_model"
    description: "Random forest model must be implemented for fraud scoring"
    priority: "high"
    check: "Must use multiple decision trees with random feature selection"
    
  - name: "logistic_regression_model"
    description: "Logistic regression model must calculate fraud probability"
    priority: "medium"
    check: "Must use linear regression with probability transformation"
    
  - name: "ensemble_scoring"
    description: "Final ensemble score must combine all model outputs"
    priority: "critical"
    check: "Must use weighted averaging of all model scores"

conditions:
  - name: "advanced_analytics_execution"
    description: "All advanced analytics models must be executed"
    check: "All ML models must be executed for comprehensive fraud detection"
    severity: "critical"
    
  - name: "pattern_detection_completeness"
    description: "All pattern detection algorithms must be implemented"
    check: "Round dollar, ascending amount, and test transaction patterns must be detected"
    severity: "high"
    
  - name: "biometric_analysis_accuracy"
    description: "Behavioral biometric analysis must be accurate"
    check: "Typing patterns, device fingerprinting, and session behavior must be analyzed"
    severity: "medium"
    
  - name: "consortium_data_integration"
    description: "Consortium data must be properly integrated"
    check: "Industry blacklists and velocity data must be checked"
    severity: "high"
    
  - name: "model_ensemble_accuracy"
    description: "Model ensemble must provide accurate fraud predictions"
    check: "Weighted averaging of all models must be implemented"
    severity: "critical"

compliant_logic:
  description: "Advanced fraud analytics implementation includes machine learning models, pattern recognition, behavioral analysis, and ensemble scoring"
  
  implementation:
    - "Execute neural network scoring with non-linear transformations"
    - "Perform pattern recognition for suspicious transaction sequences"
    - "Analyze behavioral biometrics including typing patterns and device fingerprints"
    - "Check consortium data for industry-wide fraud patterns"
    - "Execute gradient boosting, random forest, and logistic regression models"
    - "Combine all model outputs with weighted ensemble scoring"
    - "Apply final business rule adjustments based on ensemble results"

violation_examples:
  - type: "missing_neural_network"
    description: "Neural network scoring not implemented"
    code: |
      * VIOLATION: Missing neural network scoring
      * Should include: PERFORM 4100-NEURAL-NETWORK-SCORING
      PERFORM 4200-PATTERN-RECOGNITION
    severity: "high"
    
  - type: "incomplete_pattern_detection"
    description: "Pattern recognition algorithms incomplete"
    code: |
      * VIOLATION: Incomplete pattern detection
      PERFORM 4210-CHECK-ROUND-DOLLAR-PATTERN
      * Missing: PERFORM 4220-CHECK-ASCENDING-AMOUNT-PATTERN
      * Missing: PERFORM 4230-CHECK-TEST-TRANSACTION-PATTERN
    severity: "high"
    
  - type: "missing_biometric_analysis"
    description: "Behavioral biometrics analysis missing"
    code: |
      * VIOLATION: Missing biometric analysis
      * Should include: PERFORM 4310-ANALYZE-TYPING-PATTERNS
      * Should include: PERFORM 4320-ANALYZE-DEVICE-FINGERPRINT
      * Should include: PERFORM 4330-ANALYZE-SESSION-BEHAVIOR
    severity: "medium"
    
  - type: "consortium_data_bypass"
    description: "Consortium data checks bypassed"
    code: |
      * VIOLATION: Consortium data bypassed
      * Missing: PERFORM 4410-CHECK-INDUSTRY-BLACKLIST
      * Missing: PERFORM 4420-CHECK-VELOCITY-CONSORTIUM
    severity: "high"
    
  - type: "missing_ml_models"
    description: "Machine learning models not implemented"
    code: |
      * VIOLATION: ML models missing
      * Missing: PERFORM 5100-GRADIENT-BOOSTING-MODEL
      * Missing: PERFORM 5200-RANDOM-FOREST-MODEL
      * Missing: PERFORM 5300-LOGISTIC-REGRESSION-MODEL
    severity: "critical"
    
  - type: "ensemble_scoring_incorrect"
    description: "Ensemble scoring implementation incorrect"
    code: |
      * VIOLATION: Incorrect ensemble scoring
      COMPUTE WS-TOTAL-RISK-SCORE = WS-NEURAL-NETWORK-SCORE
      * Should be: COMPUTE WS-TOTAL-RISK-SCORE = (WS-NEURAL-NETWORK-SCORE * 0.25) + (WS-GRADIENT-BOOSTING-SCORE * 0.30) + (WS-RANDOM-FOREST-SCORE * 0.25) + (WS-LOGISTIC-REGRESSION-SCORE * 0.20)
    severity: "critical"
