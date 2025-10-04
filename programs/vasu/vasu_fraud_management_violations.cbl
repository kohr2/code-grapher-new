000100 IDENTIFICATION DIVISION.                                                
000200 PROGRAM-ID. FRAUD-MGMT-SYSTEM-VIOLATIONS.                               
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
005400 05  TRANS-MERCHANT-ID       PIC 9(8).                                   
005500 05  TRANS-LOCATION          PIC X(20).                                  
005600 05  TRANS-TYPE              PIC X(10).                                  
005700 05  TRANS-APPROVAL-CODE     PIC X(10).                                  
005800 05  TRANS-FILLER            PIC X(120).                                 
005900 
006000 FD  CUSTOMER-FILE                                                       
006100     RECORDING MODE IS F
006200 RECORD CONTAINS 300 CHARACTERS.                                         
006300 01  CUSTOMER-RECORD.                                                    
006400 05  CUST-CARD-NUMBER        PIC 9(16).                                  
006500 05  CUST-NAME               PIC X(30).                                  
006600 05  CUST-ADDRESS            PIC X(50).                                  
006700 05  CUST-PHONE              PIC X(15).                                  
006800 05  CUST-EMAIL              PIC X(40).                                  
006900 05  CUST-CREDIT-LIMIT       PIC 9(8)V99.                               
007000 05  CUST-AVAILABLE-CREDIT   PIC 9(8)V99.                               
007100 05  CUST-LAST-TRANS-DATE    PIC 9(8).                                  
007200 05  CUST-AVG-MONTHLY-SPEND  PIC 9(8)V99.                               
007300 05  CUST-FRAUD-FLAG         PIC X.                                      
007400 05  CUST-RISK-SCORE         PIC 9(3).                                   
007500 05  CUST-FILLER             PIC X(100).                                 
007600 
007700 FD  MERCHANT-FILE                                                       
007800     RECORDING MODE IS F
007900 RECORD CONTAINS 200 CHARACTERS.                                         
008000 01  MERCHANT-RECORD.                                                    
008100 05  MERCH-ID                PIC 9(8).                                   
008200 05  MERCH-NAME              PIC X(30).                                  
008300 05  MERCH-CATEGORY          PIC X(20).                                  
008400 05  MERCH-RISK-LEVEL        PIC 9(1).                                   
008500 05  MERCH-LOCATION          PIC X(30).                                  
008600 05  MERCH-FILLER            PIC X(100).                                 
008700 
008800 FD  FRAUD-LOG                                                           
008900     RECORDING MODE IS F
009000 RECORD CONTAINS 400 CHARACTERS.                                         
009100 01  FRAUD-LOG-RECORD.                                                   
009200 05  LOG-TRANS-ID            PIC 9(12).                                  
009300 05  LOG-CARD-NUMBER         PIC 9(16).                                  
009400 05  LOG-RISK-SCORE          PIC 9(4).                                   
009500 05  LOG-DECISION            PIC X(10).                                  
009600 05  LOG-TIMESTAMP           PIC 9(14).                                  
009700 05  LOG-RULES-TRIGGERED     PIC X(50).                                  
009800 05  LOG-FILLER              PIC X(300).                                 
009900 
010000 FD  VELOCITY-FILE                                                       
010100     RECORDING MODE IS F
010200 RECORD CONTAINS 100 CHARACTERS.                                         
010200 01  VELOCITY-RECORD.                                                    
010300 05  VELO-CARD-NUMBER        PIC 9(16).                                  
010400 05  VELO-TRANS-COUNT        PIC 9(3).                                   
010500 05  VELO-TOTAL-AMOUNT       PIC 9(8)V99.                                
010600 05  VELO-LAST-TRANS-DATE    PIC 9(8).                                  
010700 05  VELO-FILLER             PIC X(50).                                  
010800 
010900 WORKING-STORAGE SECTION.                                                
011000 
011100* File status variables                                                   
011200 01  WS-TRANS-STATUS         PIC XX.                                     
011300 01  WS-CUST-STATUS          PIC XX.                                     
011400 01  WS-MERCH-STATUS         PIC XX.                                     
011500 01  WS-FRAUD-STATUS         PIC XX.                                     
011600 01  WS-VELO-STATUS          PIC XX.                                     
011700 
011800* Constants                                                                
011900 01  HIGH-RISK-THRESHOLD     PIC 9(3) VALUE 800.                         
012000 01  MEDIUM-RISK-THRESHOLD   PIC 9(3) VALUE 600.                         
012100 01  LOW-RISK-THRESHOLD      PIC 9(3) VALUE 400.                         
012200 01  ZERO                    PIC 9(1) VALUE 0.                           
012300 
012400* Working variables                                                        
012500 01  WS-WORK-AMOUNT          PIC 9(8)V99.                                
012600 01  WS-TOTAL-RISK-SCORE     PIC 9(4) VALUE ZERO.                        
012700 01  WS-TRANSACTION-RISK     PIC 9(3) VALUE ZERO.                        
012800 01  WS-VELOCITY-RISK        PIC 9(3) VALUE ZERO.                        
012900 01  WS-LOCATION-RISK        PIC 9(3) VALUE ZERO.                        
013000 01  WS-MERCHANT-RISK        PIC 9(3) VALUE ZERO.                        
013100 01  WS-BEHAVIORAL-RISK      PIC 9(3) VALUE ZERO.                        
013200 01  WS-FRAUD-DETECTED       PIC X VALUE 'N'.                            
013300 01  WS-DECLINED-COUNT       PIC 9(5) VALUE ZERO.                        
013400 01  WS-APPROVED-COUNT       PIC 9(5) VALUE ZERO.                        
013500 01  WS-FRAUD-RULE-TRIGGERED PIC X(50).                                  
013600 01  WS-FRAUD-RISK-SCORE    PIC 9(4).                                    
013700 
013800* Rule trigger flags                                                       
013900 01  WS-RULE-FLAGS.                                                      
014000 05  RULE-01-TRIGGERED       PIC X VALUE 'N'.                            
014100 05  RULE-02-TRIGGERED       PIC X VALUE 'N'.                            
014200 05  RULE-03-TRIGGERED       PIC X VALUE 'N'.                            
014300 05  RULE-04-TRIGGERED       PIC X VALUE 'N'.                            
014400 05  RULE-05-TRIGGERED       PIC X VALUE 'N'.                            
014500 05  RULE-06-TRIGGERED       PIC X VALUE 'N'.                            
014600 05  RULE-07-TRIGGERED       PIC X VALUE 'N'.                            
014700 05  RULE-08-TRIGGERED       PIC X VALUE 'N'.                            
014800 05  RULE-09-TRIGGERED       PIC X VALUE 'N'.                            
014900 05  RULE-10-TRIGGERED       PIC X VALUE 'N'.                            
015000 
015100 PROCEDURE DIVISION.                                                     
015200 
015300 1000-MAIN-PROCESSING SECTION.                                            
015400 1000-MAIN-START.                                                         
015500     DISPLAY 'FRAUD MANAGEMENT SYSTEM - VIOLATION VERSION'                
015600     DISPLAY '==========================================='                
015700     
015800     PERFORM 2000-INITIALIZE-SYSTEM
015900     PERFORM 3000-PROCESS-TRANSACTIONS UNTIL WS-TRANS-STATUS = '10'
016000     PERFORM 4000-FINALIZE-SYSTEM
016100     
016200     DISPLAY 'PROCESSING COMPLETE'                                        
016300     DISPLAY 'DECLINED TRANSACTIONS: ' WS-DECLINED-COUNT                  
016400     DISPLAY 'APPROVED TRANSACTIONS: ' WS-APPROVED-COUNT                  
016500     
016600     STOP RUN.                                                            
016700 
016800 2000-INITIALIZE-SYSTEM SECTION.                                         
016900 2000-INIT-START.                                                         
017000     OPEN INPUT TRANSACTION-FILE
017100     OPEN I-O CUSTOMER-FILE
017200     OPEN I-O MERCHANT-FILE
017300     OPEN OUTPUT FRAUD-LOG
017400     OPEN I-O VELOCITY-FILE
017500     
017600     READ TRANSACTION-FILE
017700     END-READ.                                                            
017800 
017900 3000-PROCESS-TRANSACTIONS SECTION.                                      
018000 3000-PROCESS-START.                                                      
018100     MOVE ZERO TO WS-TOTAL-RISK-SCORE
018200     
018300* VIOLATION 1: Missing proper risk score calculation
018400* Should calculate: WS-TOTAL-RISK-SCORE = WS-TRANSACTION-RISK + WS-VELOCITY-RISK + WS-LOCATION-RISK + WS-MERCHANT-RISK + WS-BEHAVIORAL-RISK
018500* Instead just setting to zero - this is a violation
018600     MOVE ZERO TO WS-TOTAL-RISK-SCORE
018700     
018800     PERFORM 2800-DETERMINE-ACTION
018900     
019000     READ TRANSACTION-FILE
019100     END-READ.                                                            
019200 
019300 2800-DETERMINE-ACTION SECTION.                                           
019400 2800-DETERMINE-START.                                                    
019500     
019600* VIOLATION 2: Missing fraud logging
019700     IF WS-TOTAL-RISK-SCORE >= HIGH-RISK-THRESHOLD
019800     MOVE 'Y' TO WS-FRAUD-DETECTED
019900* Missing: PERFORM 3000-LOG-DECISION
020000     END-IF
020100     
020200* VIOLATION 3: Incomplete rule execution - only executing 2 out of 10 rules
020300     PERFORM 2610-RULE-HIGH-AMOUNT
020400     PERFORM 2620-RULE-VELOCITY-CHECK
020500* Missing: PERFORM 2630-RULE-LOCATION-VARIANCE
020600* Missing: PERFORM 2640-RULE-MERCHANT-RISK
020700* Missing: PERFORM 2650-RULE-BEHAVIORAL-ANALYSIS
020800* Missing: PERFORM 2660-RULE-TIME-PATTERN
020900* Missing: PERFORM 2670-RULE-AMOUNT-PATTERN
021000* Missing: PERFORM 2680-RULE-CROSS-VALIDATION
021100* Missing: PERFORM 2690-RULE-DEVICE-FINGERPRINT
021200* Missing: PERFORM 2695-RULE-CROSS-VALIDATION
021300     
021400     IF WS-FRAUD-DETECTED = 'Y'
021500     ADD 1 TO WS-DECLINED-COUNT
021600     ELSE
021700     ADD 1 TO WS-APPROVED-COUNT
021800     END-IF
021900 
022000 2610-RULE-HIGH-AMOUNT SECTION.                                           
022100 2610-HIGH-AMOUNT-START.                                                  
022200     IF TRANS-AMOUNT > 5000
022300     MOVE 'Y' TO RULE-01-TRIGGERED
022400     ADD 100 TO WS-TOTAL-RISK-SCORE
022500     END-IF
022600 
022700 2620-RULE-VELOCITY-CHECK SECTION.                                        
022800 2620-VELOCITY-START.                                                     
022900     IF VELO-TRANS-COUNT > 10
023000     MOVE 'Y' TO RULE-02-TRIGGERED
023100     ADD 75 TO WS-TOTAL-RISK-SCORE
023200     END-IF
023300 
023400* VIOLATION 4: Missing neural network scoring
023500* Should include: PERFORM 4100-NEURAL-NETWORK-SCORING
023600* This is a critical violation for advanced analytics
023700 
023800* VIOLATION 5: Incomplete pattern detection
023900* Missing: PERFORM 4210-CHECK-ROUND-DOLLAR-PATTERN
024000* Missing: PERFORM 4220-CHECK-ASCENDING-AMOUNT-PATTERN
024100* Missing: PERFORM 4230-CHECK-TEST-TRANSACTION-PATTERN
024200 
024300* VIOLATION 6: Missing biometric analysis
024400* Should include: PERFORM 4310-ANALYZE-TYPING-PATTERNS
024500* Should include: PERFORM 4320-ANALYZE-DEVICE-FINGERPRINT
024600* Should include: PERFORM 4330-ANALYZE-SESSION-BEHAVIOR
024700 
024800 4000-FINALIZE-SYSTEM SECTION.                                            
024900 4000-FINALIZE-START.                                                    
025000     CLOSE TRANSACTION-FILE
025100     CLOSE CUSTOMER-FILE
025200     CLOSE MERCHANT-FILE
025300     CLOSE FRAUD-LOG
025400     CLOSE VELOCITY-FILE
025500     
025600     DISPLAY 'SYSTEM FINALIZED'                                            
025700 
025800 END PROGRAM FRAUD-MGMT-SYSTEM-VIOLATIONS.
