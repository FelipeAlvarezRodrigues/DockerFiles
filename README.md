# Docker

# Networks
I use 2 differents "networks" in my system:

1. Frontend: Conection between Cloudflared and my reverse proxy.    

2. Backend: Conection between my reverse proxy and my applications.

- In this way i dont have to open many "Doors" in my server, everything will be pointed to my reverse proxy, and if everything is well set he can do his job.

 # Volumes
 Volumes are also important to not lose your data, there are 3 different methods of using "volumes".

 1. Named Volumes:     - my_named_volume:/app/data
 2. Bind Mounts:       - /path/on/host:/app/data
 3. Anonymous Volumes: - /app/data
 These volumes are created and managed by Docker and provide an easy way to persist data beyond the containers lifecycle.

