# SB-310-pa3

This assignment was an attempt to create a reliable TCP connection over the UDP protocol. There were several design considerations in this project, such as
* Placing MSG queues/buffers between the client and the server so that messages when to the appropriate client, and packets could be retransmitted if necessary.
* Used mutltiple threads for the client side code, mainly one for handling incoming packets from the server and one for sending packets to the server.
* Argument handling, race conditions, and packet parsing were some of the concepts that went into the project.
* The code base was written in Python to abstract some of the lower level details and mainly focus on the TCP reliability.
