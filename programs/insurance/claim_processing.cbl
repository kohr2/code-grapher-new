      * INSURANCE CLAIM PROCESSING PROGRAM
       IDENTIFICATION DIVISION.
       PROGRAM-ID. CLAIM-PROC.
       AUTHOR. INSURANCE SYSTEM.
       DATE-WRITTEN. 2024-01-01.
       
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       
       01  CLAIM-DATA.
           02  CLAIM-NUMBER         PIC X(10).
           02  CLAIM-AMOUNT         PIC 9(8)V99.
           02  CLAIM-STATUS         PIC X(1).
               88  APPROVED-CLAIM   VALUE 'A'.
               88  DENIED-CLAIM     VALUE 'D'.
               88  PENDING-CLAIM    VALUE 'P'.
       
       01  POLICY-DATA.
           02  POLICY-NUMBER        PIC X(10).
           02  POLICY-LIMIT         PIC 9(8)V99.
           02  DEDUCTIBLE-AMOUNT    PIC 9(8)V99.
       
       01  APPROVAL-DATA.
           02  APPROVAL-REQUIRED    PIC X(1) VALUE 'N'.
               88  NEEDS-APPROVAL   VALUE 'Y'.
               88  AUTO-APPROVED    VALUE 'N'.
           02  APPROVAL-AMOUNT      PIC 9(8)V99 VALUE 5000.
       
       PROCEDURE DIVISION.
       
       MAIN-PROCEDURE.
           PERFORM INITIALIZE-CLAIM
           PERFORM VALIDATE-CLAIM
           PERFORM CHECK-APPROVAL-REQUIRED
           PERFORM PROCESS-CLAIM
           PERFORM FINALIZE-CLAIM
           STOP RUN.
       
       INITIALIZE-CLAIM.
           MOVE 'N' TO APPROVAL-REQUIRED
           DISPLAY 'CLAIM PROCESSING INITIALIZED'.
       
       VALIDATE-CLAIM.
           IF CLAIM-AMOUNT > 0
               DISPLAY 'CLAIM VALIDATION PASSED'
           ELSE
               DISPLAY 'ERROR: INVALID CLAIM AMOUNT'
           END-IF.
       
       CHECK-APPROVAL-REQUIRED.
           IF CLAIM-AMOUNT > APPROVAL-AMOUNT
               MOVE 'Y' TO APPROVAL-REQUIRED
               DISPLAY 'CLAIM REQUIRES APPROVAL'
           ELSE
               DISPLAY 'CLAIM AUTO-APPROVED'
           END-IF.
       
       PROCESS-CLAIM.
           IF NEEDS-APPROVAL
               DISPLAY 'CLAIM PENDING APPROVAL'
               MOVE 'P' TO CLAIM-STATUS
           ELSE
               IF CLAIM-AMOUNT <= POLICY-LIMIT
                   MOVE 'A' TO CLAIM-STATUS
                   DISPLAY 'CLAIM APPROVED'
               ELSE
                   MOVE 'D' TO CLAIM-STATUS
                   DISPLAY 'CLAIM DENIED - EXCEEDS LIMIT'
               END-IF
           END-IF.
       
       FINALIZE-CLAIM.
           DISPLAY 'CLAIM PROCESSING COMPLETED'.
