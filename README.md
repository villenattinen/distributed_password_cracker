# distributed_password_cracker
Distributed Password Cracker
Course Project for the course Distributed Systems (521290S)

Author: Ville Nättinen

## Main idea
The project consists of a request client, a server, and worker clients. The request client is intended to send a hash to the server, which will then distribute the hash to the worker clients. The worker clients will then try to crack the hash and send the result back to the server. The server will then send the result back to the request client.  

The worker clients don't actually crack hashes, only simulate a password cracker by "working" from random, but short, times.  

## How to run
The repository contains a shell script `start.sh` that can be used to start the server and five worker clients as background processes.  
The request client can the be run manually or by using the `client.sh` script, that contains some example parameters.  

The request client's parameters don't actually matter, but they would have been passed as parameters to Hashcat/John the Ripper.  

## Example of a run:
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
