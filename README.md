# Docker

Since i am using reverse proxy, i do not need to use "ports" or "expose" in my docker compose files.

The variable "container_name" is important for this way of working with Docker. I give the container name (Forward Hostname), the container standard port (Forward Port) and my Domain name in my "Proxy Host" configuration and its all set.

# Networks
I use 2 differents "networks" in my system:

1. Frontend: Conection between Cloudflared and my reverse proxy.    

2. Backend: Conection between my reverse proxy and my applications.

- In this way i dont have to open many "Doors" in my server, everything will be pointed to my reverse proxy, and if everything is well set he can do his job.

 