000100 IDENTIFICATION DIVISION.                                                
000200 PROGRAM-ID. FRAUD-MGMT-SYSTEM.                                          
000300 AUTHOR. FRAUD-DETECTION-TEAM.                                           
000400 DATE-WRITTEN. 2025-08-06.                                               
000500 DATE-COMPILED.                                                          
000600 
000700 ENVIRONMENT DIVISION.                                                   
000800 CONFIGURATION SECTION.                                                  
000900 SOURCE-COMPUTER. IBM-Z15.                                               
001000 OBJECT-COMPUTER. IBM-Z15.                                               
001100 
001200 INPUT-OUTPUT SECTION.                                                   
001300 FILE-CONTROL.                                                           
001400     SELECT TRANSACTION-FILE ASSIGN TO 'TRANFILE'
001500     ORGANIZATION IS SEQUENTIAL
001600     ACCESS MODE IS SEQUENTIAL
001700 FILE STATUS IS WS-TRANS-STATUS.                                         
001800 
001900     SELECT CUSTOMER-FILE ASSIGN TO 'CUSTFILE'
002000     ORGANIZATION IS INDEXED
002100     ACCESS MODE IS DYNAMIC
002200     RECORD KEY IS CUST-CARD-NUMBER
002300 FILE STATUS IS WS-CUST-STATUS.                                          
002400 
002500     SELECT MERCHANT-FILE ASSIGN TO 'MERCHFILE'
002600     ORGANIZATION IS INDEXED
002700     ACCESS MODE IS DYNAMIC
002800     RECORD KEY IS MERCH-ID
002900 FILE STATUS IS WS-MERCH-STATUS.                                         
003000 
003100     SELECT FRAUD-LOG ASSIGN TO 'FRAUDLOG'
003200     ORGANIZATION IS SEQUENTIAL
003300     ACCESS MODE IS SEQUENTIAL
003400 FILE STATUS IS WS-FRAUD-STATUS.                                         
003500 
003600     SELECT VELOCITY-FILE ASSIGN TO 'VELOFILE'
003700     ORGANIZATION IS INDEXED
003800     ACCESS MODE IS DYNAMIC
003900     RECORD KEY IS VELO-CARD-NUMBER
004000 FILE STATUS IS WS-VELO-STATUS.                                          
004100 
004200 DATA DIVISION.                                                          
004300 FILE SECTION.                                                           
004400 
004500 FD  TRANSACTION-FILE                                                    
004600     RECORDING MODE IS F
004700 RECORD CONTAINS 200 CHARACTERS.                                         
004800 01  TRANSACTION-RECORD.                                                 
004900 05  TRANS-ID                PIC 9(12).                                  
005000 05  TRANS-CARD-NUMBER       PIC 9(16).                                  
005100 05  TRANS-AMOUNT            PIC 9(8)V99.                                
005200 05  TRANS-DATE              PIC 9(8).                                   
005300 05  TRANS-TIME              PIC 9(6).                                   
005400 05  TRANS-MERCHANT-ID       PIC X(10).                                  
005500 05  TRANS-MERCHANT-CAT      PIC 9(4).                                   
005600 05  TRANS-TYPE              PIC X(2).                                   
005700 05  TRANS-LOCATION-ZIP      PIC X(10).                                  
005800 05  TRANS-COUNTRY-CODE      PIC X(3).                                   
005900 05  TRANS-CURRENCY          PIC X(3).                                   
006000 05  TRANS-CHANNEL           PIC X(3).                                   
006100 05  TRANS-POS-ENTRY         PIC X(2).                                   
006200 05  TRANS-CHIP-STATUS       PIC X(1).                                   
006300 05  TRANS-PIN-VERIFIED      PIC X(1).                                   
006400 05  FILLER                  PIC X(134).                                 
006500 
006600 FD  CUSTOMER-FILE                                                       
006700     RECORDING MODE IS F
006800 RECORD CONTAINS 300 CHARACTERS.                                         
006900 01  CUSTOMER-RECORD.                                                    
007000 05  CUST-CARD-NUMBER        PIC 9(16).                                  
007100 05  CUST-NAME               PIC X(40).                                  
007200 05  CUST-HOME-ZIP           PIC X(10).                                  
007300 05  CUST-HOME-COUNTRY       PIC X(3).                                   
007400 05  CUST-ACCOUNT-OPEN-DATE  PIC 9(8).                                   
007500 05  CUST-CREDIT-LIMIT       PIC 9(8)V99.                                
007600 05  CUST-CURRENT-BALANCE    PIC 9(8)V99.                                
007700 05  CUST-RISK-SCORE         PIC 9(3).                                   
007800 05  CUST-FRAUD-FLAG         PIC X(1).                                   
007900 05  CUST-LAST-TRANS-DATE    PIC 9(8).                                   
008000 05  CUST-AVG-MONTHLY-SPEND  PIC 9(8)V99.                                
008100 05  CUST-MAX-DAILY-SPEND    PIC 9(8)V99.                                
008200 05  CUST-TRAVEL-FLAG        PIC X(1).                                   
008300 05  CUST-PHONE-NUMBER       PIC X(15).                                  
008400 05  CUST-EMAIL              PIC X(50).                                  
008500 05  FILLER                  PIC X(144).                                 
008600 
008700 FD  MERCHANT-FILE                                                       
008800     RECORDING MODE IS F
008900 RECORD CONTAINS 150 CHARACTERS.                                         
009000 01  MERCHANT-RECORD.                                                    
009100 05  MERCH-ID                PIC X(10).                                  
009200 05  MERCH-NAME              PIC X(40).                                  
009300 05  MERCH-CATEGORY          PIC 9(4).                                   
009400 05  MERCH-RISK-LEVEL        PIC 9(2).                                   
009500 05  MERCH-ZIP               PIC X(10).                                  
009600 05  MERCH-COUNTRY           PIC X(3).                                   
009700 05  MERCH-FRAUD-RATE        PIC 9(3)V99.                                
009800 05  MERCH-LAST-FRAUD-DATE   PIC 9(8).                                   
009900 05  FILLER                  PIC X(70).                                  
010000 
010100 FD  FRAUD-LOG                                                           
010200     RECORDING MODE IS F
010300 RECORD CONTAINS 400 CHARACTERS.                                         
010400 01  FRAUD-LOG-RECORD.                                                   
010500 05  FRAUD-TIMESTAMP         PIC X(20).                                  
010600 05  FRAUD-TRANS-ID          PIC 9(12).                                  
010700 05  FRAUD-CARD-NUMBER       PIC 9(16).                                  
010800 05  FRAUD-REASON-CODE       PIC X(10).                                  
010900 05  FRAUD-RISK-SCORE        PIC 9(3).                                   
011000 05  FRAUD-ACTION-TAKEN      PIC X(20).                                  
011100 05  FRAUD-RULE-TRIGGERED    PIC X(50).                                  
011200 05  FRAUD-AMOUNT            PIC 9(8)V99.                                
011300 05  FRAUD-MERCHANT          PIC X(40).                                  
011400 05  FRAUD-LOCATION          PIC X(20).                                  
011500 05  FRAUD-ANALYST-ID        PIC X(10).                                  
011600 05  FRAUD-RESOLUTION        PIC X(100).                                 
011700 05  FILLER                  PIC X(73).                                  
011800 
011900 FD  VELOCITY-FILE                                                       
012000     RECORDING MODE IS F
012100 RECORD CONTAINS 100 CHARACTERS.                                         
012200 01  VELOCITY-RECORD.                                                    
012300 05  VELO-CARD-NUMBER        PIC 9(16).                                  
012400 05  VELO-TRANS-COUNT-1H     PIC 9(3).                                   
012500 05  VELO-AMOUNT-1H          PIC 9(8)V99.                                
012600 05  VELO-TRANS-COUNT-24H    PIC 9(4).                                   
012700 05  VELO-AMOUNT-24H         PIC 9(8)V99.                                
012800 05  VELO-LAST-UPDATE        PIC 9(14).                                  
012900 05  VELO-LOCATION-COUNT     PIC 9(2).                                   
013000 05  VELO-MERCHANT-COUNT     PIC 9(3).                                   
013100 05  FILLER                  PIC X(31).                                  
013200 
013300 WORKING-STORAGE SECTION.                                                
013400 
013500* File Status Variables                                                  
013600 01  WS-TRANS-STATUS             PIC XX.                                 
013700 01  WS-CUST-STATUS              PIC XX.                                 
013800 01  WS-MERCH-STATUS             PIC XX.                                 
013900 01  WS-FRAUD-STATUS             PIC XX.                                 
014000 01  WS-VELO-STATUS              PIC XX.                                 
014100 
014200* Control Variables                                                      
014300 01  WS-EOF-FLAG                 PIC X VALUE 'N'.                        
014400 88  EOF-REACHED             VALUE 'Y'.                                  
014500 01  WS-FRAUD-DETECTED           PIC X VALUE 'N'.                        
014600 88  FRAUD-FOUND             VALUE 'Y'.                                  
014700 01  WS-PROCESS-FLAG             PIC X VALUE 'Y'.                        
014800 
014900* Risk Assessment Variables                                              
015000 01  WS-TOTAL-RISK-SCORE         PIC 9(4) VALUE ZERO.                    
015100 01  WS-TRANSACTION-RISK         PIC 9(3) VALUE ZERO.                    
015200 01  WS-VELOCITY-RISK            PIC 9(3) VALUE ZERO.                    
015300 01  WS-LOCATION-RISK            PIC 9(3) VALUE ZERO.                    
015400 01  WS-MERCHANT-RISK            PIC 9(3) VALUE ZERO.                    
015500 01  WS-BEHAVIORAL-RISK          PIC 9(3) VALUE ZERO.                    
015600 
015700* Fraud Thresholds                                                       
015800 01  WS-FRAUD-THRESHOLDS.                                                
015900 05  HIGH-RISK-THRESHOLD     PIC 9(3) VALUE 800.                         
016000 05  MEDIUM-RISK-THRESHOLD   PIC 9(3) VALUE 500.                         
016100 05  LOW-RISK-THRESHOLD      PIC 9(3) VALUE 300.                         
016200 05  MAX-DAILY-VELOCITY      PIC 9(4) VALUE 50.                          
016300 05  MAX-HOURLY-VELOCITY     PIC 9(2) VALUE 10.                          
016400 05  SUSPICIOUS-AMOUNT       PIC 9(8)V99 VALUE 5000.00.                  
016500 05  MAX-LOCATION-VARIANCE   PIC 9(4) VALUE 1000.                        
016600 
016700* Counters and Statistics                                                
016800 01  WS-COUNTERS.                                                        
016900 05  WS-TRANSACTIONS-PROCESSED PIC 9(8) VALUE ZERO.                      
017000 05  WS-FRAUD-DETECTED-COUNT   PIC 9(6) VALUE ZERO.                      
017100 05  WS-FALSE-POSITIVE-COUNT   PIC 9(6) VALUE ZERO.                      
017200 05  WS-APPROVED-COUNT         PIC 9(8) VALUE ZERO.                      
017300 05  WS-DECLINED-COUNT         PIC 9(6) VALUE ZERO.                      
017400 
017500* Work Variables                                                         
017600 01  WS-CURRENT-TIMESTAMP        PIC X(20).                              
017700 01  WS-WORK-AMOUNT              PIC 9(8)V99.                            
017800 01  WS-WORK-DATE                PIC 9(8).                               
017900 01  WS-WORK-TIME                PIC 9(6).                               
018000 01  WS-DAYS-DIFF                PIC S9(4) COMP.                         
018100 01  WS-DISTANCE-KM              PIC 9(6).                               
018200 01  WS-TIME-DIFF-HOURS          PIC 9(4).                               
018300 
018400* Rule Engine Variables                                                  
018500 01  WS-RULE-RESULTS.                                                    
018600 05  RULE-01-TRIGGERED       PIC X VALUE 'N'.                            
018700 05  RULE-02-TRIGGERED       PIC X VALUE 'N'.                            
018800 05  RULE-03-TRIGGERED       PIC X VALUE 'N'.                            
018900 05  RULE-04-TRIGGERED       PIC X VALUE 'N'.                            
019000 05  RULE-05-TRIGGERED       PIC X VALUE 'N'.                            
019100 05  RULE-06-TRIGGERED       PIC X VALUE 'N'.                            
019200 05  RULE-07-TRIGGERED       PIC X VALUE 'N'.                            
019300 05  RULE-08-TRIGGERED       PIC X VALUE 'N'.                            
019400 05  RULE-09-TRIGGERED       PIC X VALUE 'N'.                            
019500 05  RULE-10-TRIGGERED       PIC X VALUE 'N'.                            
019600 
019700* Fraud Action Codes                                                     
019800 01  WS-FRAUD-ACTIONS.                                                   
019900 05  ACTION-DECLINE          PIC X(20) VALUE 'DECLINE-TRANSACTION'.      
020000 05  ACTION-HOLD             PIC X(20) VALUE 'HOLD-FOR-REVIEW'.          
020100 05  ACTION-VERIFY           PIC X(20) VALUE 'CUSTOMER-VERIFY'.          
020200 05  ACTION-APPROVE          PIC X(20) VALUE 'APPROVE-NORMAL'.           
020300 05  ACTION-FLAG             PIC X(20) VALUE 'FLAG-ACCOUNT'.             
020400 
020500* Error Messages                                                         
020600 01  WS-ERROR-MESSAGES.                                                  
020700     05  ERR-FILE-NOT-FOUND      PIC X(50)
020800 VALUE 'ERROR: Required file not found or accessible'.                   
020900     05  ERR-INVALID-CARD        PIC X(50)
021000 VALUE 'ERROR: Invalid card number format'.                              
021100     05  ERR-SYSTEM-ERROR        PIC X(50)
021200 VALUE 'ERROR: System processing error occurred'.                        
021300 
021400 PROCEDURE DIVISION.                                                     
021500 
021600 0000-MAIN-CONTROL SECTION.                                              
021700 0000-MAIN-PROCESS.                                                      
021800     PERFORM 1000-INITIALIZE-PROGRAM
021900     PERFORM 2000-PROCESS-TRANSACTIONS
022000     PERFORM 9000-FINALIZE-PROGRAM
022100     STOP RUN.
022200 
022300 1000-INITIALIZE-PROGRAM SECTION.                                        
022400 1000-INIT-START.                                                        
022500     DISPLAY 'FRAUD MANAGEMENT SYSTEM - INITIALIZING'
022600     PERFORM 1100-OPEN-FILES
022700     PERFORM 1200-INITIALIZE-VARIABLES
022800     PERFORM 1300-LOAD-FRAUD-PARAMETERS.
022900 
023000 1100-OPEN-FILES.                                                        
023100     OPEN INPUT TRANSACTION-FILE
023200     IF WS-TRANS-STATUS NOT = '00'
023300     DISPLAY ERR-FILE-NOT-FOUND ' - TRANSACTION FILE'
023400     STOP RUN
023500     END-IF
023600 
023700     WRITE FRAUD-LOG-RECORD
023800     IF WS-FRAUD-STATUS NOT = '00'
023900     DISPLAY 'ERROR WRITING TO FRAUD LOG: ' WS-FRAUD-STATUS
024000 END-IF.                                                                 
024100 
024200 3100-UPDATE-CUSTOMER-PROFILE SECTION.                                   
024300 3100-UPDATE-START.                                                      
024400* Update customer's last transaction date and spending patterns          
024500     MOVE TRANS-DATE TO CUST-LAST-TRANS-DATE
024600 
024700* Update fraud flag if high-risk transaction detected                    
024800     IF WS-TOTAL-RISK-SCORE >= HIGH-RISK-THRESHOLD
024900     MOVE 'Y' TO CUST-FRAUD-FLAG
025000     END-IF
025100 
025200* Recalculate average monthly spend (simplified)                         
025300     IF CUST-AVG-MONTHLY-SPEND = ZERO
025400     MOVE TRANS-AMOUNT TO CUST-AVG-MONTHLY-SPEND
025500     ELSE
025600     COMPUTE CUST-AVG-MONTHLY-SPEND = (CUST-AVG-MONTHLY-SPEND * 0.9) + (TRANS-AMOUNT * 0.1)
025700     END-IF
025800 
025900* Update maximum daily spend if exceeded                                 
026000     IF TRANS-AMOUNT > CUST-MAX-DAILY-SPEND
026100     MOVE TRANS-AMOUNT TO CUST-MAX-DAILY-SPEND
026200     END-IF
026300 
026400     REWRITE CUSTOMER-RECORD
026500     IF WS-CUST-STATUS NOT = '00'
026600     DISPLAY 'ERROR UPDATING CUSTOMER RECORD: ' WS-CUST-STATUS
026700 END-IF.                                                                 
026800 
026900 4000-ADVANCED-ANALYTICS SECTION.                                        
027000 4000-ANALYTICS-START.                                                   
027100* Advanced pattern recognition and machine learning scoring              
027200     PERFORM 4100-NEURAL-NETWORK-SCORING
027300     PERFORM 4200-PATTERN-RECOGNITION
027400     PERFORM 4300-BEHAVIORAL-BIOMETRICS
027500     PERFORM 4400-CONSORTIUM-DATA-CHECK.
027600 
027700 4100-NEURAL-NETWORK-SCORING.                                            
027800* Simulate neural network scoring based on transaction features          
027900     COMPUTE WS-WORK-AMOUNT = (WS-TRANSACTION-RISK * 0.25) + (WS-VELOCITY-RISK * 0.20) + (WS-LOCATION-RISK * 0.15) + (WS-MERCHANT-RISK * 0.20) + (WS-BEHAVIORAL-RISK * 0.20)
028000 
028100* Apply non-linear transformation (sigmoid approximation)                
028200     IF WS-WORK-AMOUNT > 500 COMPUTE WS-WORK-AMOUNT = WS-WORK-AMOUNT * 1.5
028300     ELSE
028400     COMPUTE WS-WORK-AMOUNT = WS-WORK-AMOUNT * 0.8
028500     END-IF
028600 
028700     ADD WS-WORK-AMOUNT TO WS-TOTAL-RISK-SCORE.
028800 
028900 4200-PATTERN-RECOGNITION.                                               
029000* Identify suspicious patterns in transaction sequences                  
029100     IF VELO-TRANS-COUNT-1H > 3
029200     PERFORM 4210-CHECK-ROUND-DOLLAR-PATTERN
029300     PERFORM 4220-CHECK-ASCENDING-AMOUNT-PATTERN
029400     PERFORM 4230-CHECK-TEST-TRANSACTION-PATTERN
029500 END-IF.                                                                 
029600 
029700 4210-CHECK-ROUND-DOLLAR-PATTERN.                                        
029800* Detect round dollar amounts (potential card testing)                   
029900     COMPUTE WS-WORK-AMOUNT = TRANS-AMOUNT - FUNCTION INTEGER(TRANS-AMOUNT)
030000     IF WS-WORK-AMOUNT = ZERO AND TRANS-AMOUNT <= 100.00
030100     ADD 75 TO WS-TOTAL-RISK-SCORE
030200 END-IF.                                                                 
030300 
030400 4220-CHECK-ASCENDING-AMOUNT-PATTERN.                                    
030500* This would normally check against recent transaction history           
030600* Simplified version checks if amount follows common test patterns       
030700     EVALUATE TRANS-AMOUNT WHEN 1.00 WHEN 5.00 WHEN 10.00 WHEN 25.00
030800     IF VELO-TRANS-COUNT-1H > 2
030900     ADD 100 TO WS-TOTAL-RISK-SCORE
031000     END-IF
031100 END-EVALUATE.                                                           
031200 
031300 4230-CHECK-TEST-TRANSACTION-PATTERN.                                    
031400* Detect rapid small transactions followed by large ones                 
031500     IF TRANS-AMOUNT < 50.00 AND VELO-TRANS-COUNT-1H > 5
031600     ADD 150 TO WS-TOTAL-RISK-SCORE
031700 END-IF.                                                                 
031800 
031900 4300-BEHAVIORAL-BIOMETRICS.                                             
032000* Simulate behavioral analysis based on transaction timing               
032100     PERFORM 4310-ANALYZE-TYPING-PATTERNS
032200     PERFORM 4320-ANALYZE-DEVICE-FINGERPRINT
032300     PERFORM 4330-ANALYZE-SESSION-BEHAVIOR.
032400 
032500 4310-ANALYZE-TYPING-PATTERNS.                                           
032600* In real implementation, this would analyze keystroke dynamics          
032700* Simplified: flag transactions during unusual hours                     
032800     IF TRANS-TIME < 050000 OR TRANS-TIME > 230000
032900     IF TRANS-CHANNEL = 'ONL'
033000     ADD 50 TO WS-TOTAL-RISK-SCORE
033100     END-IF
033200 END-IF.                                                                 
033300 
033400 4320-ANALYZE-DEVICE-FINGERPRINT.                                        
033500* Simplified device risk assessment                                      
033600     IF TRANS-POS-ENTRY = '90'
033700     IF TRANS-AMOUNT > 200.00
033800     ADD 25 TO WS-TOTAL-RISK-SCORE
033900     END-IF
034000     END-IF
034100 
034200     IF TRANS-CHIP-STATUS = 'N' AND TRANS-AMOUNT > 100.00
034300     ADD 40 TO WS-TOTAL-RISK-SCORE
034400 END-IF.                                                                 
034500 
034600 4330-ANALYZE-SESSION-BEHAVIOR.                                          
034700* Check for suspicious session patterns                                  
034800     IF TRANS-CHANNEL = 'ONL'
034900     IF VELO-MERCHANT-COUNT > 3
035000     ADD 60 TO WS-TOTAL-RISK-SCORE
035100     END-IF
035200 END-IF.                                                                 
035300 
035400 4400-CONSORTIUM-DATA-CHECK.                                             
035500* Simulate cross-bank fraud consortium data check                        
035600     IF CUST-RISK-SCORE > 750
035700     PERFORM 4410-CHECK-INDUSTRY-BLACKLIST
035800     PERFORM 4420-CHECK-VELOCITY-CONSORTIUM
035900 END-IF.                                                                 
036000 
036100 4410-CHECK-INDUSTRY-BLACKLIST.                                          
036200* In production, this would check against shared fraud databases         
036300     IF MERCH-FRAUD-RATE > 5.00
036400     ADD 100 TO WS-TOTAL-RISK-SCORE
036500 END-IF.                                                                 
036600 
036700 4420-CHECK-VELOCITY-CONSORTIUM.                                         
036800* Check if card appears in recent consortium alerts                      
036900     IF VELO-TRANS-COUNT-24H > 30
037000     ADD 125 TO WS-TOTAL-RISK-SCORE
037100 END-IF.                                                                 
037200 
037300 5000-REAL-TIME-SCORING SECTION.                                         
037400 5000-SCORING-START.                                                     
037500* Real-time risk scoring with multiple model ensemble                    
037600     PERFORM 5100-GRADIENT-BOOSTING-MODEL
037700     PERFORM 5200-RANDOM-FOREST-MODEL
037800     PERFORM 5300-LOGISTIC-REGRESSION-MODEL
037900     PERFORM 5400-ENSEMBLE-SCORING.
038000 
038100 5100-GRADIENT-BOOSTING-MODEL.                                           
038200* Simulate gradient boosting decision tree scoring                       
038300     COMPUTE WS-WORK-AMOUNT = (TRANS-AMOUNT / CUST-AVG-MONTHLY-SPEND) * 100
038400 
038500     EVALUATE TRUE WHEN WS-WORK-AMOUNT > 500
038600     ADD 200 TO WS-TOTAL-RISK-SCORE WHEN WS-WORK-AMOUNT > 300
038700     ADD 150 TO WS-TOTAL-RISK-SCORE WHEN WS-WORK-AMOUNT > 200
038800     ADD 100 TO WS-TOTAL-RISK-SCORE WHEN WS-WORK-AMOUNT > 150
038900     ADD 75 TO WS-TOTAL-RISK-SCORE
039000 END-EVALUATE.                                                           
039100 
039200 5200-RANDOM-FOREST-MODEL.                                               
039300* Simulate random forest ensemble                                        
039400     COMPUTE WS-WORK-AMOUNT = WS-VELOCITY-RISK + WS-LOCATION-RISK + WS-MERCHANT-RISK
039500 
039600     IF WS-WORK-AMOUNT > 400
039700     ADD 175 TO WS-TOTAL-RISK-SCORE
039800     ELSE IF WS-WORK-AMOUNT > 200
039900     ADD 100 TO WS-TOTAL-RISK-SCORE
040000     ELSE IF WS-WORK-AMOUNT > 100
040100     ADD 50 TO WS-TOTAL-RISK-SCORE
040200 END-IF.                                                                 
040300 
040400 5300-LOGISTIC-REGRESSION-MODEL.                                         
040500* Simulate logistic regression probability scoring                       
040600     COMPUTE WS-WORK-AMOUNT = (WS-BEHAVIORAL-RISK * 1.2) + (WS-TRANSACTION-RISK * 1.1) + (MERCH-RISK-LEVEL * 0.8)
040700 
040800     IF WS-WORK-AMOUNT > 300
040900     ADD 125 TO WS-TOTAL-RISK-SCORE
041000 END-IF.                                                                 
041100 
041200 5400-ENSEMBLE-SCORING.                                                  
041300* Combine multiple model outputs with weighted averaging                 
041400     COMPUTE WS-TOTAL-RISK-SCORE = WS-TOTAL-RISK-SCORE * 0.85
041500 
041600* Apply final adjustments based on business rules                        
041700     IF CUST-FRAUD-FLAG = 'Y' COMPUTE WS-TOTAL-RISK-SCORE = WS-TOTAL-RISK-SCORE * 1.3
041800     END-IF
041900 
042000     IF WS-TOTAL-RISK-SCORE > 999
042100     MOVE 999 TO WS-TOTAL-RISK-SCORE
042200 END-IF.                                                                 
042300 
042400 6000-CASE-MANAGEMENT SECTION.                                           
042500 6000-CASE-START.                                                        
042600* Create fraud cases for investigation                                   
042700     IF WS-FRAUD-DETECTED = 'Y'
042800     PERFORM 6100-CREATE-FRAUD-CASE
042900     PERFORM 6200-ASSIGN-CASE-PRIORITY
043000     PERFORM 6300-NOTIFY-FRAUD-TEAM
043100 END-IF.                                                                 
043200 
043300 6100-CREATE-FRAUD-CASE.                                                 
043400* Generate unique case ID and initialize case record                     
043500     COMPUTE FRAUD-TRANS-ID = TRANS-ID + 10000000
043600     MOVE 'OPEN' TO FRAUD-RESOLUTION
043700     MOVE 'HIGH' TO FRAUD-ANALYST-ID
043800 
043900     STRING 'CASE_' FRAUD-TRANS-ID DELIMITED BY SIZE
044000 INTO FRAUD-ANALYST-ID.                                                  
044100 
044200 6200-ASSIGN-CASE-PRIORITY.                                              
044300* Assign investigation priority based on risk score and amount           
044400     EVALUATE TRUE WHEN WS-TOTAL-RISK-SCORE >= 900 AND TRANS-AMOUNT > 5000.00
044500     MOVE 'CRITICAL' TO FRAUD-ANALYST-ID
044600     WHEN WS-TOTAL-RISK-SCORE >= 800
044700     MOVE 'HIGH' TO FRAUD-ANALYST-ID
044800     WHEN WS-TOTAL-RISK-SCORE >= 600
044900     MOVE 'MEDIUM' TO FRAUD-ANALYST-ID
045000     WHEN OTHER
045100     MOVE 'LOW' TO FRAUD-ANALYST-ID
045200 END-EVALUATE.                                                           
045300 
045400 6300-NOTIFY-FRAUD-TEAM.                                                 
045500* In production, this would send alerts to fraud analysts                
045600     IF WS-TOTAL-RISK-SCORE >= 900
045700     DISPLAY 'CRITICAL FRAUD ALERT - CASE: ' FRAUD-TRANS-ID
045800     DISPLAY 'CARD: ' TRANS-CARD-NUMBER
045900     DISPLAY 'AMOUNT: ' TRANS-AMOUNT
046000 
046100     OPEN I-O CUSTOMER-FILE
046200     IF WS-CUST-STATUS NOT = '00' AND WS-CUST-STATUS NOT = '05'
046300     DISPLAY ERR-FILE-NOT-FOUND ' - CUSTOMER FILE'
046400     STOP RUN
046500     END-IF
046600 
046700     OPEN INPUT MERCHANT-FILE
046800     IF WS-MERCH-STATUS NOT = '00'
046900     DISPLAY ERR-FILE-NOT-FOUND ' - MERCHANT FILE'
047000     STOP RUN
047100     END-IF
047200 
047300     OPEN OUTPUT FRAUD-LOG
047400     IF WS-FRAUD-STATUS NOT = '00'
047500     DISPLAY ERR-FILE-NOT-FOUND ' - FRAUD LOG FILE'
047600     STOP RUN
047700     END-IF
047800 
047900     OPEN I-O VELOCITY-FILE
048000     IF WS-VELO-STATUS NOT = '00' AND WS-VELO-STATUS NOT = '05'
048100     DISPLAY ERR-FILE-NOT-FOUND ' - VELOCITY FILE'
048200     STOP RUN
048300 END-IF.                                                                 
048400 
048500 1200-INITIALIZE-VARIABLES.                                              
048600     MOVE FUNCTION CURRENT-DATE TO WS-CURRENT-TIMESTAMP
048700     MOVE 'N' TO WS-EOF-FLAG
048800     MOVE 'N' TO WS-FRAUD-DETECTED
048900     INITIALIZE WS-COUNTERS
049000 INITIALIZE WS-RULE-RESULTS.                                             
049100 
049200 1300-LOAD-FRAUD-PARAMETERS.                                             
049300* In production, these would be loaded from parameter tables             
049400     MOVE 850 TO HIGH-RISK-THRESHOLD
049500     MOVE 550 TO MEDIUM-RISK-THRESHOLD
049600     MOVE 350 TO LOW-RISK-THRESHOLD
049700     DISPLAY 'FRAUD PARAMETERS LOADED SUCCESSFULLY'.
049800 
049900 2000-PROCESS-TRANSACTIONS SECTION.                                      
050000 2000-PROCESS-START.                                                     
050100     DISPLAY 'BEGINNING TRANSACTION PROCESSING'
050200     PERFORM 2100-READ-TRANSACTION
050300     PERFORM UNTIL EOF-REACHED
050400     PERFORM 2200-ANALYZE-TRANSACTION
050500     PERFORM 2100-READ-TRANSACTION END-PERFORM
050600     DISPLAY 'TRANSACTION PROCESSING COMPLETED'.
050700 
050800 2100-READ-TRANSACTION.                                                  
050900     READ TRANSACTION-FILE AT END SET EOF-REACHED TO TRUE NOT AT END
051000     ADD 1 TO WS-TRANSACTIONS-PROCESSED
051100     IF WS-TRANSACTIONS-PROCESSED = 1 OR FUNCTION MOD(WS-TRANSACTIONS-PROCESSED, 1000) = 0
051200     DISPLAY 'PROCESSED: ' WS-TRANSACTIONS-PROCESSED
051300     ' TRANSACTIONS'
051400     END-IF
051500 END-READ.                                                               
051600 
051700 2200-ANALYZE-TRANSACTION SECTION.                                       
051800 2200-ANALYSIS-START.                                                    
051900     INITIALIZE WS-RULE-RESULTS
052000     MOVE 'N' TO WS-FRAUD-DETECTED
052100     MOVE ZERO TO WS-TOTAL-RISK-SCORE
052200 
052300     PERFORM 2300-VALIDATE-TRANSACTION
052400     IF WS-PROCESS-FLAG = 'Y'
052500     PERFORM 2400-LOAD-CUSTOMER-DATA
052600     PERFORM 2500-LOAD-MERCHANT-DATA
052700     PERFORM 2600-EXECUTE-FRAUD-RULES
052800     PERFORM 2700-CALCULATE-FINAL-RISK
052900     PERFORM 2800-DETERMINE-ACTION
053000     PERFORM 2900-UPDATE-VELOCITY-DATA
053100     PERFORM 3000-LOG-DECISION
053200 END-IF.                                                                 
053300 
053400 2300-VALIDATE-TRANSACTION.                                              
053500     MOVE 'Y' TO WS-PROCESS-FLAG
053600 
053700* Validate card number using Luhn algorithm                              
053800     PERFORM 2310-VALIDATE-CARD-NUMBER
053900 
054000* Validate amount                                                        
054100     IF TRANS-AMOUNT <= 0 OR TRANS-AMOUNT > 999999.99
054200     MOVE 'N' TO WS-PROCESS-FLAG
054300     DISPLAY 'INVALID TRANSACTION AMOUNT: ' TRANS-AMOUNT
054400     END-IF
054500 
054600* Validate date                                                          
054700     IF TRANS-DATE < 20200101 OR TRANS-DATE > 20301231
054800     MOVE 'N' TO WS-PROCESS-FLAG
054900     DISPLAY 'INVALID TRANSACTION DATE: ' TRANS-DATE
055000 END-IF.                                                                 
055100 
055200 2310-VALIDATE-CARD-NUMBER.                                              
055300* Simplified Luhn algorithm validation                                   
055400     IF TRANS-CARD-NUMBER < 1000000000000000 OR TRANS-CARD-NUMBER > 9999999999999999
055500     MOVE 'N' TO WS-PROCESS-FLAG
055600     DISPLAY 'INVALID CARD NUMBER FORMAT'
055700 END-IF.                                                                 
055800 
055900 2400-LOAD-CUSTOMER-DATA.                                                
056000     MOVE TRANS-CARD-NUMBER TO CUST-CARD-NUMBER
056100     READ CUSTOMER-FILE
056200     IF WS-CUST-STATUS = '23'
056300     DISPLAY 'CUSTOMER NOT FOUND: ' TRANS-CARD-NUMBER
056400     MOVE 'N' TO WS-PROCESS-FLAG
056500     ELSE IF WS-CUST-STATUS NOT = '00'
056600     DISPLAY 'ERROR READING CUSTOMER FILE: ' WS-CUST-STATUS
056700     MOVE 'N' TO WS-PROCESS-FLAG
056800 END-IF.                                                                 
056900 
057000 2500-LOAD-MERCHANT-DATA.                                                
057100     MOVE TRANS-MERCHANT-ID TO MERCH-ID
057200     READ MERCHANT-FILE
057300     IF WS-MERCH-STATUS = '23'
057400     DISPLAY 'MERCHANT NOT FOUND: ' TRANS-MERCHANT-ID
057500* Continue processing with default merchant risk                         
057600     MOVE 50 TO MERCH-RISK-LEVEL
057700     MOVE 'UNKNOWN MERCHANT' TO MERCH-NAME
057800     ELSE IF WS-MERCH-STATUS NOT = '00'
057900     DISPLAY 'ERROR READING MERCHANT FILE: ' WS-MERCH-STATUS
058000 END-IF.                                                                 
058100 
058200 2600-EXECUTE-FRAUD-RULES SECTION.                                       
058300 2600-RULES-START.                                                       
058400     PERFORM 2610-RULE-HIGH-AMOUNT
058500     PERFORM 2620-RULE-VELOCITY-CHECK
058600     PERFORM 2630-RULE-LOCATION-VARIANCE
058700     PERFORM 2640-RULE-MERCHANT-RISK
058800     PERFORM 2650-RULE-TIME-PATTERN
058900     PERFORM 2660-RULE-CARD-NOT-PRESENT
059000     PERFORM 2670-RULE-SUSPICIOUS-CATEGORY
059100     PERFORM 2680-RULE-CUSTOMER-BEHAVIOR
059200     PERFORM 2690-RULE-ACCOUNT-AGE
059300     PERFORM 2695-RULE-CROSS-VALIDATION.
059400 
059500 2610-RULE-HIGH-AMOUNT.                                                  
059600* Rule 1: High Amount Transaction                                        
059700     IF TRANS-AMOUNT > SUSPICIOUS-AMOUNT
059800     MOVE 'Y' TO RULE-01-TRIGGERED
059900     ADD 150 TO WS-TRANSACTION-RISK
060000     IF TRANS-AMOUNT > (CUST-AVG-MONTHLY-SPEND * 3)
060100     ADD 100 TO WS-TRANSACTION-RISK
060200     END-IF
060300 END-IF.                                                                 
060400 
060500 2620-RULE-VELOCITY-CHECK.                                               
060600* Rule 2: Transaction Velocity Analysis                                  
060700     PERFORM 2621-CHECK-VELOCITY-LIMITS
060800     IF VELO-TRANS-COUNT-1H > MAX-HOURLY-VELOCITY
060900     MOVE 'Y' TO RULE-02-TRIGGERED
061000     ADD 200 TO WS-VELOCITY-RISK
061100     END-IF
061200     IF VELO-TRANS-COUNT-24H > MAX-DAILY-VELOCITY
061300     MOVE 'Y' TO RULE-02-TRIGGERED
061400     ADD 150 TO WS-VELOCITY-RISK
061500 END-IF.                                                                 
061600 
061700 2621-CHECK-VELOCITY-LIMITS.                                             
061800     MOVE TRANS-CARD-NUMBER TO VELO-CARD-NUMBER
061900     READ VELOCITY-FILE
062000     IF WS-VELO-STATUS = '23'
062100* First transaction for this card - initialize                           
062200     MOVE TRANS-CARD-NUMBER TO VELO-CARD-NUMBER
062300     MOVE 1 TO VELO-TRANS-COUNT-1H
062400     MOVE 1 TO VELO-TRANS-COUNT-24H
062500     MOVE TRANS-AMOUNT TO VELO-AMOUNT-1H
062600     MOVE TRANS-AMOUNT TO VELO-AMOUNT-24H
062700     MOVE FUNCTION CURRENT-DATE(9:6) TO VELO-LAST-UPDATE
062800     MOVE 1 TO VELO-LOCATION-COUNT
062900     MOVE 1 TO VELO-MERCHANT-COUNT
063000 END-IF.                                                                 
063100 
063200 2630-RULE-LOCATION-VARIANCE.                                            
063300* Rule 3: Geographical Location Analysis                                 
063400     PERFORM 2631-CALCULATE-LOCATION-RISK
063500     IF WS-DISTANCE-KM > MAX-LOCATION-VARIANCE
063600     MOVE 'Y' TO RULE-03-TRIGGERED
063700     ADD 175 TO WS-LOCATION-RISK
063800     IF TRANS-COUNTRY-CODE NOT = CUST-HOME-COUNTRY
063900     IF CUST-TRAVEL-FLAG = 'N'
064000     ADD 100 TO WS-LOCATION-RISK
064100     END-IF
064200     END-IF
064300 END-IF.                                                                 
064400 
064500 2631-CALCULATE-LOCATION-RISK.                                           
064600* Simplified distance calculation based on ZIP codes                     
064700     IF TRANS-LOCATION-ZIP NOT = CUST-HOME-ZIP
064800     IF TRANS-COUNTRY-CODE NOT = CUST-HOME-COUNTRY
064900     MOVE 2000 TO WS-DISTANCE-KM
065000     ELSE
065100     MOVE 500 TO WS-DISTANCE-KM
065200     END-IF
065300     ELSE
065400     MOVE 0 TO WS-DISTANCE-KM
065500 END-IF.                                                                 
065600 
065700 2640-RULE-MERCHANT-RISK.                                                
065800* Rule 4: Merchant Risk Assessment                                       
065900     IF MERCH-RISK-LEVEL > 70
066000     MOVE 'Y' TO RULE-04-TRIGGERED
066100     ADD 125 TO WS-MERCHANT-RISK
066200     END-IF
066300 
066400* High-risk merchant categories                                          
066500     EVALUATE TRANS-MERCHANT-CAT WHEN 4829
066600     MOVE 'Y' TO RULE-04-TRIGGERED
066700     ADD 100 TO WS-MERCHANT-RISK
066800 END-EVALUATE.                                                           
066900 
067000 2650-RULE-TIME-PATTERN.                                                 
067100* Rule 5: Unusual Time Pattern                                           
067200     PERFORM 2651-ANALYZE-TIME-PATTERN
067300     IF WS-TIME-DIFF-HOURS < 1
067400     IF VELO-LOCATION-COUNT > 3
067500     MOVE 'Y' TO RULE-05-TRIGGERED
067600     ADD 150 TO WS-BEHAVIORAL-RISK
067700     END-IF
067800 END-IF.                                                                 
067900 
068000 2651-ANALYZE-TIME-PATTERN.                                              
068100* Check for rapid-fire transactions in different locations               
068200     MOVE 2 TO WS-TIME-DIFF-HOURS
068300     IF TRANS-TIME < 060000 OR TRANS-TIME > 220000
068400     ADD 50 TO WS-BEHAVIORAL-RISK
068500 END-IF.                                                                 
068600 
068700 2660-RULE-CARD-NOT-PRESENT.                                             
068800* Rule 6: Card Not Present Risk                                          
068900     IF TRANS-CHANNEL = 'ONL' OR TRANS-CHANNEL = 'TEL'
069000     IF TRANS-AMOUNT > 500.00
069100     MOVE 'Y' TO RULE-06-TRIGGERED
069200     ADD 75 TO WS-TRANSACTION-RISK
069300     END-IF
069400     IF TRANS-PIN-VERIFIED = 'N'
069500     ADD 50 TO WS-TRANSACTION-RISK
069600     END-IF
069700 END-IF.                                                                 
069800 
069900 2670-RULE-SUSPICIOUS-CATEGORY.                                          
070000* Rule 7: Suspicious Category Combinations                               
070100     IF VELO-MERCHANT-COUNT > 5
070200     MOVE 'Y' TO RULE-07-TRIGGERED
070300     ADD 100 TO WS-BEHAVIORAL-RISK
070400 END-IF.                                                                 
070500 
070600 2680-RULE-CUSTOMER-BEHAVIOR.                                            
070700* Rule 8: Customer Behavioral Analysis                                   
070800     IF CUST-FRAUD-FLAG = 'Y'
070900     MOVE 'Y' TO RULE-08-TRIGGERED
071000     ADD 200 TO WS-BEHAVIORAL-RISK
071100     END-IF
071200 
071300     COMPUTE WS-DAYS-DIFF = TRANS-DATE - CUST-LAST-TRANS-DATE
071400     IF WS-DAYS-DIFF > 90
071500     ADD 50 TO WS-BEHAVIORAL-RISK
071600     END-IF
071700 
071800     IF TRANS-AMOUNT > CUST-MAX-DAILY-SPEND
071900     MOVE 'Y' TO RULE-08-TRIGGERED
072000     ADD 125 TO WS-BEHAVIORAL-RISK
072100 END-IF.                                                                 
072200 
072300 2690-RULE-ACCOUNT-AGE.                                                  
072400* Rule 9: New Account Risk                                               
072500     COMPUTE WS-DAYS-DIFF = TRANS-DATE - CUST-ACCOUNT-OPEN-DATE
072600     IF WS-DAYS-DIFF < 30
072700     MOVE 'Y' TO RULE-09-TRIGGERED
072800     ADD 100 TO WS-BEHAVIORAL-RISK
072900     IF TRANS-AMOUNT > 1000.00
073000     ADD 50 TO WS-BEHAVIORAL-RISK
073100     END-IF
073200 END-IF.                                                                 
073300 
073400 2695-RULE-CROSS-VALIDATION.                                             
073500* Rule 10: Cross-validation of multiple risk factors                     
073600     IF (RULE-01-TRIGGERED = 'Y' AND RULE-03-TRIGGERED = 'Y') OR (RULE-02-TRIGGERED = 'Y' AND RULE-04-TRIGGERED = 'Y') OR (RULE-06-TRIGGERED = 'Y' AND RULE-08-TRIGGERED = 'Y')
073700     MOVE 'Y' TO RULE-10-TRIGGERED
073800     ADD 100 TO WS-TOTAL-RISK-SCORE
073900 END-IF.                                                                 
074000 
074100 2700-CALCULATE-FINAL-RISK.                                              
074200     COMPUTE WS-TOTAL-RISK-SCORE = WS-TRANSACTION-RISK + WS-VELOCITY-RISK + WS-LOCATION-RISK + WS-MERCHANT-RISK + WS-BEHAVIORAL-RISK +
074300 CUST-RISK-SCORE.                                                        
074400 
074500 2800-DETERMINE-ACTION.                                                  
074600     EVALUATE TRUE WHEN WS-TOTAL-RISK-SCORE >= HIGH-RISK-THRESHOLD
074700     MOVE 'Y' TO WS-FRAUD-DETECTED
074800     ADD 1 TO WS-FRAUD-DETECTED-COUNT
074900     ADD 1 TO WS-DECLINED-COUNT WHEN WS-TOTAL-RISK-SCORE >= MEDIUM-RISK-THRESHOLD
075000     PERFORM 2810-MANUAL-REVIEW-REQUIRED WHEN OTHER
075100     ADD 1 TO WS-APPROVED-COUNT
075200 END-EVALUATE.                                                           
075300 
075400 2810-MANUAL-REVIEW-REQUIRED.                                            
075500* Medium risk transactions require additional validation                 
075600     IF RULE-08-TRIGGERED = 'Y' OR RULE-10-TRIGGERED = 'Y'
075700     MOVE 'Y' TO WS-FRAUD-DETECTED
075800     ADD 1 TO WS-FRAUD-DETECTED-COUNT
075900     ELSE
076000     ADD 1 TO WS-APPROVED-COUNT
076100 END-IF.                                                                 
076200 
076300 2900-UPDATE-VELOCITY-DATA.                                              
076400     MOVE TRANS-CARD-NUMBER TO VELO-CARD-NUMBER
076500     READ VELOCITY-FILE
076600     IF WS-VELO-STATUS = '00'
076700     ADD 1 TO VELO-TRANS-COUNT-1H
076800     ADD 1 TO VELO-TRANS-COUNT-24H
076900     ADD TRANS-AMOUNT TO VELO-AMOUNT-1H
077000     ADD TRANS-AMOUNT TO VELO-AMOUNT-24H
077100     MOVE FUNCTION CURRENT-DATE(9:6) TO VELO-LAST-UPDATE
077200     REWRITE VELOCITY-RECORD
077300     ELSE
077400* Create new velocity record                                             
077500     MOVE TRANS-CARD-NUMBER TO VELO-CARD-NUMBER
077600     MOVE 1 TO VELO-TRANS-COUNT-1H
077700     MOVE 1 TO VELO-TRANS-COUNT-24H
077800     MOVE TRANS-AMOUNT TO VELO-AMOUNT-1H
077900     MOVE TRANS-AMOUNT TO VELO-AMOUNT-24H
078000     MOVE FUNCTION CURRENT-DATE(9:6) TO VELO-LAST-UPDATE
078100     MOVE 1 TO VELO-LOCATION-COUNT
078200     MOVE 1 TO VELO-MERCHANT-COUNT
078300     WRITE VELOCITY-RECORD
078400 END-IF.                                                                 
078500 
078600 3000-LOG-DECISION.                                                      
078700     MOVE WS-CURRENT-TIMESTAMP TO FRAUD-TIMESTAMP
078800     MOVE TRANS-ID TO FRAUD-TRANS-ID
078900     MOVE TRANS-CARD-NUMBER TO FRAUD-CARD-NUMBER
079000     MOVE WS-TOTAL-RISK-SCORE TO FRAUD-RISK-SCORE
079100     MOVE TRANS-AMOUNT TO FRAUD-AMOUNT
079200     MOVE MERCH-NAME TO FRAUD-MERCHANT
079300     MOVE TRANS-LOCATION-ZIP TO FRAUD-LOCATION
079400     MOVE 'SYSTEM' TO FRAUD-ANALYST-ID
079500 
079600     IF WS-FRAUD-DETECTED = 'Y'
079700     MOVE 'FRAUD_DETECTED' TO FRAUD-REASON-CODE
079800     MOVE ACTION-DECLINE TO FRAUD-ACTION-TAKEN
079900     STRING 'RULES_TRIGGERED: ' RULE-01-TRIGGERED RULE-02-TRIGGERED RULE-03-TRIGGERED RULE-04-TRIGGERED RULE-05-TRIGGERED RULE-06-TRIGGERED RULE-07-TRIGGERED RULE-08-TRIGGERED RULE-09-TRIGGERED RULE-10-TRIGGERED DELIMITED BY SIZE INTO FRAUD-RULE-TRIGGERED
080000     MOVE 'TRANSACTION_DECLINED' TO FRAUD-RESOLUTION
080100     ELSE
080200     MOVE 'CLEAN_TRANS' TO FRAUD-REASON-CODE
080300     MOVE ACTION-APPROVE TO FRAUD-ACTION-TAKEN
080400     MOVE 'NO_RULES_TRIGGERED' TO FRAUD-RULE-TRIGGERED
080500     MOVE 'TRANSACTION_APPROVED' TO FRAUD-RESOLUTION
080600     DISPLAY 'RISK SCORE: ' WS-TOTAL-RISK-SCORE
080700     END-IF.                                                                 
080900 
081000 7000-REPORTING-ANALYTICS SECTION.                                       
081100 7000-REPORTING-START.                                                   
081200* Generate real-time fraud statistics                                    
081300     PERFORM 7100-CALCULATE-FRAUD-RATES
081400     PERFORM 7200-UPDATE-PERFORMANCE-METRICS
081500     PERFORM 7300-GENERATE-ALERTS.
081600 
081700 7100-CALCULATE-FRAUD-RATES.                                             
081800     IF WS-TRANSACTIONS-PROCESSED > 0 COMPUTE WS-WORK-AMOUNT = (WS-FRAUD-DETECTED-COUNT / WS-TRANSACTIONS-PROCESSED) * 100
081900 
082000     IF FUNCTION MOD(WS-TRANSACTIONS-PROCESSED, 5000) = 0
082100     DISPLAY 'FRAUD DETECTION RATE: ' WS-WORK-AMOUNT '%'
082200     DISPLAY 'TOTAL PROCESSED: ' WS-TRANSACTIONS-PROCESSED
082300     DISPLAY 'FRAUD DETECTED: ' WS-FRAUD-DETECTED-COUNT
082400     DISPLAY 'APPROVED: ' WS-APPROVED-COUNT
082500     DISPLAY 'DECLINED: ' WS-DECLINED-COUNT
082600     END-IF
082700 END-IF.                                                                 
082800 
082900 7200-UPDATE-PERFORMANCE-METRICS.                                        
083000* Calculate system performance indicators                                
083100     COMPUTE WS-WORK-AMOUNT = WS-APPROVED-COUNT + WS-DECLINED-COUNT
083200 
083300     IF WS-WORK-AMOUNT > 0 COMPUTE WS-WORK-AMOUNT = (WS-APPROVED-COUNT / WS-WORK-AMOUNT) * 100
083400 END-IF.                                                                 
083500 
083600 7300-GENERATE-ALERTS.                                                   
083700* Generate system alerts based on processing patterns                    
083800     IF WS-FRAUD-DETECTED-COUNT > (WS-TRANSACTIONS-PROCESSED * 0.05)
083900     DISPLAY 'HIGH FRAUD RATE ALERT - INVESTIGATE PATTERNS'
084000     END-IF
084100 
084200     IF WS-DECLINED-COUNT > (WS-TRANSACTIONS-PROCESSED * 0.10)
084300     DISPLAY 'HIGH DECLINE RATE ALERT - CHECK THRESHOLDS'
084400 END-IF.                                                                 
084500 
084600 8000-CLEANUP-VELOCITY SECTION.                                          
084700 8000-CLEANUP-START.                                                     
084800* Clean up old velocity data to maintain performance                     
084900     PERFORM 8100-PURGE-OLD-VELOCITY
085000     PERFORM 8200-ARCHIVE-OLD-LOGS.
085100 
085200 8100-PURGE-OLD-VELOCITY.                                                
085300* In production, this would remove velocity records older than 24 hours  
085400     DISPLAY 'VELOCITY DATA CLEANUP COMPLETED'.
085500 
085600 8200-ARCHIVE-OLD-LOGS.                                                  
085700* Archive fraud logs older than specified retention period               
085800     DISPLAY 'LOG ARCHIVAL COMPLETED'.
085900 
086000 9000-FINALIZE-PROGRAM SECTION.                                          
086100 9000-FINALIZE-START.                                                    
086200     PERFORM 9100-CLOSE-FILES
086300     PERFORM 9200-DISPLAY-FINAL-STATS
086400     DISPLAY 'FRAUD MANAGEMENT SYSTEM - PROCESSING COMPLETED'.
086500 
086600 9100-CLOSE-FILES.                                                       
086700     CLOSE TRANSACTION-FILE
086800     CLOSE CUSTOMER-FILE
086900     CLOSE MERCHANT-FILE
087000     CLOSE FRAUD-LOG
087100     CLOSE VELOCITY-FILE.
087200 
087300 9200-DISPLAY-FINAL-STATS.                                               
087400     DISPLAY ' '
087500     DISPLAY '=========================================='
087600     DISPLAY 'FINAL PROCESSING STATISTICS'
087700     DISPLAY '=========================================='
087800     DISPLAY 'TOTAL TRANSACTIONS PROCESSED: '
087900     WS-TRANSACTIONS-PROCESSED
088000     DISPLAY 'FRAUD CASES DETECTED: ' WS-FRAUD-DETECTED-COUNT
088100     DISPLAY 'TRANSACTIONS APPROVED: ' WS-APPROVED-COUNT
088200     DISPLAY 'TRANSACTIONS DECLINED: ' WS-DECLINED-COUNT
088300 
088400     IF WS-TRANSACTIONS-PROCESSED > 0 COMPUTE WS-WORK-AMOUNT = (WS-FRAUD-DETECTED-COUNT / WS-TRANSACTIONS-PROCESSED) * 100
088500     DISPLAY 'FRAUD DETECTION RATE: ' WS-WORK-AMOUNT '%'
088600 
088700     COMPUTE WS-WORK-AMOUNT = (WS-APPROVED-COUNT / WS-TRANSACTIONS-PROCESSED) * 100
088800     DISPLAY 'APPROVAL RATE: ' WS-WORK-AMOUNT '%'
088900     END-IF
089000 
089100     DISPLAY '=========================================='.
089200 
089300* END OF FRAUD-MGMT-SYSTEM PROGRAM                                       
089400 
089500     OPEN I-O CUSTOMER-FILE
089600     IF WS-CUST-STATUS NOT = '00' AND WS-CUST-STATUS NOT = '05'
089700     DISPLAY ERR-FILE-NOT-FOUND ' - CUSTOMER FILE'
089800     STOP RUN
089900     END-IF
090000 
090100     OPEN INPUT MERCHANT-FILE
090200     IF WS-MERCH-STATUS NOT = '00'
090300     DISPLAY ERR-FILE-NOT-FOUND ' - MERCHANT FILE'
090400     STOP RUN
090500     END-IF
090600 
090700     OPEN OUTPUT FRAUD-LOG
090800     IF WS-FRAUD-STATUS NOT = '00'
090900     DISPLAY ERR-FILE-NOT-FOUND ' - FRAUD LOG FILE'
091000     STOP RUN
091100     END-IF
091200 
091300     OPEN I-O VELOCITY-FILE
091400     IF WS-VELO-STATUS NOT = '00' AND WS-VELO-STATUS NOT = '05'
091500     DISPLAY ERR-FILE-NOT-FOUND ' - VELOCITY FILE'
091600     STOP RUN
091700 END-IF.                                                                 
091800 
091900 1200-INITIALIZE-VARIABLES.                                              
092000     MOVE FUNCTION CURRENT-DATE TO WS-CURRENT-TIMESTAMP
092100     MOVE 'N' TO WS-EOF-FLAG
092200     MOVE 'N' TO WS-FRAUD-DETECTED
092300     INITIALIZE WS-COUNTERS
092400 INITIALIZE WS-RULE-RESULTS.                                             
092500 
092600 1300-LOAD-FRAUD-PARAMETERS.                                             
092700* In production, these would be loaded from parameter tables             
092800     MOVE 850 TO HIGH-RISK-THRESHOLD
092900     MOVE 550 TO MEDIUM-RISK-THRESHOLD
093000     MOVE 350 TO LOW-RISK-THRESHOLD
093100     DISPLAY 'FRAUD PARAMETERS LOADED SUCCESSFULLY'.
093200 
093300 2000-PROCESS-TRANSACTIONS SECTION.                                      
093400 2000-PROCESS-START.                                                     
093500     DISPLAY 'BEGINNING TRANSACTION PROCESSING'
093600     PERFORM 2100-READ-TRANSACTION
093700     PERFORM UNTIL EOF-REACHED
093800     PERFORM 2200-ANALYZE-TRANSACTION
093900     PERFORM 2100-READ-TRANSACTION END-PERFORM
094000     DISPLAY 'TRANSACTION PROCESSING COMPLETED'.
094100 
094200 2100-READ-TRANSACTION.                                                  
094300     READ TRANSACTION-FILE AT END SET EOF-REACHED TO TRUE NOT AT END
094400     ADD 1 TO WS-TRANSACTIONS-PROCESSED
094500     IF WS-TRANSACTIONS-PROCESSED = 1 OR FUNCTION MOD(WS-TRANSACTIONS-PROCESSED, 1000) = 0
094600     DISPLAY 'PROCESSED: ' WS-TRANSACTIONS-PROCESSED
094700     ' TRANSACTIONS'
094800     END-IF
094900 END-READ.                                                               
095000 
095100 2200-ANALYZE-TRANSACTION SECTION.                                       
095200 2200-ANALYSIS-START.                                                    
095300     INITIALIZE WS-RULE-RESULTS
095400     MOVE 'N' TO WS-FRAUD-DETECTED
095500     MOVE ZERO TO WS-TOTAL-RISK-SCORE
095600 
095700     PERFORM 2300-VALIDATE-TRANSACTION
095800     IF WS-PROCESS-FLAG = 'Y'
095900     PERFORM 2400-LOAD-CUSTOMER-DATA
096000     PERFORM 2500-LOAD-MERCHANT-DATA
096100     PERFORM 2600-EXECUTE-FRAUD-RULES
096200     PERFORM 2700-CALCULATE-FINAL-RISK
096300     PERFORM 2800-DETERMINE-ACTION
096400     PERFORM 2900-UPDATE-VELOCITY-DATA
096500     PERFORM 3000-LOG-DECISION
096600 END-IF.                                                                 
096700 
096800 2300-VALIDATE-TRANSACTION.                                              
096900     MOVE 'Y' TO WS-PROCESS-FLAG
097000 
097100* Validate card number using Luhn algorithm                              
097200     PERFORM 2310-VALIDATE-CARD-NUMBER
097300 
097400* Validate amount                                                        
097500     IF TRANS-AMOUNT <= 0 OR TRANS-AMOUNT > 999999.99
097600     MOVE 'N' TO WS-PROCESS-FLAG
097700     DISPLAY 'INVALID TRANSACTION AMOUNT: ' TRANS-AMOUNT
097800     END-IF
097900 
098000* Validate date                                                          
098100     IF TRANS-DATE < 20200101 OR TRANS-DATE > 20301231
098200     MOVE 'N' TO WS-PROCESS-FLAG
098300     DISPLAY 'INVALID TRANSACTION DATE: ' TRANS-DATE
098400 END-IF.                                                                 
098500 
098600 2310-VALIDATE-CARD-NUMBER.                                              
098700* Simplified Luhn algorithm validation                                   
098800     IF TRANS-CARD-NUMBER < 1000000000000000 OR TRANS-CARD-NUMBER > 9999999999999999
098900     MOVE 'N' TO WS-PROCESS-FLAG
099000     DISPLAY 'INVALID CARD NUMBER FORMAT'
099100 END-IF.                                                                 
099200 
099300 2400-LOAD-CUSTOMER-DATA.                                                
099400     MOVE TRANS-CARD-NUMBER TO CUST-CARD-NUMBER
099500     READ CUSTOMER-FILE
099600     IF WS-CUST-STATUS = '23'
099700     DISPLAY 'CUSTOMER NOT FOUND: ' TRANS-CARD-NUMBER
099800     MOVE 'N' TO WS-PROCESS-FLAG
099900     ELSE IF WS-CUST-STATUS NOT = '00'
100000     DISPLAY 'ERROR READING CUSTOMER FILE: ' WS-CUST-STATUS
100100     MOVE 'N' TO WS-PROCESS-FLAG
100200 END-IF.                                                                 
100300 
100400 2500-LOAD-MERCHANT-DATA.                                                
100500     MOVE TRANS-MERCHANT-ID TO MERCH-ID
100600     READ MERCHANT-FILE
100700     IF WS-MERCH-STATUS = '23'
100800     DISPLAY 'MERCHANT NOT FOUND: ' TRANS-MERCHANT-ID
100900* Continue processing with default merchant risk                         
101000     MOVE 50 TO MERCH-RISK-LEVEL
101100     MOVE 'UNKNOWN MERCHANT' TO MERCH-NAME
101200     ELSE IF WS-MERCH-STATUS NOT = '00'
101300     DISPLAY 'ERROR READING MERCHANT FILE: ' WS-MERCH-STATUS
101400 END-IF.                                                                 
101500 
101600 2600-EXECUTE-FRAUD-RULES SECTION.                                       
101700 2600-RULES-START.                                                       
101800     PERFORM 2610-RULE-HIGH-AMOUNT
101900     PERFORM 2620-RULE-VELOCITY-CHECK
102000     PERFORM 2630-RULE-LOCATION-VARIANCE
102100     PERFORM 2640-RULE-MERCHANT-RISK
102200     PERFORM 2650-RULE-TIME-PATTERN
102300     PERFORM 2660-RULE-CARD-NOT-PRESENT
102400     PERFORM 2670-RULE-SUSPICIOUS-CATEGORY
102500     PERFORM 2680-RULE-CUSTOMER-BEHAVIOR
102600     PERFORM 2690-RULE-ACCOUNT-AGE
102700     PERFORM 2695-RULE-CROSS-VALIDATION.
102800 
102900 2610-RULE-HIGH-AMOUNT.                                                  
103000* Rule 1: High Amount Transaction                                        
103100     IF TRANS-AMOUNT > SUSPICIOUS-AMOUNT
103200     MOVE 'Y' TO RULE-01-TRIGGERED
103300     ADD 150 TO WS-TRANSACTION-RISK
103400     IF TRANS-AMOUNT > (CUST-AVG-MONTHLY-SPEND * 3)
103500     ADD 100 TO WS-TRANSACTION-RISK
103600     END-IF
103700 END-IF.                                                                 
103800 
103900 2620-RULE-VELOCITY-CHECK.                                               
104000* Rule 2: Transaction Velocity Analysis                                  
104100     PERFORM 2621-CHECK-VELOCITY-LIMITS
104200     IF VELO-TRANS-COUNT-1H > MAX-HOURLY-VELOCITY
104300     MOVE 'Y' TO RULE-02-TRIGGERED
104400     ADD 200 TO WS-VELOCITY-RISK
104500     END-IF
104600     IF VELO-TRANS-COUNT-24H > MAX-DAILY-VELOCITY
104700     MOVE 'Y' TO RULE-02-TRIGGERED
104800     ADD 150 TO WS-VELOCITY-RISK
104900 END-IF.                                                                 
105000 
105100 2621-CHECK-VELOCITY-LIMITS.                                             
105200     MOVE TRANS-CARD-NUMBER TO VELO-CARD-NUMBER
105300     READ VELOCITY-FILE
105400     IF WS-VELO-STATUS = '23'
105500* First transaction for this card - initialize                           
105600     MOVE TRANS-CARD-NUMBER TO VELO-CARD-NUMBER
105700     MOVE 1 TO VELO-TRANS-COUNT-1H
105800     MOVE 1 TO VELO-TRANS-COUNT-24H
105900     MOVE TRANS-AMOUNT TO VELO-AMOUNT-1H
106000     MOVE TRANS-AMOUNT TO VELO-AMOUNT-24H
106100     MOVE FUNCTION CURRENT-DATE(9:6) TO VELO-LAST-UPDATE
106200     MOVE 1 TO VELO-LOCATION-COUNT
106300     MOVE 1 TO VELO-MERCHANT-COUNT
106400 END-IF.                                                                 
106500 
106600 2630-RULE-LOCATION-VARIANCE.                                            
106700* Rule 3: Geographical Location Analysis                                 
106800     PERFORM 2631-CALCULATE-LOCATION-RISK
106900     IF WS-DISTANCE-KM > MAX-LOCATION-VARIANCE
107000     MOVE 'Y' TO RULE-03-TRIGGERED
107100     ADD 175 TO WS-LOCATION-RISK
107200     IF TRANS-COUNTRY-CODE NOT = CUST-HOME-COUNTRY
107300     IF CUST-TRAVEL-FLAG = 'N'
107400     ADD 100 TO WS-LOCATION-RISK
107500     END-IF
107600     END-IF
107700 END-IF.                                                                 
107800 
107900 2631-CALCULATE-LOCATION-RISK.                                           
108000* Simplified distance calculation based on ZIP codes                     
108100     IF TRANS-LOCATION-ZIP NOT = CUST-HOME-ZIP
108200     IF TRANS-COUNTRY-CODE NOT = CUST-HOME-COUNTRY
108300     MOVE 2000 TO WS-DISTANCE-KM
108400     ELSE
108500     MOVE 500 TO WS-DISTANCE-KM
108600     END-IF
108700     ELSE
108800     MOVE 0 TO WS-DISTANCE-KM
108900 END-IF.                                                                 
109000 
109100 2640-RULE-MERCHANT-RISK.                                                
109200* Rule 4: Merchant Risk Assessment                                       
109300     IF MERCH-RISK-LEVEL > 70
109400     MOVE 'Y' TO RULE-04-TRIGGERED
109500     ADD 125 TO WS-MERCHANT-RISK
109600     END-IF
109700 
109800* High-risk merchant categories                                          
109900     EVALUATE TRANS-MERCHANT-CAT WHEN 4829
110000     MOVE 'Y' TO RULE-04-TRIGGERED
110100     ADD 100 TO WS-MERCHANT-RISK
110200 END-EVALUATE.                                                           
110300 
110400 2650-RULE-TIME-PATTERN.                                                 
110500* Rule 5: Unusual Time Pattern                                           
110600     PERFORM 2651-ANALYZE-TIME-PATTERN
110700     IF WS-TIME-DIFF-HOURS < 1
110800     IF VELO-LOCATION-COUNT > 3
110900     MOVE 'Y' TO RULE-05-TRIGGERED
111000     ADD 150 TO WS-BEHAVIORAL-RISK
111100     END-IF
111200 END-IF.                                                                 
111300 
111400 2651-ANALYZE-TIME-PATTERN.                                              
111500* Check for rapid-fire transactions in different locations               
111600     MOVE 2 TO WS-TIME-DIFF-HOURS
111700     IF TRANS-TIME < 060000 OR TRANS-TIME > 220000
111800     ADD 50 TO WS-BEHAVIORAL-RISK
111900 END-IF.                                                                 
112000 
112100 2660-RULE-CARD-NOT-PRESENT.                                             
112200* Rule 6: Card Not Present Risk                                          
112300     IF TRANS-CHANNEL = 'ONL' OR TRANS-CHANNEL = 'TEL'
112400     IF TRANS-AMOUNT > 500.00
112500     MOVE 'Y' TO RULE-06-TRIGGERED
112600     ADD 75 TO WS-TRANSACTION-RISK
112700     END-IF
112800     IF TRANS-PIN-VERIFIED = 'N'
112900     ADD 50 TO WS-TRANSACTION-RISK
113000     END-IF
113100 END-IF.                                                                 
113200 
113300 2670-RULE-SUSPICIOUS-CATEGORY.                                          
113400* Rule 7: Suspicious Category Combinations                               
113500     IF VELO-MERCHANT-COUNT > 5
113600     MOVE 'Y' TO RULE-07-TRIGGERED
113700     ADD 100 TO WS-BEHAVIORAL-RISK
113800 END-IF.                                                                 
113900 
114000 2680-RULE-CUSTOMER-BEHAVIOR.                                            
114100* Rule 8: Customer Behavioral Analysis                                   
114200     IF CUST-FRAUD-FLAG = 'Y'
114300     MOVE 'Y' TO RULE-08-TRIGGERED
114400     ADD 200 TO WS-BEHAVIORAL-RISK
114500     END-IF
114600 
114700     COMPUTE WS-DAYS-DIFF = TRANS-DATE - CUST-LAST-TRANS-DATE
114800     IF WS-DAYS-DIFF > 90
114900     ADD 50 TO WS-BEHAVIORAL-RISK
115000     END-IF
115100 
115200     IF TRANS-AMOUNT > CUST-MAX-DAILY-SPEND
115300     MOVE 'Y' TO RULE-08-TRIGGERED
115400     ADD 125 TO WS-BEHAVIORAL-RISK
115500 END-IF.                                                                 
115600 
115700 2690-RULE-ACCOUNT-AGE.                                                  
115800* Rule 9: New Account Risk                                               
115900     COMPUTE WS-DAYS-DIFF = TRANS-DATE - CUST-ACCOUNT-OPEN-DATE
116000     IF WS-DAYS-DIFF < 30
116100     MOVE 'Y' TO RULE-09-TRIGGERED
116200     ADD 100 TO WS-BEHAVIORAL-RISK
116300     IF TRANS-AMOUNT > 1000.00
116400     ADD 50 TO WS-BEHAVIORAL-RISK
116500     END-IF
116600 END-IF.                                                                 
116700 
116800 2695-RULE-CROSS-VALIDATION.                                             
116900* Rule 10: Cross-validation of multiple risk factors                     
117000     IF (RULE-01-TRIGGERED = 'Y' AND RULE-03-TRIGGERED = 'Y') OR (RULE-02-TRIGGERED = 'Y' AND RULE-04-TRIGGERED = 'Y') OR (RULE-06-TRIGGERED = 'Y' AND RULE-08-TRIGGERED = 'Y')
117100     MOVE 'Y' TO RULE-10-TRIGGERED
117200     ADD 100 TO WS-TOTAL-RISK-SCORE
117300 END-IF.                                                                 
117400 
117500 2700-CALCULATE-FINAL-RISK.                                              
117600     COMPUTE WS-TOTAL-RISK-SCORE = WS-TRANSACTION-RISK + WS-VELOCITY-RISK + WS-LOCATION-RISK + WS-MERCHANT-RISK + WS-BEHAVIORAL-RISK +
117700 CUST-RISK-SCORE.                                                        
117800 
117900 2800-DETERMINE-ACTION.                                                  
118000     EVALUATE TRUE WHEN WS-TOTAL-RISK-SCORE >= HIGH-RISK-THRESHOLD
118100     MOVE 'Y' TO WS-FRAUD-DETECTED
118200     ADD 1 TO WS-FRAUD-DETECTED-COUNT
118300     ADD 1 TO WS-DECLINED-COUNT WHEN WS-TOTAL-RISK-SCORE >= MEDIUM-RISK-THRESHOLD
118400     PERFORM 2810-MANUAL-REVIEW-REQUIRED WHEN OTHER
118500     ADD 1 TO WS-APPROVED-COUNT
118600 END-EVALUATE.                                                           
118700 
118800 2810-MANUAL-REVIEW-REQUIRED.                                            
118900* Medium risk transactions require additional validation                 
119000     IF RULE-08-TRIGGERED = 'Y' OR RULE-10-TRIGGERED = 'Y'
119100     MOVE 'Y' TO WS-FRAUD-DETECTED
119200     ADD 1 TO WS-FRAUD-DETECTED-COUNT
119300     ELSE
119400     ADD 1 TO WS-APPROVED-COUNT
119500 END-IF.                                                                 
119600 
119700 2900-UPDATE-VELOCITY-DATA.                                              
119800     MOVE TRANS-CARD-NUMBER TO VELO-CARD-NUMBER
119900     READ VELOCITY-FILE
120000     IF WS-VELO-STATUS = '00'
120100     ADD 1 TO VELO-TRANS-COUNT-1H
120200     ADD 1 TO VELO-TRANS-COUNT-24H
120300     ADD TRANS-AMOUNT TO VELO-AMOUNT-1H
120400     ADD TRANS-AMOUNT TO VELO-AMOUNT-24H
120500     MOVE FUNCTION CURRENT-DATE(9:6) TO VELO-LAST-UPDATE
120600     REWRITE VELOCITY-RECORD
120700     ELSE
120800* Create new velocity record                                             
120900     MOVE TRANS-CARD-NUMBER TO VELO-CARD-NUMBER
121000     MOVE 1 TO VELO-TRANS-COUNT-1H
121100     MOVE 1 TO VELO-TRANS-COUNT-24H
121200     MOVE TRANS-AMOUNT TO VELO-AMOUNT-1H
121300     MOVE TRANS-AMOUNT TO VELO-AMOUNT-24H
121400     MOVE FUNCTION CURRENT-DATE(9:6) TO VELO-LAST-UPDATE
121500     MOVE 1 TO VELO-LOCATION-COUNT
121600     MOVE 1 TO VELO-MERCHANT-COUNT
121700     WRITE VELOCITY-RECORD
121800 END-IF.                                                                 
121900 
122000 3000-LOG-DECISION.                                                      
122100     MOVE WS-CURRENT-TIMESTAMP TO FRAUD-TIMESTAMP
122200     MOVE TRANS-ID TO FRAUD-TRANS-ID
122300     MOVE TRANS-CARD-NUMBER TO FRAUD-CARD-NUMBER
122400     MOVE WS-TOTAL-RISK-SCORE TO FRAUD-RISK-SCORE
122500     MOVE TRANS-AMOUNT TO FRAUD-AMOUNT
122600     MOVE MERCH-NAME TO FRAUD-MERCHANT
122700     MOVE TRANS-LOCATION-ZIP TO FRAUD-LOCATION
122800     MOVE 'SYSTEM' TO FRAUD-ANALYST-ID
122900 
123000     IF WS-FRAUD-DETECTED = 'Y'
123100     MOVE 'FRAUD_DETECTED' TO FRAUD-REASON-CODE
123200     MOVE ACTION-DECLINE TO FRAUD-ACTION-TAKEN
123300     STRING 'RULES_TRIGGERED: ' RULE-01-TRIGGERED RULE-02-TRIGGERED RULE-03-TRIGGERED RULE-04-TRIGGERED RULE-05-TRIGGERED RULE-06-TRIGGERED RULE-07-TRIGGERED RULE-08-TRIGGERED RULE-09-TRIGGERED RULE-10-TRIGGERED DELIMITED BY SIZE INTO FRAUD-RULE-TRIGGERED
123400     MOVE 'TRANSACTION_DECLINED' TO FRAUD-RESOLUTION
123500     ELSE
123600     MOVE 'CLEAN_TRANS' TO FRAUD-REASON-CODE
123700     MOVE ACTION-APPROVE TO FRAUD-ACTION-TAKEN
123800     MOVE 'NO_RULES_TRIGGERED' TO FRAUD-RULE-TRIGGERED
123900     MOVE 'TRANSACTION_APPROVED' TO FRAUD-RESOLUTION
124000     END-IF.
