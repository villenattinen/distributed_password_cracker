# distributed_password_cracker
Distributed Password Cracker

(Unfortunately) This project is built to be run in a Windows environment and assumes that Hashcat is already installed.

Example of a run:
| Client | Server | Workers |
| ------ | ------ | ------ |
| PING -> | | <- JOIN |
| | <- PONG | |
| | ACK -> | |
| JOB -> | | |
| | PING -> | |
| | | <- status (IDLE/BUSY) |
| | PING -> | |
| | | <- status (IDLE/BUSY) |
| | PING -> | |
| | | <- status (IDLE/BUSY) |
| | <- ACK_JOB | |
| | JOB (iteration set 1) -> | |
| | | <- ACK_JOB |
| | JOB (iteration set 2) -> | |
| | | <- ACK_JOB |
| | JOB (iteration set 3) -> | |
| | | <- ACK_JOB |
| PING -> | | |
| | <- PONG | |
| | | <- FAIL (no match found) |
| PING -> | | |
| | <- PONG | |
| | | <- RESULT (hash cracked) |
| | ABORT (end the job of the still running worker) -> | |
| PING -> | | |
| | <- RESULT | |
